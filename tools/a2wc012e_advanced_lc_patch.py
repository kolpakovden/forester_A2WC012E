#!/usr/bin/env python3
import argparse
import hashlib
import struct
from pathlib import Path

ROM_SIZE = 524288

# A2WC012E / A2WC0MME verified OEM call pointers / RAM.
H_POLF, S_POLF = 0x1132C, 0x000228C4
H_TIMING, S_TIMING = 0x113D8, 0x00028AF8

# Existing MerpMod / custom Delta-MAP patch ends at 0x6AD43.
FUEL_HOOK = 0x6AD50
FUEL_ORIG = 0x6AD70
LC_ENGAGED_FUEL = 0x6AD74
FUEL_MODE = 0x6AD78
FUEL_TARGET = 0x6AD7C
P_POLF = 0x6AD80

TIMING_HOOK = 0x6AD90
TIMING_ORIG = 0x6ADB0
LC_ENGAGED_TIMING = 0x6ADB4
TIMING_MODE = 0x6ADB8
TIMING_TARGET = 0x6ADBC
P_BASE_TIMING = 0x6ADC0

FREE_START, FREE_END = 0x6AD44, 0x6ADC4
LC_ENGAGED_RAM = 0xFFFFCA3B
POLF_ENRICH_RAM = 0xFFFFB6E8
BASE_TIMING_RAM = 0xFFFFB9F8


def be32(v):
    return int(v).to_bytes(4, 'big')


def emit_words(words):
    return b''.join(int(w).to_bytes(2, 'big') for w in words)


def groups(diffs):
    if not diffs:
        return []
    out = []
    s = p = diffs[0]
    for x in diffs[1:]:
        if x == p + 1:
            p = x
        else:
            out.append((s, p))
            s = p = x
    out.append((s, p))
    return out


def patch(inp: Path, out: Path, report_path: Path):
    original = inp.read_bytes()
    if len(original) != ROM_SIZE:
        raise RuntimeError(f'Expected {ROM_SIZE} bytes, got {len(original)}')

    cal = original[0x2000:0x2008]
    if cal != b'A2WC0MME':
        raise RuntimeError(f'Internal ID @0x2000 is {cal!r}, expected A2WC0MME')

    old_polf = int.from_bytes(original[H_POLF:H_POLF+4], 'big')
    old_timing = int.from_bytes(original[H_TIMING:H_TIMING+4], 'big')
    if old_polf != S_POLF:
        raise RuntimeError(f'POLF pointer @0x{H_POLF:X}=0x{old_polf:08X}, expected 0x{S_POLF:08X}')
    if old_timing != S_TIMING:
        raise RuntimeError(f'Timing pointer @0x{H_TIMING:X}=0x{old_timing:08X}, expected 0x{S_TIMING:08X}')

    occupied = [(i, b) for i, b in enumerate(original[FREE_START:FREE_END], FREE_START) if b != 0xFF]
    if occupied:
        preview = ', '.join(f'0x{i:X}=0x{b:02X}' for i, b in occupied[:32])
        raise RuntimeError(f'Advanced-LC target area 0x{FREE_START:X}-0x{FREE_END-1:X} is not blank. First occupied bytes: {preview}')

    rom = bytearray(original)

    # POLF wrapper: call OEM routine, then optionally override pPolfEnrich when LC is engaged.
    fuel_words = [
        0x4F22, 0xD307, 0x430B, 0x0009,
        0xD106, 0x6010, 0x2008, 0x8905,
        0xD005, 0x2008, 0x8902, 0xD005,
        0xD205, 0x2202, 0x4F26, 0x000B,
    ]
    rom[FUEL_HOOK:FUEL_HOOK+0x20] = emit_words(fuel_words)
    rom[FUEL_ORIG:FUEL_ORIG+4] = be32(S_POLF)
    rom[LC_ENGAGED_FUEL:LC_ENGAGED_FUEL+4] = be32(LC_ENGAGED_RAM)
    rom[FUEL_MODE:FUEL_MODE+4] = b'\x00\x00\x00\x00'  # OFF by default
    fuel_enrichment = 14.7 / 11.0 - 1.0
    rom[FUEL_TARGET:FUEL_TARGET+4] = struct.pack('>f', fuel_enrichment)
    rom[P_POLF:P_POLF+4] = be32(POLF_ENRICH_RAM)

    # Base-timing wrapper: call OEM routine, then optionally override pBaseTiming when LC is engaged.
    timing_words = [
        0x4F22, 0xD307, 0x430B, 0x0009,
        0xD106, 0x6010, 0x2008, 0x8905,
        0xD005, 0x2008, 0x8902, 0xD005,
        0xD205, 0x2202, 0x4F26, 0x000B,
    ]
    rom[TIMING_HOOK:TIMING_HOOK+0x20] = emit_words(timing_words)
    rom[TIMING_ORIG:TIMING_ORIG+4] = be32(S_TIMING)
    rom[LC_ENGAGED_TIMING:LC_ENGAGED_TIMING+4] = be32(LC_ENGAGED_RAM)
    rom[TIMING_MODE:TIMING_MODE+4] = b'\x00\x00\x00\x00'  # OFF by default
    rom[TIMING_TARGET:TIMING_TARGET+4] = struct.pack('>f', 0.0)
    rom[P_BASE_TIMING:P_BASE_TIMING+4] = be32(BASE_TIMING_RAM)

    # Redirect OEM function pointers to our wrappers.
    rom[H_POLF:H_POLF+4] = be32(FUEL_HOOK)
    rom[H_TIMING:H_TIMING+4] = be32(TIMING_HOOK)

    # Hard validation.
    assert int.from_bytes(rom[H_POLF:H_POLF+4], 'big') == FUEL_HOOK
    assert int.from_bytes(rom[H_TIMING:H_TIMING+4], 'big') == TIMING_HOOK
    assert int.from_bytes(rom[FUEL_ORIG:FUEL_ORIG+4], 'big') == S_POLF
    assert int.from_bytes(rom[TIMING_ORIG:TIMING_ORIG+4], 'big') == S_TIMING
    assert int.from_bytes(rom[LC_ENGAGED_FUEL:LC_ENGAGED_FUEL+4], 'big') == LC_ENGAGED_RAM
    assert int.from_bytes(rom[LC_ENGAGED_TIMING:LC_ENGAGED_TIMING+4], 'big') == LC_ENGAGED_RAM
    assert int.from_bytes(rom[P_POLF:P_POLF+4], 'big') == POLF_ENRICH_RAM
    assert int.from_bytes(rom[P_BASE_TIMING:P_BASE_TIMING+4], 'big') == BASE_TIMING_RAM

    # Preserve the existing Delta MAP hook/table block byte-for-byte.
    assert rom[0x6A612:0x6A616] == original[0x6A612:0x6A616]
    assert rom[0x6AC40:0x6AD44] == original[0x6AC40:0x6AD44]

    out.write_bytes(rom)

    diffs = [i for i, (a, b) in enumerate(zip(original, rom)) if a != b]
    sha_in = hashlib.sha256(original).hexdigest()
    sha_out = hashlib.sha256(rom).hexdigest()
    afr = 14.7 / (1.0 + struct.unpack('>f', rom[FUEL_TARGET:FUEL_TARGET+4])[0])
    timing = struct.unpack('>f', rom[TIMING_TARGET:TIMING_TARGET+4])[0]

    report = f'''A2WC012E / A2WC0MME Advanced LC patch report\n\nInput:\n  {inp.name}\n  SHA256 {sha_in}\n\nOutput:\n  {out.name}\n  SHA256 {sha_out}\n\nValidation:\n  ROM size: {len(rom)}\n  Internal ID: {rom[0x2000:0x2008].decode(errors="replace")}\n  Existing Delta MAP hook preserved: YES\n  Existing Delta MAP block 0x6AC40-0x6AD43 preserved byte-for-byte: YES\n  POLF OEM pointer verified: 0x{S_POLF:08X}\n  Base Timing OEM pointer verified: 0x{S_TIMING:08X}\n  Advanced-LC target ROM area was blank before patch: YES\n\nNew hooks:\n  0x{H_POLF:06X}: 0x{S_POLF:08X} -> 0x{FUEL_HOOK:08X}\n  0x{H_TIMING:06X}: 0x{S_TIMING:08X} -> 0x{TIMING_HOOK:08X}\n\nNew calibrations:\n  0x{FUEL_MODE:06X} Fuel Mode = 0 (OFF)\n  0x{FUEL_TARGET:06X} Fuel Target preset = {afr:.2f} estimated AFR\n  0x{TIMING_MODE:06X} Timing Mode = 0 (OFF)\n  0x{TIMING_TARGET:06X} Base Timing Lock preset = {timing:.1f} deg BTDC\n\nChanged bytes: {len(diffs)}\nChanged regions:\n'''
    report += '\n'.join(f'  0x{s:06X}-0x{e:06X} ({e-s+1} bytes)' for s, e in groups(diffs))
    report += '''\n\nIMPORTANT:\n  Fuel Mode and Timing Mode are both OFF by default.\n  Checksum has NOT been recalculated. Open/save the output in EcuFlash and let\n  the proven subarudbw checksum workflow correct it before flashing.\n'''
    report_path.write_text(report, encoding='utf-8')

    print(report)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('input_bin', type=Path)
    ap.add_argument('output_bin', type=Path)
    ap.add_argument('report', type=Path)
    args = ap.parse_args()
    patch(args.input_bin, args.output_bin, args.report)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib

EXPECTED_BASE_SHA256 = '57cc8860190c15b74b8e7dbbf3bd9bf529f85a2df97d00df0fd73cbe1eedb17a'
EXPECTED_SIZE = 524288

PATCHES = {
    'forester_sg9_sti_MAP_IAT_GM_dMap_v68_SPARK_CUT_SAFE.bin': {
        'sha256': 'b9da808571b17bcd38bae71c6949c3da6d7ebcc2e17759abded1e6c1c0766466',
        'runs': [
            (0xA126, 'd304430b0009a007000900090009000900090006ae800009'),
            (0xA188, 'd303430b0009a02900090009000900090006af4000090009'),
            (0x1132E, 'ae00'),
            (0x6ADBD, '00'),
            (0x6ADC4, '000000000300000005000000'),
            (0x6AE00, '4f22d310430b0009d10f601020088915d10e601088018b09d10d6012d20d632233068b03d10c6010c97f2100d10b601020088903d10a6012d20a22024f26000b00090009000228c4'),
            (0x6AE4A, 'ca3b0006adc4'),
            (0x6AE52, 'b2180006a4d0'),
            (0x6AE5A, 'b8680006ad780006ad7c'),
            (0x6AE66, 'b6e8'),
            (0x6AE80, 'd020e10020108f3b63d33348633f43118d0163536d43336c523122d16d23d01a610021188929d019600088018b25d0186102d018620231268b1fd017670027788b00e701d01562003726890ad00de1012010e00362e35132302c21012d21a00000097701d00e62002228890137268b00e701d0092070a0030009e701d0062070000b0009'),
            (0x6AF06, 'ca78'),
            (0x6AF0A, 'ca3b0006adc4'),
            (0x6AF12, 'b2180006a4f0'),
            (0x6AF1A, 'ca790006adc80006adcc'),
            (0x6AF40, 'e0018076d007610021188b0962e33248622f42118d0100096e43356c535223e1000b0009'),
            (0x6AF66, 'ca78'),
        ],
    },
    'forester_sg9_sti_MAP_IAT_GM_dMap_v68_SPARK_CUT_ENABLED.bin': {
        'sha256': '8f02eecf37fad5340baf0ba5d66e62308a979660b4926c6ad0559fc53f869ecc',
        'runs': [
            (0xA126, 'd304430b0009a007000900090009000900090006ae800009'),
            (0xA188, 'd303430b0009a02900090009000900090006af4000090009'),
            (0x1132E, 'ae00'),
            (0x6ADBD, '00'),
            (0x6ADC4, '010000000300000005000000'),
            (0x6AE00, '4f22d310430b0009d10f601020088915d10e601088018b09d10d6012d20d632233068b03d10c6010c97f2100d10b601020088903d10a6012d20a22024f26000b00090009000228c4'),
            (0x6AE4A, 'ca3b0006adc4'),
            (0x6AE52, 'b2180006a4d0'),
            (0x6AE5A, 'b8680006ad780006ad7c'),
            (0x6AE66, 'b6e8'),
            (0x6AE80, 'd020e10020108f3b63d33348633f43118d0163536d43336c523122d16d23d01a610021188929d019600088018b25d0186102d018620231268b1fd017670027788b00e701d01562003726890ad00de1012010e00362e35132302c21012d21a00000097701d00e62002228890137268b00e701d0092070a0030009e701d0062070000b0009'),
            (0x6AF06, 'ca78'),
            (0x6AF0A, 'ca3b0006adc4'),
            (0x6AF12, 'b2180006a4f0'),
            (0x6AF1A, 'ca790006adc80006adcc'),
            (0x6AF40, 'e0018076d007610021188b0962e33248622f42118d0100096e43356c535223e1000b0009'),
            (0x6AF66, 'ca78'),
        ],
    },
    'forester_sg9_sti_MAP_IAT_GM_dMap_v69_CLEAN_SPARK_SAFE.bin': {
        'sha256': 'b3bb642372636c7abb312e7659f91ad4e69d683afe0a2d4d681eb3a405715ec2',
        'runs': [
            (0xA126, 'd304430b0009a007000900090009000900090006ae800009'),
            (0xA188, 'd303430b0009a02900090009000900090006af4000090009'),
            (0x1132E, 'b000'),
            (0x6ADBD, '00'),
            (0x6ADC4, '000000000200000005000000'),
            (0x6AE00, '4f22d310430b0009d10f601020088915d10e601088018b09d10d6012d20d632233068b03d10c6010c97f2100d10b601020088903d10a6012d20a22024f26000b00090009000228c4'),
            (0x6AE4A, 'ca3b0006adc4'),
            (0x6AE52, 'b2180006a4d0'),
            (0x6AE5A, 'b8680006ad780006ad7c'),
            (0x6AE66, 'b6e8'),
            (0x6AE80, 'd020e10020108f3b63d33348633f43118d0163536d43336c523122d16d23d01a610021188929d019600088018b25d0186102d018620231268b1fd017670027788b00e701d01562003726890ad00de1012010e00362e35132302c21012d21a00000097701d00e62002228890137268b00e701d0092070a0030009e701d0062070000b0009'),
            (0x6AF06, 'ca78'),
            (0x6AF0A, 'ca3b0006adc4'),
            (0x6AF12, 'b2180006a4f0'),
            (0x6AF1A, 'ca790006adc80006adcc'),
            (0x6AF40, 'e0018076d007610021188b0962e33248622f42118d0100096e43356c535223e1000b0009'),
            (0x6AF66, 'ca78'),
            (0x6B000, '4f22d312430b0009d111601020088919d110601088018b0dd10f6012d10f631233068b07d10e2132d10e2132d10e6010c97f2100d10d601020088903d10c6012d20c22024f26000b00090009000228c4'),
            (0x6B052, 'ca3b0006adc4'),
            (0x6B05A, 'b218'),
            (0x6B05E, 'ca4c'),
            (0x6B062, 'ca44'),
            (0x6B066, 'ca48'),
            (0x6B06A, 'b8680006ad780006ad7c'),
            (0x6B076, 'b6e8'),
        ],
    },
    'forester_sg9_sti_MAP_IAT_GM_dMap_v69_CLEAN_SPARK_CUT.bin': {
        'sha256': '02581366d410326102c8ca7ffe7f483e2b1ecdc1f7363cd8a7eac663c8d6e4aa',
        'runs': [
            (0xA126, 'd304430b0009a007000900090009000900090006ae800009'),
            (0xA188, 'd303430b0009a02900090009000900090006af4000090009'),
            (0x1132E, 'b000'),
            (0x6ADBD, '00'),
            (0x6ADC4, '010000000200000005000000'),
            (0x6AE00, '4f22d310430b0009d10f601020088915d10e601088018b09d10d6012d20d632233068b03d10c6010c97f2100d10b601020088903d10a6012d20a22024f26000b00090009000228c4'),
            (0x6AE4A, 'ca3b0006adc4'),
            (0x6AE52, 'b2180006a4d0'),
            (0x6AE5A, 'b8680006ad780006ad7c'),
            (0x6AE66, 'b6e8'),
            (0x6AE80, 'd020e10020108f3b63d33348633f43118d0163536d43336c523122d16d23d01a610021188929d019600088018b25d0186102d018620231268b1fd017670027788b00e701d01562003726890ad00de1012010e00362e35132302c21012d21a00000097701d00e62002228890137268b00e701d0092070a0030009e701d0062070000b0009'),
            (0x6AF06, 'ca78'),
            (0x6AF0A, 'ca3b0006adc4'),
            (0x6AF12, 'b2180006a4f0'),
            (0x6AF1A, 'ca790006adc80006adcc'),
            (0x6AF40, 'e0018076d007610021188b0962e33248622f42118d0100096e43356c535223e1000b0009'),
            (0x6AF66, 'ca78'),
            (0x6B000, '4f22d312430b0009d111601020088919d110601088018b0dd10f6012d10f631233068b07d10e2132d10e2132d10e6010c97f2100d10d601020088903d10c6012d20c22024f26000b00090009000228c4'),
            (0x6B052, 'ca3b0006adc4'),
            (0x6B05A, 'b218'),
            (0x6B05E, 'ca4c'),
            (0x6B062, 'ca44'),
            (0x6B066, 'ca48'),
            (0x6B06A, 'b8680006ad780006ad7c'),
            (0x6B076, 'b6e8'),
        ],
    },
}

def apply_patch(base: bytes, runs):
    out = bytearray(base)
    for offset, hexdata in runs:
        data = bytes.fromhex(hexdata)
        out[offset:offset+len(data)] = data
    return bytes(out)

def main():
    ap = argparse.ArgumentParser(description='Materialize exact A2WC0MME v68/v69 LC test ROMs from exact v67 base.')
    ap.add_argument('--input', required=True, type=Path)
    ap.add_argument('--out-dir', required=True, type=Path)
    args = ap.parse_args()
    base = args.input.read_bytes()
    if len(base) != EXPECTED_SIZE:
        raise SystemExit(f'bad v67 size: {len(base)}')
    got = hashlib.sha256(base).hexdigest()
    if got != EXPECTED_BASE_SHA256:
        raise SystemExit(f'bad v67 SHA256: {got}')
    if base[0x2000:0x2008] != b'A2WC0MME':
        raise SystemExit('bad internal ID')
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for filename, spec in PATCHES.items():
        out = apply_patch(base, spec['runs'])
        sha = hashlib.sha256(out).hexdigest()
        if sha != spec['sha256']:
            raise SystemExit(f'{filename}: hash mismatch {sha}')
        path = args.out_dir / filename
        path.write_bytes(out)
        print(f'{sha}  {path}')
if __name__ == '__main__':
    main()

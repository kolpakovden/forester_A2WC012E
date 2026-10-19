# Tip-in v31: static placement & integrity audit (2026-10-20)

**Status: OFFLINE RESEARCH; v30 LAB must NOT be flashed.** The ROMs were tested against pinned SHA-256 hashes; no binary was changed or pushed.

## Reproduced on source ROM and laboratory v30
- v25 SHA-256: `2ca539d0c47e3b1eec96c41e1e514c7b19b0e3786e9d826a41d3a3505b4c5d99`.
- v30 SHA-256: `accd26e250cba8b8757718a6fdcb5aa2a080f3b7774a6712f9006c7515f2ff08`.
- Both images exactly 524288 bytes.
- 15 byte offsets differ: `0x105C5–0x105C7` (pointer `0x105C4: 0x00024A04 → 0x0006AC40`) and `0x6AC40–0x6AC4B` (12 byte wrapper). The high-order pointer byte `0x105C4` remains `00`.
- `0x103F0 D2 74`, `0x103F2 42 0B`, `0x103F4 00 09` unchanged. SH PC-relative load points to `0x105C4`.
- Wrapper: `D2 01; 42 2B; 00 09; 00 09; 00 02 4A 04`. Ghidra also independently decoded `MOV.L @(1,PC),R2; JMP @R2; NOP` with literal `0x24A04`.
- Baseline `0x6AC40–0x6AC4B` was all `FF`, inside the uninterrupted run `[0x6AC3D,0x7FAF8)`, **85,691** bytes.
- OEM `0x24A04–0x24B73` unchanged, last 32 bytes of ROM unchanged.

## Simple sums (NOT validated Subaru checksum)
| Metric | v25 | v30 |
|---|---|---|
| Byte sum modulo 65536 | `D485` | `CAD5` |
| Big-endian uint16 sum modulo 65536 | `775A` | `37E4` |
| Big-endian uint32 sum modulo 2^32 | `0FDB7C2E` | `E1EC6AA5` |

These changes do **not** establish what checksum ECUFlash/bootloader uses or whether ECU integrity check passes or fails. The original ROM's last bytes remaining unchanged is also not sufficient evidence.

## Blocking uncertainties
1. A large `FF` fill is **not proof of unused, executable ROM**; flash sector, device mapping, checksumming, aliases and reserved area must be determined.
2. Dynamic behavior and exact PR/R2/stack preservation must be validated on a bench. The trampoline changes cycle count even though intended arithmetic is neutral.
3. Actual Subaru checksum verification/correction algorithm remains unidentified and untested. Do not create a flash-ready ROM based on simple sums.
4. Hook safety, hardware event timing and CarBerry input/output unit conversions remain unverified.

## Reproduce
`python3 tools/tipin-v31/audit_v31.py Forester_SG9_MAP_clean_v25.bin Forester_SG9_v30_NEUTRAL_HOOK_OFFLINE_NOT_FOR_FLASH.bin`

No ECU flash until checksum, executable-region semantics and bench results have been verified.

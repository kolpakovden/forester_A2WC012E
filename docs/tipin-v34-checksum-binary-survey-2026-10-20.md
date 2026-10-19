# v34 — checksum-module identification and ROM boundary evidence (2026-10-20)

**OFFLINE STATIC RESEARCH ONLY — no validated checksum algorithm, no flash approval.**

## Artifacts inspected locally
- EcuFlash v1.44.4347 user-provided Windows EXE, PE32 x86, section layout including .text, .rdata, .data. Static strings confirm `SubaruDBWChecksumModule`, `subarudbw`, `Checksum Incorrect`, and correction prompt. No checksum execution path or actual arithmetic algorithm has yet been recovered; this is **not reverse-engineering completion**.
- `A2WC012E.xml` declares `checksummodule=subarudbw`, `memmodel=SH7055`, `flashmethod=sti04`. The local user-copied `A2WC0MME.xml` retains `ecuid=3B02594316` from the donor; **ECUID has not been verified for A2WC0MME** and this derivative XML is unsafe as authoritative ECU flashing metadata.
- Original `A2WC0MME` v25 hash `2ca539d0c47e3b1eec96c41e1e514c7b19b0e3786e9d826a41d3a3505b4c5d99`.
- v30 neutral-hook hash `accd26e250cba8b8757718a6fdcb5aa2a080f3b7774a6712f9006c7515f2ff08`.
- One-byte corrupted offline probe hash `0790a0888d7c1a1863d387055af9d87d995758cdea2885adab83a4f01a25eed6`.

## Direct image evidence
- At `0x6AC20`, the source contains code and PC-relative data; `0x6AC28..0x6AC3B` includes non-FF literals. Erased span begins `0x6AC3D`; patch landing `0x6AC40` is only 3 bytes beyond first erased byte. **No executable/sector safety proof**.
- At `0x7FAF8`, data begins `43 49 FF FF 00 00 88 9A`.
- At `0x7FF00`, starts `00 00 2E D8 00 00 50 D0 00 00 2E F0 00 00 50 D0`; this appears like address/value records but purpose unproven.
- At `0x7FFF8`: `00 00 EF 6C 00 00 20 00`.
- ROM header `0x1FFC`: `34 11 00 01`, followed at `0x2000` by `A2WC0MME`.

## Empirical checksum behavior
- EcuFlash recognizes `A2WC0MME` using the locally fabricated XML; it opens source and patched ROM. Simple `Save ROM As` did not change either file. A modified single byte at `0x58DAB` did not trigger a prompt upon opening.
- **This does not imply checksum validity or disabled checksum.** Such prompts may depend on write path, flags, supported image format, or actual checksum regions.
- Distinguish flash communication CRC and the `subarudbw` ROM correction algorithm. See general SH7055 tool implementation at https://github.com/rimwall/fastecu-oem/blob/master/modules/flash_ecu_subaru_denso_sh7055_02.cpp (CRC used to compare flash blocks; not proof of `subarudbw` behavior).

## Next precise work
1. Obtain source or disassemble `SubaruDBWChecksumModule` class methods in PE, trace to metadata-aware checksum dispatch, identify offsets and flags.
2. Recover exact checksum algorithm; validate against pinned clean BIN and deliberately corrupted BIN, with a known-good expected checksum.
3. Validate write/execute sector geometry for SH7055, particularly `0x6AC40` and tail region. Avoid using nearby FF as a safety guarantee.
4. Keep tested laboratory BIN separate. Do not select the copied ECUID as an unverified ECU target.

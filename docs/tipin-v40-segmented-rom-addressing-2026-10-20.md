# v40 — segmented ROM addressing in EcuFlash (2026-10-20)

**Offline-only reverse engineering; no validated checksum or flash-ready BIN.**

Input SHA256 EXE `80ab6e185ac2383651b592751e0c9db1a7cf2cbe3c039e6363d90cdf7cea74dd`.

Verified disassembly:
- `0x4C2910` supplies logical addresses `0x13F500` for 17 records and `0x13F5E8` for 2 records to `0x4C26C0`, which calls `0x456EA0` to read each set of 12-byte records.
- `0x456EA0` invokes `0x456C10` for mapped section lookup. At `0x456C74`, EcuFlash compares logical address against `[esi+0x34]` section start and at `0x456C79` against `[esi+0x38]` section end. `0x456EA0` loads those limits through `[edi+0x34]`/`[edi+0x38]` then calls `0x45A990` for mapped read.
- So logical `0x13F500` **is not a verified raw 512KiB file offset**, and simple subtraction by `0x100000` is merely a hypothesis; exact model-to-file translation is still unproven.
- Original v25 hash `2ca539d0c47e3b1eec96c41e1e514c7b19b0e3786e9d826a41d3a3505b4c5d99`; offline probe differs at only `0x58DAB` (1 byte). Neutral v30 differs by 15 bytes: `0x105C5..0x105C7` and `0x6AC40..0x6AC4B`. Saved v30 is identical to generated v30.

Next: identify section creation and back-buffer layout, map checksum table addresses, independently calculate/check actual checksums on v25/probe/v30, inspect flash execution blocks and copied ECUID. **No claim of checksum passing, and no flashing permitted.**

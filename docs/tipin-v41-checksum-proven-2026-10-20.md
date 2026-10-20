# v41 — A2WC0MME SH7055 checksum reproduced and neutral hook repaired (2026-10-20)

**CHECKSUM VERIFIED OFFLINE; BENCH-ONLY BIN; NO ON-CAR FLASH CLEARANCE.**

## Corrected previous branch assumption
The branch at EcuFlash VA 0x4C293A for CPU string SH7055 goes to 0x4C29E6, **not** the hardcoded 0x13F500/0x13F5E8 record addresses. SH7055 computes the checksum-table address from ROM bounds (`end-start-0x47f`). In the pinned 512-KiB A2WC0MME image this resolves to file offset **0x7FB80**. EcuFlash SH7055 checksum table has 17 records, each 12 bytes; only record 0 is active, records 1..16 have (0,0,0x5AA5A55A).

Record 0 at 0x7FB80: start `0x00002000`, inclusive end `0x0007FAF7`, big-endian correction at `0x7FB88`. Checksum adds all big-endian 32-bit words in range `[0x2000,0x7FAF7]`, modulo 2^32; sum plus correction must equal **0x5AA5A55A**.

Reproduced independently:
- Original v25 (SHA256 `2ca539d0c47e3b1eec96c41e1e514c7b19b0e3786e9d826a41d3a3505b4c5d99`): sum `0x344B7833` + stored `0x265A2D27` = `0x5AA5A55A`: **PASS**.
- One-byte corrupted probe: sum `0x344B7834` + stored `0x265A2D27` = `0x5AA5A55B`: **FAIL**, one-count deviation.
- Lab v30 (SHA256 `accd26e250cba8b8757718a6fdcb5aa2a080f3b7774a6712f9006c7515f2ff08`): sum `0x065C66AA` + stored `0x265A2D27` = `0x2CB693D1`: **FAIL**.
- New checksum-fixed v41: sum `0x065C66AA` + corrected `0x54493EB0` = `0x5AA5A55A`: **PASS**.
- New v41 SHA256: `26e3f36ad835000286f85d896506825bea1e24be0167c28efae6a584d92fe13b`. Size 0x80000. Relative to lab v30, **only** 4 checksum bytes `0x7FB88..0x7FB8B` change. Relative to original v25 there are 19 changed bytes total: 15 hook, 4 checksum.

Reproducible offline builder in `tools/tipin-v41/build_checksum_v41.py` (source BINs must match pinned hashes).

## Critical unclosed safety issues
1. Hook target `0x6AC40` sits in a region full of FF. This proves original bytes are blank but **does not prove sector write coverage, valid runtime address translation, executable memory mapping, or freedom from other code consumers**.
2. EcuFlash user-created `A2WC0MME.xml` was copied from `A2WC012E.xml`; field `ecuid=3B02594316` has **not been proven for the ECU**.
3. Only a neutral pass-through hook was built, **not CarBerry Tip-in control**. Passing checksum is not functional verification.
4. No bench hardware or car test occurred. Preserve original recovery image and verify original ECU IDs, voltage stability and recoverability with appropriate equipment.

**Never treat this v41 as verified safe for the user's car.**

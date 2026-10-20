# v44 — sti04 SH7055 offline flash path evidence (2026-10-20)

**Result: SH7055/sti04 compatibility at the family level is supported; exact EcuFlash 1.44 flashing path and user ECU remain unverified. DO NOT FLASH v41 solely on this basis.**

## Source checks

1. The A2WC012E donor XML records `<flashmethod>sti04</flashmethod>`, `<memmodel>SH7055</memmodel>`, `<checksummodule>subarudbw</checksummodule>`, but its ECU ID `3B02594316` was copied to the locally fabricated A2WC0MME XML without verification. A2WC0MME ROM ID by itself does not validate an ECU-specific protocol ID.
2. Public OpenECU unbrick guide lists **Subaru 2004 DBW STi/FXT/LGT/Baja, sti04, SH7055, 512k**, separately from **sti05, SH7058, 1024k**. https://raw.githubusercontent.com/OhNineSTI/subaru-unbrick/refs/heads/main/Unbrick.pdf
3. The third-party **FastECU** open source method `modules/flash_ecu_subaru_denso_sh7055_04.cpp` at https://github.com/rimwall/fastecu-oem/blob/master/modules/flash_ecu_subaru_denso_sh7055_04.cpp implements `get_changed_blocks_kline_32bit` before writing, compares each block using a remote checksum/CRC request, reflashes only changed blocks with `reflash_block_kline_32bit`, and compares again after. This proves that one SH7055/04 implementation follows a block compare/reflash/check flow. It does **not** prove Tactrix EcuFlash implementation does the same thing.
4. The user-supplied **actual EcuFlash 1.44 EXE** contains literal `sti04` at file `0x7622E0` VA `0xB63CE0`, referred to from executable code VA `0x4BC214`. Also contains log strings `comparing ECU flash memory pages to image file --` and `kernel flash buffer size`; but strings alone cannot attribute these to the sti04 path or establish safe runtime flashing.
5. The publicly available EcuFlash log in https://minkara.carview.co.jp/group/OpenECU/bbs/1137711/121-150/ for a 524288-byte Subaru ROM shows a **SH7055 DUAL kernel**, flash buffer size **4096**, per-segment CRC32 comparison, and selective programming workflow. It is a different older release and ECU and thus corroborative, **not** direct validation of this exact current ECU / EcuFlash build.

## Pinned offline image facts (previous v41/v43; independently reproducible)

- Original v25: SHA256 `2ca539d0c47e3b1eec96c41e1e514c7b19b0e3786e9d826a41d3a3505b4c5d99`.
- v41: SHA256 `26e3f36ad835000286f85d896506825bea1e24be0167c28efae6a584d92fe13b`, 512KiB, 19 byte changes in **EB9** (`0x10000..0x1FFFF`: 3), **EB14** (`0x60000..0x6FFFF`:12), **EB15** (`0x70000..0x7FFFF`:4). Their erase granularity is three distinct 64KiB blocks. No other byte modifications.
- v41 SubaruDBW checksum `0x065C66AA + 0x54493EB0 = 0x5AA5A55A` verified.
- Neutral hook static control-flow review passed. It is *not* a CarBerry behavior port, and code deployment does not establish runtime correctness.

## Explicit gates still open

- Independently verify live ECU SSM ECU ID and on-car full stock read; compare bit-for-bit and retain recovery backup. The locally copied ECUID from another XML must never be relied on.
- Tactrix EcuFlash 1.44's own sti04 flash code/kernel, block erasure and verification are not fully traced from the supplied executable; a string registration pointer is insufficient.
- Battery power stability, actual bootloader compatibility, and recovery after a failed flash cannot be proven with BIN-only analysis.
- A third-party **test write** is not a guarantee that EcuFlash's command of the same name behaves identically; do not infer hardware harmlessness from this offline analysis.

**v44 does not create a new BIN. Continue to label v41 BENCH ONLY, NOT TESTED FOR FLASH ON A VEHICLE.**

# v43 — SH7055 flash-block audit (2026-10-20)

**OFFLINE/BENCH ONLY. NOT FLASH-APPROVED.**

v25 SHA256: `2ca539d0c47e3b1eec96c41e1e514c7b19b0e3786e9d826a41d3a3505b4c5d99`.
v41 SHA256: `26e3f36ad835000286f85d896506825bea1e24be0167c28efae6a584d92fe13b`.
Both 524288 bytes.

Actual SH7055 512-KiB chip block layout: 8 x 0x1000, 1 x 0x8000, 7 x 0x10000. This is NOT the SH7058 1-MiB layout. Offsets and CRC32 (zlib on block bytes) experimentally checked using pinned original v25 and neutral v41:

| Block | Range | Changes | CRC32 v25 | CRC32 v41 |
| --- | --- | --- | --- | --- |
| EB9 | 0x10000–0x1FFFF | 3, 0x105C5–0x105C7 | 2576ACE0 | 492AA598 |
| EB14 | 0x60000–0x6FFFF | 12, 0x6AC40–0x6AC4B | CA0E7962 | DF10D3AD |
| EB15 | 0x70000–0x7FFFF | 4, 0x7FB88–0x7FB8B | 3E63593E | 9C55D870 |

13 other blocks are byte-identical. Three changed erase blocks cover 192 KiB despite only 19 differing bytes. Offline SubaruDBW checksum v41: 0x065C66AA + 0x54493EB0 = 0x5AA5A55A.

**Not confirmed**: exact implementation/coverage of `sti04` kernel used by EcuFlash 1.44, ECU ID retained from donor XML, live ECU and voltage, recovery, whether all original blocks are actually written/restored by flashing tool. Local zlib CRC32 is not automatically on-wire EcuFlash kernel CRC. This is still neutral hook, not CarBerry Tip-in. No flashing.

Sources: Renesas SH7055 hardware manual (see https://www.renesas.com/en/document/mah/sh-2e-sh7055s-hardware-manual), FastECU SH7055 kernel/flash implementation https://github.com/rimwall/fastecu-oem/blob/master/modules/flash_ecu_subaru_denso_sh7055_04.cpp ; note the james-portman 1-MB SH7058 kernel block listing is not valid for SH7055.

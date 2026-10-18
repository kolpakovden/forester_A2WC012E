# CarBerry Ghidra HC16 diagnostic scripts

These are **read-only Java GhidraScript tools**, for Ghidra 12.1.x with an HC16 language module. The repository copies are maintained/condensed versions of the Java scans used in the October 2026 research, rather than byte-for-byte snapshots of earlier chat ZIPs. Names and report formats are preserved.

- `FindCarBerryTipInWriter.java`: initial static-listing scan and Ghidra diagnostics for RAM `0x17D6..0x17DA`; saves `carberry_tps_delta_xrefs.txt`.
- `CarBerryTPSDeepScan.java`: additional ROM raw signature scan, undefined regions, nearby accesses and indexed write inventory; saves `carberry_tps_delta_deep.txt` and `carberry_indexed_writes.csv`.

## Running

1. Open **the analyzed original CarBerry** program `work2_100+95_3D04EA4605_CarBerry42_FULL_160KiB.bin`, not the second import `original_carberry.bin` with zero instructions.
2. In Ghidra Script Manager, add this folder to script directories and Refresh.
3. Run the **.java** script; ordinary Ghidra without PyGhidra cannot run the original `.py` script.
4. Choose an **existing** destination folder. Missing parent folders cause `NoSuchFileException`.

The original scan observed 1,026 functions and 31,250 already-defined instructions, but **missed producer code** because `0x004D5E..0x004E09` was not disassembled. Raw ROM pairs at `0x004DF4` revealed the real store to `0x17DA`; manual Ghidra disassembly verified it. Likewise a raw `FA 00 4D 5E` at `0x000350` was decoded to `JSR FUN_004D5E` inside an interrupt path.

**Caution:** indexed-write rows and raw byte matches are candidates, not proof of actual RAM writes. HC16 bank/address contexts must be inspected manually. Neither script disassembles, modifies, or patches the BIN.

Research write-up: [Tip-in Delta interrupt evidence](../../docs/carberry-tipin-delta-interrupt-2026-10-19.md).

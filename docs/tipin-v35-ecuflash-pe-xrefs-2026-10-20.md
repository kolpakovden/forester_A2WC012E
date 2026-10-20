# v35 — EcuFlash checksum module: PE xrefs (2026-10-20)

**Static analysis only. Algorithm NOT recovered; do NOT flash any Tip-in LAB image.**

Pinned user-supplied EcuFlash v1.44 executable: 11,370,696 bytes; SHA-256 `80ab6e185ac2383651b592751e0c9db1a7cf2cbe3c039e6363d90cdf7cea74dd`. Binary is not committed.

Confirmed PE32/x86 section mapping: `.text` file `0x400` → VA `0x401000`; `.rdata` file `0x74F600` → VA `0xB51000`; `.data` file `0xA64A00` → VA `0xE67000`.

## Specific string references
- ASCII `subarudbw` at file `0x750550`, VA `0xB51F50`. Absolute x86 immediate reference at file `0x245B9` = VA `0x4251B9` inside routine beginning near `0x425180`. This routine constructs/registers an object and copies the module-name string into its member field (observed instruction sequence).
- `SubaruDBWChecksumModule` at file `0x790108`, VA `0xB91B08`, with a direct VA reference near file `0xC8662` = `0x4C9262`. Further identical strings in `.data` suggest class metadata; their exact RTTI roles not yet established.
- `Checksum Incorrect` at file `0x75CF08`, VA `0xB5E908`; references at file `0x901A8`, `0x6F0028`, `0x73FC55` (VAs respectively `0x490DA8`, `0xAF0C28`, `0xB40855`). These may be UI-related; **not proof of actual checksum verification**.
- `WARNING: this ROM` at file `0x762C00`, VA `0xB64600`; references at file `0xC1C7A` and `0xC2017` (VAs `0x4C287A`, `0x4C2C17`). This warning may be on a separate analysis or logging path.

## Repro
Run `python3 tools/tipin-v35/pe_xrefs_v35.py ecuflash.exe` and independently inspect the reported VAs with a PE-aware disassembler. Absolute-reference scanning intentionally misses references via indirect tables, relative offsets, virtual dispatch and other addressing modes.

## What remains unknown
- The algorithm and correct offsets for `subarudbw`, its guard conditions, and whether `A2WC0MME` is actually covered.
- Whether `Save ROM As` invokes the module. Experiments show no byte changes, but that does not prove correctness or absence of checks.
- Whether `0x6AC40` is physically executed / included by flash loader; the wrapper's SH code only passes static disassembly.

**Next technical branch:** identify C++ RTTI/vtable for SubaruDBWChecksumModule, follow its virtual methods into the checksum calculation, then validate against known-good/bad images offline. Treat the fabricated A2WC0MME metadata ECUID as unverified.

# v47: HC16 TPS provenance offline

Pinned CarBerry source SHA256 b06e1282a4b274db856d250ae8a1babaf175729f7f9e9fec12e465fb774a4483 and SG9 v39 SHA256 43a4751d68da4ddca9d483c1723a78f04c85ad982423f48177402f9962245ad4.

Verified instruction bytes in original ROM:
- 0x04E58: 17 65 17 DA, LDAA 0x17DA,IZ
- 0x04E5C: 17 6A 17 D9, STAA 0x17D9,IZ
- 0x06D5C: 17 6A 17 D9, STAA 0x17D9,IZ (second writer)
- 0x0A7D0: 17 E5 17 D9, LDAB 0x17D9,IZ
- 0x0A7FE: 17 65 17 D9, LDAA 0x17D9,IZ

Previous Ghidra export attributes first writer and copy to FUN_004E0A, second writer to FUN_006906, and readers to FUN_00A7C4. Indexed IZ base, HC16 banking, provenance of byte at 0x17DA, cadence, units and sign are still unverified. In particular **0x17D9 is not proven to be an absolute TPS-delta RAM byte**.

Next: in the existing HC16 Ghidra database decompile those 3 functions, inspect IZ base and caller chains, compare physical encoding to SG9 v39 OEM routine 0x24A04. Active CarBerry ROM patch must wait for compatible input units and output actuator safety proof. v45 remains neutral bench-only.

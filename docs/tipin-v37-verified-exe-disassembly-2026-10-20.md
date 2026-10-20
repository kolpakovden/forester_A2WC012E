# v37 — Verified EcuFlash call-site & RTTI-adjacent structures (2026-10-20)

**Static reverse-engineering; checksum algorithm not yet located. Not for ECU flashing.**

Input: user-provided EcuFlash v1.44.4347 PE32 x86, SHA256 `80ab6e185ac2383651b592751e0c9db1a7cf2cbe3c039e6363d90cdf7cea74dd`. Inspected with GNU objdump and raw section bytes; the EXE is not redistributed.

### Disassembly evidence
```asm
00425180: push ecx
...
004251B8: push 0x00B51F50            ; ASCII "subarudbw"
004251BE: call 0x00401090
004251C3: mov edx,[eax]
004251C5: mov ecx,[esi+0xA0]
004251CB: mov [esi+0xA0],edx
```
This **establishes assignment of module-name string into an object** at offset `+A0` near function `0x425180`; it is not the calculation routine.

```asm
004C9250: push edi
004C9261: mov esi,0x00B91B08       ; ASCII "SubaruDBWChecksumModule"
004C9268: mov bl,[edx]
004C926A: cmp bl,[esi]
...
004C929A: call 0x004C39B0
```
This routine compares the class-name string against a caller-supplied string. Likely part of class identification, **not** the checksum algorithm. Further xrefs for `0x4C9250` and nearby type descriptors are needed.

At file offset `0x7900E0` (`.rdata`) multiple little-endian pointer values precede the class-name string at file `0x790108` (VA `0xB91B08`): `0xB8C5E4,0xB91A7C,0xB91AA4,0x9159D0`, with additional metadata immediately before class text. Could represent RTTI/type-descriptor graph, but fields and roles are **not independently validated**.

Nearby file `0x750580` starts `subarudiesel\0 ... mitsucan ... mitsuh8\0` followed by several function pointers. The adjacency is insufficient to label this collection the specific `SubaruDBWChecksumModule` vtable.

### Important correction
Earlier phrasing that "the vtable was found" was too strong. No verified checksum method entry point, dispatch guards, checksum table, or repair algorithm has yet been established. The one-byte probe did not cause an opening-time warning, which is not proof that checksums are off.

### Next concrete work
1. Parse MSVC RTTI CompleteObjectLocator/type descriptors for the checksum class and find associated vftable address(es); apply relocation-aware cross-reference scans.
2. Determine which vtable slot handles checksum validation/correction; trace writes into ROM buffer and guards.
3. Independently validate against clean v25, 1-byte probe, and neutral v30; review flash sector/execution mapping for `0x6AC40` before any bench image.

All work remains **OFFLINE**, with no flashable image.

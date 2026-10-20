# v36 — EcuFlash static checksum-class investigation (2026-10-20)

**Offline research; no validated checksum algorithm, no flash authorization.**

Inspected pinned user-supplied EcuFlash 1.44.4347 x86 PE (SHA-256 `80ab6e185ac2383651b592751e0c9db1a7cf2cbe3c039e6363d90cdf7cea74dd`) with `objdump -D -Mintel` and byte/reference scans.

## Confirmed instruction evidence

```asm
004251b8: 68 50 1f b5 00  push 0xB51F50   ; "subarudbw"
004251be: e8 cd be fd ff  call 0x401090
```

- Near `0x425180` is a constructor-like method which copies the module-name string into an object field `[esi+0xA0]`. Treating this as an algorithm implementation would be incorrect.
- An occurrence of `SubaruDBWChecksumModule` at `0xB91B08` is directly referenced near `0x4C9262` within string comparison/class metadata-like code. The exact C++ RTTI/vtable relationship has NOT been demonstrated.
- Adjacent to the module-name strings is a plausible list of code pointers starting `0xB51F84` with entries `0x4C3AF0`, `0x4C3A70`, `0x773FD0`, `0x403A70`, `0x9CA070`, `0x664380`. **This must not be described as an established SubaruDBWChecksumModule vtable.** Sample disassembly at `0x4C3A70` contains a string-comparison loop and at `0x664380` simply `xor al,al; ret 8`. Their roles are unproven.
- `Checksum Incorrect` appears in executable string resources, but its presence does not prove that an `A2WC0MME` checksum check runs at ROM load or save time.

## Reproducibility

Run `python3 tools/tipin-v36/pe_candidate_survey_v36.py "ecuflash.exe"`. Outputs string occurrences, pointer references and nearby pointer words. Uses SHA pinning and does not launch EXE or change any files.

## Remaining work / next evidence gate

1. Follow object creation sites and assignments of VAs into vtable pointers; differentiate unrelated polymorphic classes in nearby `.rdata`.
2. Recover concrete checksum method entrypoint and guards via call-chain dataflow analysis.
3. Reproduce algorithm on clean v25, deliberately modified one-byte probe, and neutral v30 to prove correct coverage; then verify a correct fixup, with exact offsets.
4. Verify executable mapping and memory sectors at `0x6AC40` independently. `FF` in original image is not evidence of safety.

**No claim of checksum correction; no image in this stage is ready for ECU flashing.**

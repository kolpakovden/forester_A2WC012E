# v30: verified call site and neutral tail jump proof (2026-10-20)

**OFFLINE LAB ONLY — NOT FOR ECU FLASH.** Original clean v25 ROM SHA-256: `2ca539d0c47e3b1eec96c41e1e514c7b19b0e3786e9d826a41d3a3505b4c5d99`.

## Confirmed from Ghidra + ROM
- `0x103F0: D2 74` = `MOV.L @(disp,PC),R2`. SH PC-relative calculation targets `0x105C4`.
- `0x103F2: 42 0B` = `JSR @R2`; `0x103F4: 00 09` = `NOP` delay slot.
- `0x105C4: 00 02 4A 04` = address `0x00024A04`, verified `FUN_00024A04` (OEM Tip-in).
- Ghidra XREF: `0x103F0(R) → PTR_FUN_000105C4 → FUN_00024A04`.
- Adjacent PC-relative call/literal pattern continues; `0x104D4: BRA 0x1065C` jumps over the inline address pool. These are sequential calls, not an indexed dispatcher; the earlier 'index 59' interpretation is obsolete.
- Result before OEM injection scheduling is FR14 written to `FFFFB80C` at `0x24B16`, followed by minimum check and eventual `FFFFB810` at `0x24B38`; the OEM calculation and injector hardware scheduling are preserved.

## Experimental (unverified executable placement)
Candidate wrapper location `0x6AC40` is all FF in source v25, but **FF does not establish free/executable memory or checksum exclusion**. It has NOT been vetted for image checksums, flash sectors, overlay, memory accessibility, code reference aliases or runtime timing. DO NOT FLASH.

Literal pointer `0x105C4` is rewritten from `0x00024A04` to `0x0006AC40`; 3 changed bytes. Wrapper at `0x6AC40`, 12 bytes:

```asm
6AC40: D2 01          mov.l @(1,pc),r2     ; literal at 6AC48
6AC42: 42 2B          jmp @r2
6AC44: 00 09          nop                ; delay slot
6AC46: 00 09          nop                ; pad
6AC48: 00 02 4A 04    .long 0x00024A04  ; OEM target
```

The caller's `JSR` sets PR for the normal continuation at `0x103F6`; the wrapper's `JMP` leaves PR untouched. At OEM entry R2 is restored to the exact original `0x24A04` target, other registers and stack untouched. The extra cycles **do** affect timing: neutral means *same arithmetic and control state*, not proven timing-identical. Only one call site/pointer consumer was confirmed in currently analyzed code, not necessarily all runtime routes.

### Automated static assertions
`python3 tools/tipin-v30/build_neutral_hook_lab.py Forester_SG9_MAP_clean_v25.bin output_LAB.bin`

Checks SHA, fixed call opcodes, OEM target, FF destination, ROM size, preservation of OEM function/calibration, and exactly 15 byte differences. Lab output SHA-256 `accd26e250cba8b8757718a6fdcb5aa2a080f3b7774a6712f9006c7515f2ff08`. **Output must not be flashed.** No checksum update, emulation or on-ECU tests yet.

## Remaining prerequisites
1. Prove `0x6AC40` is executable and unallocated; evaluate image/sector checksums.
2. Independently disassemble wrapper as SH7055 and check R2/PR/FPSCR path, ISR/reentrancy/timing.
3. Find all uses of pointer `0x105C4`, not solely Ghidra XREF.
4. Instrument/evaluate behavior on bench before any CarBerry calculations replace fueling.
5. Establish CarBerry ΔTPS input/output scale and pulse-unit correspondence; avoid changing injector schedule blindly.

No binaries are committed; git stores source and documentation only.

# Forester SG9 A2WC0MME: CarBerry Tip-in port, v26–v30 (2026-10-20)

**Status: OFFLINE / RESEARCH — do not flash.** Branch: `research/carberry-hc16-tipin`. Original Forester ROM: clean v25 (not v84), 524288 bytes, SHA-256 `2ca539d0c47e3b1eec96c41e1e514c7b19b0e3786e9d826a41d3a3505b4c5d99`. CarBerry source SHA-256 `b06e1282a4b274db856d250ae8a1babaf175729f7f9e9fec12e465fb774a4483`.

## Versions and evidence
- **v26 laboratory-only BIN**: changed float32 BE `0x58DA8` from 250.0 to 200.0 (one byte, offset `0x58DA9`); checksum/injector safety not verified. Not a CarBerry port and **not for ECU flash**. No modified BIN uploaded to Git.
- **v27 mapping study**: CarBerry 18-node byte axis/table `0x21400/0x21414` vs Forester 18-node ΔTPS float axis `0x59B3C` and uint16 values `0x59B84`. CarBerry compensations: RPM `0x21429`, boost error `0x21438`, ECT `0x21445`. Physical mappings, sampling and arithmetic compatibility remain unproven. See `port_mapping.csv`.
- **v28 C99 fixed-point shadow prototype**: 35,131 model-to-model comparisons against Python passed; does **not** prove byte-exact HC16 behavior. C-only code under `tipin_v28.c`, not ECU-target compiled code.
- **v29 static hook feasibility**: five unmodified source regions SHA-256-pinned in `region_fingerprints.csv`, and `tools/tipin-v30/verify_baseline.py` verifies them. No hook inserted.
- **v30 first actionable step**: added read-only ROM preflight/assertions for the known integration boundary. It detects mismatched ROMs, unapproved v26 edits and code drift before any assembler/patch work. **No flashable v30 BIN**.

## Established OEM pipeline
`TPS history 0x171C6 → Tip-in gate/computation 0x24A22–0x24B5C → event dispatch 0x272F8 → conversion 0x27344 → scheduler 0x985C → counter write 0x9B10`.
`FUN_27344` converts FR4 through a float 0.25 divisor before integer conversion; selected `0x985C` branches apply four SHAR shifts and combine with pending count. **Physical pulse time and complete timing in all branches still unproven**. Preserve OEM gating and scheduler.

### VBR exploration note
Function `0x129C` executes `MOV.L @(0x1364,PC),R3` at `0x12AA`, followed by `LDC R3,VBR` at `0x12AC`; source word `0x1364` holds `0x00001F4C`. This setup is on a conditional execution path. `0x254C` is a small clamp routine, not a verified ATU-II ISR. Do not claim a verified ISR from simple `VBR+offset` arithmetic.

## v30 design constraints
1. Do **not** hook inside `0x985C/0x9B10`; keep original injectors scheduler intact.
2. Candidate hook should be after OEM activation gate and before event dispatch, but exact instruction, SH ABI, relocations, FPU saving, scratch ROM and reentrancy are **not** validated yet.
3. Neutral hook must be byte/behavior-identical to OEM output; validate with bench instrumentation and checksum before any vehicle tests.
4. Prove CarBerry input byte↔Forester ΔTPS mapping, every compensation rounding branch, output scale and worst-case duration/overlap first.
5. Keep v25 clean ROM unchanged; do not conflate this research with v84/v85 FFS/LC work.

Run: `python3 tools/tipin-v30/verify_baseline.py /path/to/Forester_SG9_MAP_clean_v25.bin`. Optional second argument: laboratory v26 BIN to check the exact one-byte delta. Do not use these checks as evidence of flash safety.

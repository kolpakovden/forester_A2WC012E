# CarBerry 4.2 Tip-in: HC16 Delta producer, interrupt path and Ghidra evidence (2026-10-19)

**Scope:** reverse engineering only; preserve the original ROM and Forester v84. This addendum supersedes older "TPS Delta source unknown" notes in [carberry-hc16-tipin-research.md](carberry-hc16-tipin-research.md). Processor: experimental `HC-16:BE:16:default` on Ghidra 12.1.4. CarBerry original SHA-256: `b06e1282a4b274db856d250ae8a1babaf175729f7f9e9fec12e465fb774a4483`.

## 1. Discovery and diagnostics

We had *two different Ghidra program databases for the same BIN*:
- `original_carberry.bin`: 0 functions and 0 instructions, ROM imported as data; running `FindCarBerryTipInWriter.java` found no hits (false negative).
- `work2_100+95_3D04EA4605_CarBerry42_FULL_160KiB.bin`: 1,026 functions and 31,250 recognized instructions **before additional manual disassembly**. The script found 13 direct operands to RAM `0x17D6..0x17DA`; only startup had an apparent write to `0x17DA`. No pointer bases were identified.

The read-only `CarBerryTPSDeepScan.java` v3 additionally detected raw byte pairs `17 D6..17 DA` in *undefined code region `0x004D5E..0x004E09`*. The pair at ROM `0x004DF6` is preceded by `17 6A`, corresponding to `STAA 0x17DA,IZ` at **0x004DF4**. After the user manually disassembled from 0x004D5E, the instruction and full function were confirmed. **Never treat raw-byte hits as instructions until decoded in context.**

## 2. Exact producer of RAM 0x17DA: FUN_004D5E

Relevant listing supplied by the user:

```asm
004D5E LDD   0x17C0,IZ
004D62 STD   0x17C4,IZ
004D66 LDD   0x081C,IZ
004D6A STD   0x17C0,IZ
004D6E SUBD  0x03C8,IZ
004D72 BCC   004D76
004D74 CLRD
004D76 STD   0x17D0,IZ
004D7A BRCLR 0x01,0xDC,IZ,004D82
004D7E LDAA  #0x0D
004D80 CLRB
004D82 STAA  0x17C8,IZ
...
004DDC LDAA  0x17C8,IZ
004DE0 SUBA  0x17D8,IZ
004DE4 BCS   004DEE
004DE6 ADDA  #0x80
004DE8 BCC   004DF4
004DEA LDAA  #0xFF
004DEC BRA   004DF4
004DEE ADDA  #0x80
004DF0 BCS   004DF4
004DF2 LDAA  #0x00
004DF4 STAA  0x17DA,IZ
004DF8 LDAA  0x17D7,IZ
004DFC STAA  0x17D8,IZ
004E00 LDAA  0x17C8,IZ
004E04 STAA  0x17D7,IZ
004E08 RTS
```

**Reconstructed unsigned/saturated mathematical model:**

```c
uint16_t positive_diff = (ram081c >= ram03c8) ? (ram081c - ram03c8) : 0;
uint8_t current = (ramDC & 0x01) ? 0x0D : (uint8_t)(positive_diff >> 8);
uint8_t delta = clamp_u8(128 + (int)current - (int)ram17d8);
ram17da = delta;
ram17d8 = ram17d7;
ram17d7 = current;
```

The producer uses a **two-sample history**: `0x17D7` previous update, `0x17D8` two updates earlier. `0x17DA=0x80` is neutral; `0..127` negative and `129..255` positive change. At startup `FUN_006906` initializes `0x17D7` and `0x17D8` from `0xE6`, and `0x17D9/0x17DA` to `0x80`.

`0x17C8` is the high byte of saturated `RAM16[0x081C]-RAM16[0x03C8]` unless `RAM[0xDC]&1` overrides it with `0x0D`. **The physical meaning of 0x081C and 0x03C8 and corresponding TPS/angle scaling is not independently established.** The function also updates other working fields and hysteresis flags `0x17D2/0x17D3/0x17D6` based on calibrations `0x28673..0x28678`.

## 3. Evidence of execution: interrupt handler and divider

Searching ROM bytes `FA 00 4D 5E` yielded one raw match **0x000350**. Its range was previously marked undefined; Ghidra recognized the call after manual disassembly:

```asm
000330 JSR   FUN_013E26
000334 JSR   FUN_002658
000338 JSR   FUN_004896
00033C LDAA  0x08B1,IZ
000340 CMPA  #0x07
000342 BCC   00034C
000344 INCA
000346 STAA  0x08B1,IZ
00034A BRA   00036C
00034C CLR   0x08B1,IZ
000350 JSR   FUN_004D5E
000354 JSR   FUN_012156
000358 LDAA  0x08B2,IZ
00035C CMPA  #0x07
00035E BCC   000368
000360 INCA
000362 STAA  0x08B2,IZ
000366 BRA   00036C
000368 CLR   0x08B2,IZ
00036C BCLR  0x08,0x08A7,IZ
000370 PULM  #0x7E
000372 RTI
```

**Conclusions supported by decoded listing:** `FUN_004D5E` is called on the threshold branch of this **interrupt handler** (RTI at end), with `0x08B1` as a saturating/wrapping divider. Starting at 0 and assuming uninterrupted execution, it calls on every **8th entry** into that segment (values 0→1→...→7 then branch/reset/call). The call is conditional on reaching this handler path; its hardware interrupt source, upstream dispatch and base period **have not yet been established**. Hence **do not infer milliseconds or rate in Hz** from the divider alone.

Ghidra initially showed `0 XREF` at `FUN_004D5E` because the caller bytes at `0x000350` had not been decoded as instructions. Likewise other unnamed gaps can conceal valid code. Ghidra ROM `0x000350` and data RAM `0x17DA` are unrelated address spaces/roles even where numeric offsets overlap.

## 4. Consumer chain and reconstructed arithmetic

```asm
004E58 LDAA 0x17DA,IZ
004E5C STAA 0x17D9,IZ
...
000BE8 JSR  FUN_00A7C4
...
00A832 LDAB 0x17D9,IZ
```

`FUN_004E0A` copies the fresh `0x17DA` into `0x17D9` before `FUN_00A7C4` executes within the `FUN_000BA6` dispatcher. Whether a fresh producer update occurred immediately before this particular dispatcher invocation depends on interrupt timing.

Base Tip-in calibration:
- 18-entry axis file `0x21400..0x21411`, values `0x21414..0x21425`; identical duplicate at `0x23874..`.
- Axis `[0x80,0x84,...,0xC4]`; values `[06,0E,16,1E,26,2D,34,3C,43,4C,53,59,60,63,64,64,64,64]`.
- RPM compensation descriptor at file `0x21429`; positive boost error `0x21438`; ECT `0x21445`.
- `FUN_00850C` lookup returns packed Q8.8 values (integer A, fractional B); `FUN_00F572/00F7A2/00F6A0/0087DE` uses two curves and an interpolation coefficient from `0x1042` (written by `FUN_00F3C0`, observed 0 or 0xFFFF). Duplicate curves are identical in reference ROM.
- Under the studied unsigned fixed-point interpretation, `factor = min(65535, (rpm_raw * boost_raw * ect_raw) >> 4)`, `tip_raw = (factor * base_D) >> 16`; `tip_raw * 0.004 ms` with minimum activation raw `0x0060=96`. At neutral comp raw 0x20 each, the base value unit converts to `0.032 ms` per table step.
- A test example TPS delta `0x96` between base axis `0x94` and `0x98`: interpolated 48.5, `base_D=0x3080`, neutral raw compensation factor 2048 yields `tip_raw=388`, or 1.552 ms.
- Output `FUN_0027DC` sends requests to HC16 TPU 8–11; **do not claim physical injector firing/wiring without corroboration**.

The offline `carberry_tipin_lab_v2` Python harness passed 7 internal unit tests; it is **not an independent bit-accurate HC16 execution test**. A Forester SH7055 port must reimplement the arithmetic and validate physical scaling, scheduler interval, activation conditions, and real injector-actuator behavior.

## 5. Scripts and reports

Ghidra scripts (read-only; run on the *analyzed* CarBerry project, not an unanalysed second import):
- `FindCarBerryTipInWriter.java` (v2) — initial targeted listing diagnostics, direct references, neighboring operands.
- `CarBerryTPSDeepScan.java` (v3) — detects undecoded two-byte address signatures, raw ROM regions and indexed store candidates; emits `carberry_tps_delta_deep.txt` and `carberry_indexed_writes.csv`.
- Earlier `FindCarBerryTipInWriter.py` requires PyGhidra; ordinary Ghidra launch returned `Ghidra was not started with PyGhidra. Python is not available`. Prefer Java.

Observed reports: 31,250 initially decoded instructions, 1,026 functions, 13 direct target operands, 5,001 potential indexed writes, raw bytes in previously unanalysed `0x004D5E–0x004E09`. The huge indexed-writes CSV is an inventory **not a confirmed set of writers**. Inspect addresses/branches manually.

## 6. Open questions / next experiments

1. Trace the vector/interrupt entry leading to `0x000330`; measure its base cadence and impact of gating conditions.
2. Trace how `RAM16[0x081C]` and `RAM16[0x03C8]` are produced; derive physical coordinate scale relative to TPS signal.
3. Reconcile the precise behavior of `FUN_00850C`/signed interpolation at boundaries with a real HC16 test or emulator; add independent golden vectors.
4. Confirm TPU channel function, scheduling timing and actual injector wiring.
5. Only then prepare an isolated SH7055/MerpMod port; preserve Forester v84 BIN until tests.

**Evidence provenance:** user-supplied Ghidra asm listings for `FUN_004D5E`, dispatcher `FUN_000BA6`, `FUN_004E0A`, and interrupt range `0x000330..0x000372`; read-only report v3 and original ROM offline laboratory.

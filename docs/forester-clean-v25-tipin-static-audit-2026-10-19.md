# SH7055 Forester A2WC0MME clean v25: Tip-in static baseline (2026-10-19)

**ROM:** `Forester_SG9_MAP_clean_v25.bin` (clean v25 only; **not v84**), size 524288 bytes, SHA256 `2ca539d0c47e3b1eec96c41e1e514c7b19b0e3786e9d826a41d3a3505b4c5d99`, internal ID `A2WC0MME`. Source binary supplied directly by the user and decoded offline read-only. No ECU patches or calibration writes occurred.

## Verified bytes and layout

| Address (BIN offset) | Bytes / type | Interpretation |
|---|---|---|
| `0x58DA4` | `3E 4C CC CD`, float32 BE | 0.20; XML defines minimum Delta TPS percent |
| `0x58DA8` | `43 7A 00 00`, float32 BE | 250.0 internal units; 0.004 ms/unit per prior definition => 1.000 ms |
| `0x59B3C` | 18 float32 BE entries | Delta TPS axis |
| `0x59B84` | 18 uint16 BE entries | Base Tip-in pulse table, 0.004 ms per count per prior definition |
| `0x54910` | `00 12 08 00 00 05 9B 3C 00 05 9B 84 40 80 00 00 00 00 00 00` | Descriptor: 18 entries, axis pointer `0x59B3C`, values pointer `0x59B84`. Other descriptor bytes not yet decoded. |

### Entire base table

| Delta TPS (%) | raw | pulse (ms) |
|---:|---:|---:|
| 0.40 | 33 | 0.132 |
| 0.98 | 75 | 0.300 |
| 1.95 | 115 | 0.460 |
| 3.91 | 158 | 0.632 |
| 5.86 | 243 | 0.972 |
| 7.81 | 284 | 1.136 |
| 9.77 | 325 | 1.300 |
| 11.70 | 374 | 1.496 |
| 13.70 | 422 | 1.688 |
| 15.60 | 478 | 1.912 |
| 17.60 | 534 | 2.136 |
| 19.50 | 590 | 2.360 |
| 21.50 | 646 | 2.584 |
| 23.40 | 695 | 2.780 |
| 25.40 | 766 | 3.064 |
| 27.30 | 838 | 3.352 |
| 29.30 | 908 | 3.632 |
| 31.30 | 978 | 3.912 |

### Candidate SH7055 literal pool (not yet code XREF-confirmed)

Scanning the entire v25 ROM for big-endian 32-bit address literals yields unique locations:

- `0x24BAC`: `00 05 8D A4` -> minimum Delta TPS threshold.
- `0x24BBC`: `00 05 49 10` -> base table descriptor.
- `0x24BCC`: `00 05 8D A8` -> minimum Tip-in pulse threshold.

All three are clustered, providing a **concrete SH7055 disassembly target**. A code reference to each constant, the enclosing runtime function, gate conditions, and actual fuel actuator behavior **remain unknown**.

## Interpretation and next step

The previously hypothesized 1.000-ms minimum threshold vs 0.384-ms CarBerry threshold is an important calibration distinction, but the static table cannot prove that an enrichment event is delivered/cancelled: the OEM SH7055 runtime gate, compensations, elapsed-time conditions, and injector output path have not yet been recovered.

At 5.86% Delta TPS the **base uncorrected** table reads 0.972 ms (below 1.000-ms nominal threshold); at 7.81% it reads 1.136 ms (above nominal). This is a potential, **not confirmed**, transition region and is subject to runtime compensations and activation rules.

**Next reverse-engineering job:** disassemble the region responsible for references to literal-pool offsets `0x24BAC`, `0x24BBC`, `0x24BCC`, trace throttle Delta and minimum pulse gates, and identify if/where extra injection is scheduled. If hardware logs are available, compare matched warmed throttle-step events including TPS, RPM, MAP, commanded lambda, wideband lambda, injection PW, IAT and ECT. Only then consider an isolated reversible threshold experiment. Do not attempt an unvalidated code port or direct CarBerry byte patch.

Offline extractor with SHA verification and full decoded table was produced as a downloadable artifact in this conversation. Source v25 and v84 were unchanged.


## Addendum 2026-10-19: OEM SH7055 Delta TPS producer and call graph

**Evidence:** user-supplied Ghidra SH-2A/FPU disassembly plus direct read-only verification of the exact Forester clean v25 ROM (524288 bytes, SHA256 listed above). SH7055's SH-2E/FPU architecture is not identical to Ghidra's provisional SH-2A decoder. Ghidra previously misclassified active instructions as float data and literal-pool words as MOVI20 code. Verify code/data boundaries; no BIN writes or ECU flash occurred.

### Delta TPS producer: 0x171C6

~~~asm
171C6 7F FC   ADD    #-4,R15
171C8 96 36   MOV.W  @(PC),R6       ; literal B02C => RAM FFFFB02C
171D0 E5 02   MOV    #2,R5
171D6 75 FF   ADD    #-1,R5
171D8 F3 48   FMOV.S @R4,FR3
171DC F7 3B   FMOV.S FR3,@-R7
171E0 8D F9   BT/S   171D6
171E2 74 FC   _ADD   #-4,R4        ; branch delay slot
171E4 94 27   MOV.W  @(PC),R4      ; literal B024
171E8 93 27   MOV.W  @(PC),R3      ; literal B028
171EA F3 48   FMOV.S @R4,FR3      ; read current TPS
171EC F6 3A   FMOV.S FR3,@R6      ; save current to B02C
171EE F3 66   FMOV.S @(R0,R6),FR3 ; R0=8 => history B034
171F0 F2 48   FMOV.S @R4,FR2      ; current
171F2 F2 31   FSUB   FR3,FR2     ; current minus historical
171F4 F3 2A   FMOV.S FR2,@R3      ; write B028 Delta TPS
171F6 00 0B   RTS
~~~

RAM layout: B024=current TPS; B028=Delta TPS; B02C/B030/B034=history Float32. The loop shifts B030→B034 and B02C→B030, saves current B024→B02C and computes B028=B024−B034. If called once per TPS update, that history corresponds to TPS[n]−TPS[n−2]. The *elapsed time* of the comparison window is not yet known.

### Confirmed call at 0x170F6 and upstream chain

Reading the raw v25 bytes confirms a SH relative branch-and-subroutine:

~~~asm
170F6 B0 66  BSR 0x171C6  ; target = 0x170F6+4+(0x066*2)
170F8 00 09  NOP
~~~

An aligned ROM opcode scan identified this BSR, while a literal 32-bit big-endian search for 00 01 71 C6 found zero matches. Hence the 0 XREF count in partially disassembled Ghidra was a false negative.

Observed caller chain with PC-relative literal targets:

~~~text
0x6330 routine
  0x634A MOV.L literal @0x63D4 = 0x1028C ; JSR via register
0x1028C routine
  0x10372 MOV.L literal @0x10570 = 0x170E8 ; JSR via register
0x170E8 routine
  0x170F6 BSR 0x171C6
0x171C6 Delta TPS history update and write -> RAM 0xFFFFB028
~~~

This **does not establish a frequency** for the 0x6330 dispatcher or whether every entry reaches this path. Determine scheduling, gate conditions and period before assigning milliseconds.

### OEM Tip-in consumer and gate

User-supplied FPU disassembly establishes:
- 0x24A22 loads float32 RAM B028 into FR15 as Delta TPS, used as base lookup argument at 0x24AE6.
- 0x24A9C..0x24AA4 loads 0x58DA4 (float 0.20) and returns early if Delta TPS is below that threshold.
- Additional early exits include 0x24AB0 (RAM B818 versus calibration 0x58852=7), 0x24AB8 (local byte), 0x24ACA (RAM B469 bit 0x80, unknown meaning), 0x24AD8 (float 0x58DAC=23.0 versus RAM B814).
- 0x24AE2..0x24AE6 calls lookup 0x209C with base table descriptor 0x54910 and FR15 argument, returning FR0, copied to FR14.
- 0x24AF8..0x24AFC uses table descriptor 0x5455C with RAM AF08 minus RAM AF94.
- 0x24B00..0x24B06 uses descriptor 0x54924 with RAM B090.
- 0x24B12..0x24B16 multiplies base by both table compensation results and stores result at RAM B80C.
- 0x24B18..0x24B20 checks float32 250.0 at 0x58DA8; if final result is below 250, branches to function epilogue at 0x24B5C. Equality passes this gate.
- 0x24B22..0x24B5A includes subsequent state updates and calls to 0x3980, 0xD754, 0x3994 and 0x24D8. Injector firing is **not yet proven**.

The XML's 0.004 ms/raw conversion makes 250 equal to a nominal 1.000 ms threshold, but confirm units at the intermediate float and real injection actuation stage before claiming 1.000 ms is actually delivered.

### CarBerry comparison and next work

CarBerry 4.2 forms a saturated 8-bit difference about neutral 128 using a two-update-old internal sample. Forester v25 forms a float32 subtraction between the current TPS and two-update-old history in B028. Thus the history-depth **appears equivalent**, but physical TPS scaling, tick cadence, gate logic, compensation curves, actual injector event and timing **remain unverified**. CarBerry uses a divide-by-8 path from an interrupt handler with unknown base cadence; Forester Delta TPS is downstream of 0x6330 with unknown cadence.

Next: trace scheduler/periodic source of 0x6330; characterize both compensation descriptors 0x5455C/0x54924; investigate actuator calls 0xD754/0x3980; gather matched throttle-step logs to test hypotheses. Do not modify or flash clean v25 until the relevant actuator, math and A/B tests are validated.


## Quantitative calibration comparison (2026-10-19, clean v25)

Decoded directly from original bytes, descriptor encoding: 0x04 has uint8 ordinate; 0x08 has uint16 ordinate; float32 big-endian multiplication scalar at descriptor +0x0C. This gives:

| Descriptor | Axis pointer | Value pointer | 1D table | Ordinate factor |
| --- | --- | --- | --- | --- |
| 0x54910 | 0x59B3C | 0x59B84 | 18 TPS-delta points | uint16 * 4.0 (internal tip-in units) |
| 0x5455C | 0x59318 | 0x5933C | 9 boost-error/difference points | uint8 * 1/128 |
| 0x54924 | 0x58F14 | 0x59BA8 | 16 temperature points | uint16 * 1/8192 |

**Boost-error compensation:**
axis values (float32 BE) = [0,64,128,192,256,320,384,448,512]; 9 uint8 BE values = [64,64,128,128,128,128,128,128,128], so compensation = [0.5,0.5,1,1,1,1,1,1,1]. The code feeds this table with the difference RAM FFFFAF08 minus RAM FFFFAF94. Units of that difference are not independently established.

**Temperature compensation:**
axis (°C) = [-40,-30,-20,-10,0,10,20,30,40,50,60,70,80,90,100,110].
Raw uint16 ordinates = [29950,27460,25166,22872,20382,18153,15991,14025,12321,10748,9699,8716,8192,8192,8192,8192], each divided by 8192. Selected ratios: -40 °C=3.656, 20 °C=1.952, 40 °C=1.504, 60 °C=1.184, 70 °C=1.064, >=80 °C=1.000. RAM B090 is the actual input; check external definition to confirm its physical temperature units before relying on °C labels.

**New evidence: the actual 0x209C scale instruction was found in a Ghidra dump (2026-10-19).** At 0x209C the generic table lookup calls helper 0x2684, selects a type-specific lookup function via a byte offset in the table descriptor, and then executes the following *only when returned R3 != 0*:

~~~asm
020B6  TST   R3,R3
020B8  BT/S  020C4
020BC  ADD   #12,R4
020BE  FMOV.S @R4+,FR0      ; descriptor +0x0C Scale
020C0  FMOV.S @R4,FR1       ; descriptor +0x10 Offset
020C2  FMAC  FR0,FR2,FR1    ; FR1 = Offset + Scale * FR2
020C8  FMOV  FR1,FR0       ; returned float result
~~~

Thus **the scale math itself IS now confirmed**: when R3 != 0, Result = Offset + Scale * lookup_FR2. For descriptor 0x54910, Scale=4.0 and Offset=0. We still need to establish R3 return conditions from handler 0x2730 (descriptor byte+2 = 0x08, dispatch table 0x20CC + 8), and what the typed lookup returns in FR2 for this table (raw vs normalized). Be careful: Ghidra's decompiler output shows a simplified indirect call and cannot alone prove the value of R3 in every normal lookup.

Conditional scenario only — assuming active scale branch, raw uint16 value returned in FR2, and both compensation results 1.0, gate250/4 => raw62.5, which interpolates at about **0.807%** Delta TPS (between 0.40%,raw33 and 0.98%,raw75). At hypothetical gate150/4 => raw37.5, about **0.462%** Delta TPS. These numbers replace the previously proposed 6.19% and 3.55% *under this new conditional model*; they are not hardware-confirmed. With another boost compensation (e.g. 0.5), they differ accordingly.

Critical nuance: these modeled differences indicate that modifying gate250→150 may have a much smaller or different effect than previously suggested. Do not recommend a flash-ready reduction until R3 branch behavior, typed 0x2730 lookup units, and physical injector scheduling are validated.

**Provisional engineering choice:** Evaluate a single reversible clean-v25 parameter experiment at nominal 0.600 ms (float32 150.0 BE = 43 16 00 00 at ROM 0x58DA8; clean baseline 250.0 BE = 43 7A 00 00), *only* after confirming table-to-runtime units, injector scheduler, checksum correction and safety test/logging plan. Do **not** apply as a flash-ready patch solely on this static analysis; also avoid direct adoption of CarBerry 0.384 ms gate because actuator implementation and timing are different/unverified. The aim is to retain OEM logic and change only minimum threshold if evidence supports it. No ROM bytes have been changed in the repository.

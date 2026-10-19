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

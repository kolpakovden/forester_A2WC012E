# A2WC012E Launch Control — Advanced LC / Spark Cut

Этот документ фиксирует текущую ветку исследования launch control для **Subaru Forester STI SG9, JDM / RHD**, ROM family **A2WC012E**, patched internal ID **A2WC0MME**.

Все адреса ниже относятся к этому ROM/patch и не должны автоматически переноситься на другие Subaru ROM ID.

## Статусы

- ✅ **CONFIRMED** — подтверждено binary inspection и/или логом автомобиля.
- 🧪 **EXPERIMENTAL** — код собран и структурно проверен, но результат ещё требует vehicle validation.
- 📚 **REFERENCE** — источник/ориентир из MerpMod source/definition.

## Advanced LC — подтверждённая база

Для текущей ветки используются существующие MerpMod launch-control state/limits и отдельные mini-hooks для топлива/угла.

Подтверждённые точки:

```text
LCEngaged RAM:              0xFFFFCA3B
RevLim Active Cut RPM:      0xFFFFCA44
RevLim Active Resume RPM:   0xFFFFCA48
RedLine Cut RPM:            0xFFFFCA4C
pFlagsRevLim:               0xFFFFB868
pPolfEnrich:                0xFFFFB6E8
pBaseTiming:                0xFFFFB9F8
pEngineSpeed:               0xFFFFB218

OEM POLF routine:           0x000228C4
POLF call pointer:          0x0001132C
OEM Base Timing routine:    0x00028AF8
Base Timing call pointer:   0x000113D8
```

Advanced-LC calibration block:

```text
0x6AD78  LC Advanced Fuel Mode
0x6AD7C  LC Advanced Fuel Target
0x6ADB8  LC Advanced Timing Mode
0x6ADBC  LC Advanced Base Timing Lock
0x6ADC4  LC Cut Mode
0x6ADC8  LC Spark Events Cut
0x6ADCC  LC Spark Event Cycle
```

### Timing observation

Vehicle logs confirmed that changing `Base Timing Lock` changes the pre-limiter timing, but the logged `Ignition Total Timing` is not guaranteed to equal the lock value after all downstream timing logic. A comparison around `-2°` vs `-5°` Base Timing Lock did not produce a meaningful spool improvement, so the current branch returned to `-2°`.

## v68 — experimental spark-cut path

Files are stored under `roms/experimental/v68/`.

Main test artifact:

```text
forester_sg9_sti_MAP_IAT_GM_dMap_v68_SPARK_CUT_ENABLED.bin
SHA256 8f02eecf37fad5340baf0ba5d66e62308a979660b4926c6ad0559fc53f869ecc
LC Cut Mode: 1
Spark pattern: 3/5
```

Matching SAFE artifact keeps the new hooks installed but uses `LC Cut Mode = 0`.

### ✅ CONFIRMED — vehicle result of v68 enabled

The user explicitly confirmed that `romraiderlog_20260902_001107.csv` was recorded with the **v68 enabled / LC Cut Mode = 1** build.

In that log:

- launch RPM is roughly `4.4–4.6k rpm`;
- MAP rises from about `1.12 bar absolute` near limiter entry to a peak of about `1.93 bar absolute`;
- injector pulse width repeatedly alternates between normal/high values and about `0.77 ms`;
- logged total timing on the limiter is around `+3…+4°` in the sampled rows;
- coolant temperature in that test was only about `61°C`, so it is not a preferred thermal baseline for repeated testing.

The critical confirmed fact is that **fuel cut was still present** with v68 mode 1 because injector pulse width continued dropping to ~`0.77 ms`.

The large spool increase strongly indicates changed limiter behaviour, but the log did not contain a direct spark-cut-active channel, so the exact per-event spark suppression must not be claimed from that log alone.

## v69 — Clean Spark Cut

Status: **🧪 EXPERIMENTAL / awaiting vehicle validation**.

Base:

```text
v68 SPARK_CUT_ENABLED
SHA256 8f02eecf37fad5340baf0ba5d66e62308a979660b4926c6ad0559fc53f869ecc
```

Main v69 artifact:

```text
forester_sg9_sti_MAP_IAT_GM_dMap_v69_CLEAN_SPARK_CUT.bin
SHA256 02581366d410326102c8ca7ffe7f483e2b1ecdc1f7363cd8a7eac663c8d6e4aa
LC Cut Mode: 1
Spark pattern: 2/5
```

Fallback artifact:

```text
forester_sg9_sti_MAP_IAT_GM_dMap_v69_CLEAN_SPARK_SAFE.bin
SHA256 b3bb642372636c7abb312e7659f91ad4e69d683afe0a2d4d681eb3a405715ec2
LC Cut Mode: 0
```

SAFE and CLEAN differ by the mode byte; both contain the v69 wrapper.

### v69 clean-spark logic

The v68 POLF-time fuel-cut flag clear was insufficient. v69 therefore changes the active MerpMod limiter thresholds **only while LC is engaged and clean-spark mode is selected**:

```text
RevLimCut    0xFFFFCA44 <- RedLineCut 0xFFFFCA4C
RevLimResume 0xFFFFCA48 <- RedLineCut 0xFFFFCA4C
```

It also clears the rev-limit fuel-cut bit `0x80` in `pFlagsRevLim @ 0xFFFFB868` below the normal RedLineCut.

The spark scheduler continues to use the existing launch-control RPM threshold. The normal high-RPM redline calibration/logic is not removed and remains the hard fuel-cut protection.

v69 also reduces the initial spark suppression pattern from `3/5` to `2/5` because the mixed-cut v68 test already reached ~`1.93 bar absolute`.

### Binary diff summary — v68 enabled → v69 clean

```text
POLF wrapper pointer: 0x1132C  0x0006AE00 -> 0x0006B000
LC Spark Events Cut:  0x6ADC8  3 -> 2
new clean wrapper:    0x6B000...
changed bytes:        108
```

Preserved byte-for-byte from v68 where expected:

- DeltaMAP block `0x6AC40–0x6AD43`;
- OCR/GR ignition hook sites;
- OCR/GR custom spark routines;
- Advanced LC fuel target;
- Base Timing Lock `-2°`;
- MerpMod revlim code `0x25758–0x2583F`;
- normal RedLine Cut calibration.

## v69 logger channels

Latest logger definition adds:

```text
A2WC0MME LC Spark Cut Active    @ 0xFFCA78
A2WC0MME LC Spark Event Counter @ 0xFFCA79
```

Also log `MerpMod RevLimit Active Cut RPM @ 0xFFCA44` if available.

## Expected v69 validation signature

For a short, fully-warmed clean-spark test:

1. `LC Engaged` activates normally.
2. Active `RevLimCut` should move to normal `RedLineCut` instead of staying at launch RPM.
3. Injector pulse width should **stop cycling to ~0.77 ms because of the LC limiter**.
4. `LC Spark Cut Active` / event counter should show the configured spark-event pattern.
5. RPM should still be controlled around launch RPM by the spark path.
6. MAP/spool should be compared against v68, but not at the cost of excessive launch duration or thermal load.

If IPW still falls to ~`0.77 ms`, clean fuel-cut suppression is not yet complete and the exact downstream cut path must be traced before increasing retard/fueling aggressiveness.

## Flashing / safety

These are experimental ECU binaries, not universal tunes.

- Generated patch BIN checksum is not recalculated by the builder.
- Before flashing, open and **save** the selected BIN in EcuFlash so `subarudbw` recalculates checksum.
- Keep a known-working rollback ROM available.
- First clean-spark tests should be short and done only with engine/oil fully warmed.
- Spark cut / late combustion can raise exhaust-manifold, turbine and catalyst/exhaust thermal load very quickly.

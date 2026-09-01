# v69 — Clean Spark Cut LC

Status: **EXPERIMENTAL / AWAITING VEHICLE VALIDATION**.

Base:

- v68 `SPARK_CUT_ENABLED`
- SHA256 `8f02eecf37fad5340baf0ba5d66e62308a979660b4926c6ad0559fc53f869ecc`

Artifacts:

- `forester_sg9_sti_MAP_IAT_GM_dMap_v69_CLEAN_SPARK_CUT.bin` — mode 1; SHA256 `02581366d410326102c8ca7ffe7f483e2b1ecdc1f7363cd8a7eac663c8d6e4aa`.
- `forester_sg9_sti_MAP_IAT_GM_dMap_v69_CLEAN_SPARK_SAFE.bin` — mode 0 fallback; SHA256 `b3bb642372636c7abb312e7659f91ad4e69d683afe0a2d4d681eb3a405715ec2`.

Initial spark pattern: **2 cut events / 5 total**.

## What changed

v68 mode 1 changed launch behaviour strongly, but fuel cut still appeared in the vehicle log. v69 therefore changes the active MerpMod limiter thresholds only while `LC Engaged && LC Cut Mode == 1`:

```text
RevLimCut    @ 0xFFFFCA44 <- RedLineCut @ 0xFFFFCA4C
RevLimResume @ 0xFFFFCA48 <- RedLineCut @ 0xFFFFCA4C
```

The wrapper also clears the already-latched rev-limit fuel-cut bit `0x80` in `pFlagsRevLim @ 0xFFFFB868`. The separate ignition scheduler continues to use the configured Launch Control RPM as its spark-cut threshold.

Normal high-RPM RedLine fuel-cut protection is retained.

## Validation log

For the first short, fully warmed test log:

- RPM
- MAP absolute
- throttle
- Injector Pulse Width
- Ignition Total Timing
- Final Fueling Base
- Wideband AFR
- LC Engaged
- `A2WC0MME LC Spark Cut Active @ 0xFFCA78`
- `A2WC0MME LC Spark Event Counter @ 0xFFCA79`
- `MerpMod RevLimit Active Cut RPM @ 0xFFCA44`, if available

Expected clean-spark signature: active cut RPM moves to normal RedLine, IPW no longer cycles to ~`0.77 ms` because of the launch limiter, while spark flag/counter confirms the 2/5 event pattern.

Before flashing generated BINs, open/save in EcuFlash so `subarudbw` recalculates checksum.

# v68 — Experimental LC Spark Cut

Status: **EXPERIMENTAL / VEHICLE TESTED**.

Base ROM:

- `forester_sg9_sti_MAP_IAT_GM_dMap_v67.bin`
- SHA256 `57cc8860190c15b74b8e7dbbf3bd9bf529f85a2df97d00df0fd73cbe1eedb17a`

Artifacts:

- `forester_sg9_sti_MAP_IAT_GM_dMap_v68_SPARK_CUT_SAFE.bin` — mode 0 / original fuel-cut LC; SHA256 `b9da808571b17bcd38bae71c6949c3da6d7ebcc2e17759abded1e6c1c0766466`.
- `forester_sg9_sti_MAP_IAT_GM_dMap_v68_SPARK_CUT_ENABLED.bin` — mode 1 / experimental spark path; SHA256 `8f02eecf37fad5340baf0ba5d66e62308a979660b4926c6ad0559fc53f869ecc`.

Initial spark pattern: **3 cut events / 5 total**.

## Vehicle result

`romraiderlog_20260902_001107.csv` was explicitly confirmed to have been recorded with v68 ENABLED (`LC Cut Mode = 1`).

Observed around launch limiter:

- RPM about `4.4–4.6k`;
- MAP rose to about `1.93 bar absolute`;
- Injector Pulse Width repeatedly fell to about `0.77 ms` between normal/high-IPW samples;
- therefore the launch fuel-cut component was still active in parallel;
- logged final ignition timing in part of the limiter region was about `+3…+4°`;
- coolant temperature in this test was about `61°C`, so this run is evidence of limiter behaviour, not a preferred thermal baseline.

Conclusion: v68 is useful vehicle evidence, but it is **not Clean Spark Cut**. It motivated v69.

Before flashing generated BINs, open/save in EcuFlash so `subarudbw` recalculates checksum.

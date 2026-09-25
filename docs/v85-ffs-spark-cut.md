# v85 FFS Spark Cut

Status: **EXPERIMENTAL / awaiting vehicle validation**

Base ROM: `forester_sg9_sti_MAP_IAT_GM_dMap_v84_AF_off.bin`  
Base SHA256: `30b1994039775bbef362bcd166d6fcfbde3d618585115a7a44edeb53f3bae278`

Output: `forester_sg9_sti_MAP_IAT_GM_dMap_v85_FFS_SPARK_CUT.bin`  
Output SHA256: `61e7802c2f6594ccc8046c72c0fbd1d31fdbec62c79dfc3a900bf0b19d3f6d57`  
Internal ID: `A2WC0MME`  
Size: 524288 bytes

## Purpose

The old FFS path reaches the common MerpMod rev limiter and sets `pFlagsRevLim bit 0x80`, producing fuel cut. Vehicle behavior showed this is undesirable for the intended full-throttle shift strategy.

v85 keeps MerpMod's FFS target-RPM calculation, but uses that target for ignition-event suppression while preventing the lower FFS threshold from becoming fuel cut. The normal hard redline remains fuel-cut protection.

## Runtime design

- `FFSEngaged @ 0xFFFFCA3C`; active FFS state is value 2.
- Original FFS `RevLimCut/Resume` are preserved in `0xFFFFCA7C/0xFFFFCA80`.
- Active limiter thresholds are moved to hard redline while FFS is active.
- OCR spark scheduler uses the preserved FFS target.
- Initial spark pattern is 2 cut events per 5-event cycle.
- LC remains a separate condition.
- OEM/Merp RevLimiter code `0x25758-0x2583F` remains byte-for-byte unchanged.

## Reproducibility

Use `tools/materialize_v85_ffs_spark_cut.py` with the exact v84 base. The script validates input size, internal ID, base SHA256 and final output SHA256.

## First vehicle test

Test only with fully warmed engine/oil and a short shift. Log RPM, throttle, clutch/FFS state, Injector Pulse Width, AFR/lambda, ignition timing, FBKC/FKL/knock, active RevLimCut and spark-cut flag/counter.

Primary acceptance check: during FFS, Injector Pulse Width should no longer repeatedly fall toward approximately 0.77 ms as observed with the previous fuel-cut behavior. Hard-redline fuel cut must still function independently.

## Checksum

The patch materializer does not recalculate Subaru DBW checksum. Open/save the generated ROM with EcuFlash/subarudbw before flashing.

Do not mark this version CONFIRMED until the vehicle log is reviewed.

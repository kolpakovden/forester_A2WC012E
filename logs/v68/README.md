# v68 vehicle log

ROM:
- `forester_sg9_sti_MAP_IAT_GM_dMap_v68_SPARK_CUT_ENABLED.bin`
- SHA256 `8f02eecf37fad5340baf0ba5d66e62308a979660b4926c6ad0559fc53f869ecc`

Log:
- `romraiderlog_20260902_001107.csv`

Confirmed test configuration:
- `LC Cut Mode = 1`
- spark pattern `3/5`

Observed:
- MAP reached about `1.93 bar absolute`;
- Injector Pulse Width still repeatedly fell to about `0.77 ms` in the limiter region;
- therefore v68 mode 1 still had the launch fuel-cut component active alongside the experimental spark-cut path.

Status: **EXPERIMENTAL / vehicle-tested evidence**.

This log is the reason v69 Clean Spark Cut was created.

# v46 — Current v39 foundation and CarBerry port constraints

Source image SHA256 `43a4751d68da4ddca9d483c1723a78f04c85ad982423f48177402f9962245ad4` (512KiB, A2WC0MME). User reports v39 currently installed; ECU read not available to confirm.

Offline comparison: 1650 differences from clean v25. OEM Tip-in pointer remains 0x24A04. Neutral v45 on v39 differs by exactly 19 bytes (3 pointer, 12 wrapper, 4 checksum) and has no CarBerry functionality. No flash clearance.

Calibration change already on v39: big-endian float32 threshold at 0x58DA8 is **25.0**, versus **250.0** on v25. Tip-in table at 0x59B84 begins U16 values v25 33,75,115,158,243,284; v39 **25,56,86,124,191,224**. Do not overwrite live calibrations with v25 values.

CarBerry source HC16 160KiB SHA256 `b06e1282a4b274db856d250ae8a1babaf175729f7f9e9fec12e465fb774a4483`. Existing fixed-point model describes 18-node base lookup and RPM / boost error / ECT compensation, but its physical units, TPS delta encoding, scheduling and signed interpolation are **not yet proved from independent traces**. Existing C/Python agreement is model-to-model, not hardware validation.

Next: trace CarBerry writer/reader around RAM 0x17D9 and Subaru TPS history near 0x171C6 into 0x24A04, derive comparable physical delta units and sampling intervals; retain stock Subaru activation/scheduling. Do **not** issue active CarBerry BIN before ABI/pulse-duration and safety checks.

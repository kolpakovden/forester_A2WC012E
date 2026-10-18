# CarBerry Tip-in offline reference model

These are **new consolidated research helpers** reflecting the October 19 delta-producer discovery. Earlier chat artifacts (`carberry_tipin_lab_v2.zip`, original `tipin_math.py`, and tests) were produced separately; this folder is not a claim to reproduce the older ZIP byte-for-byte.

```bash
python -m unittest discover -s tools/carberry-tipin-lab -p "test_*.py" -v
```

Contents: `carberry_tipin_math.py` models 2-sample, neutral-128 input Delta, base table Q8.8 increasing-axis interpolation and three compensation factors; `test_tipin_math.py` tests boundaries and examples.

Evidence and remaining caveats: [Delta/interruption research](../../docs/carberry-tipin-delta-interrupt-2026-10-19.md). The tests **do not prove full ECU equivalence**. Check sensor physical scaling, interrupt cadence, negative slope rounding and TPU actuation before considering any SH7055 patch.

Do not commit proprietary/full ECU BINs just to make this script run. Model examples are self-contained.

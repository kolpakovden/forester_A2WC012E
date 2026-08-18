# MAF Scaling 11 — validation evidence

## ROM diff

```text
ROM size:             524288 bytes → 524288 bytes
MAF Voltage offset:   0x5E538 → unchanged
MAF Flow offset:      0x5E610
MAF points:           54
Changed MAF points:   20
Changed ROM bytes:    57
Bytes outside MAF:    0
```

```text
Source SHA-256:
62ac1b5666c297480cead4a4ddcada5c1d6894590c33dbdeee731e26a645e2d8

Result SHA-256:
6279f5502ec053e73df472ef9720f9317831c648efd5b079e4c274c85c8c02a9
```

## Связанные файлы

```text
Source ROM: forester_sg9_sti_MAF_Scaling_10.bin
Result ROM: forester_sg9_sti_MAF_Scaling_11_CL_full.bin
Log:        romraiderlog_20260803_182839.csv
```

## Log coverage

```text
Useful duration:        ~41.5 min
Stable CL rows:          >7000
Stable CL MAF range:     ~1.25–2.66 V confidently covered
Upper CL sparse region:  ~2.66–2.89 V
No usable CL samples:    ~3.0 V and above
```

## Stable CL filter

```text
CL/OL status:                    8 = Closed Loop
ECT:                             85–105 °C
Continuous CL:                   ≥ 0.5 s before and after row
MAF Voltage rate:                ≤ 0.20 V/s
Throttle rate:                   ≤ 3 %/s
RPM rate:                        ≤ 250 rpm/s
|A/F Correction|:               ≤ 15 %
Battery voltage:                 ≥ 13 V
```

Combined trim:

```text
(1 + A/F Correction / 100)
× (1 + A/F Learning / 100)
- 1
```

## Итог

Основная отрицательная коррекция находилась примерно в зоне `1.25–2.03 V`. В диапазоне около `2.11–2.77 V` MAF уже был существенно ближе к нулю, поэтому применялись небольшие изменения/сглаживание. OL-часть выше примерно `3.0 V` этим логом не калибровалась.

Отдельно отмечалось повторяющееся FBKC на частичной нагрузке примерно `2300–2500 rpm`; этот вопрос не лечился MAF-таблицей и должен анализироваться отдельно.

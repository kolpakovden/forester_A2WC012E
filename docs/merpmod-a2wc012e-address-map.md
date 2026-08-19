# MerpMod / A2WC012E — reference address map

Эта карта собрана из target-файлов MerpMod для **A2WC012E** и наших проверок сборки.

> По умолчанию записи ниже имеют статус **REFERENCE**. Они полезны для reverse engineering и разработки patch, но не должны автоматически считаться подтверждёнными калибровочными offsets RomRaider.

## Идентификация и память

```text
ECU_CALIBRATION_ID   A2WC012E
ECU_IDENTIFIER       3B02594316
MOD_ECUID             8FBBFF9B0D

dCalId               0x00002000
dEcuId                0x0005F004
dRomHoleStart         0x00069C10
pRamHoleStart         0xFFFFCA00
sPull2DFloat          0x0000209C
sPull3DFloat          0x00002110
```

### ROM hole

`0x00069C10` имеет повышенный уровень доверия: этот же адрес присутствует в A2WC012E target header и используется как начало patch в существующем `A2WC012E.MeRpMoD.Gratis.Testing.v13.5.6.212.patch`.

Статус:

```text
dRomHoleStart 0x00069C10 — SOURCE-CORROBORATED
```

Это **не означает**, что вся область после `0x69C10` свободна для произвольной записи: границы конкретной сборки и размещение секций всё равно нужно проверять по linker map/S-record.

## Switch / startup references

```text
tTipInEnrich          0x00054910
tStartupEnrich2_2A    0x00054674
```

## Rev Limit Hack

```text
hRevLimDelete         0x00011310
sRevLimStart          0x00025758
sRevLimEnd            0x0002578E
pFlagsRevLim          0xFFFFB868
RevLimBitMask         0x80
```

## Speed Density / MAF hook

```text
hMafCalc              0x000077B4
sMafCalc              0x00007758
```

Эти адреса используются MerpMod как точки вмешательства в расчёт MAF/Speed Density. Перед переносом логики в собственный patch проверять инструкции вокруг hook и calling convention.

## Injector reference

```text
dInjectorScaling      0x000589B0
```

Этот адрес совпадает с известным кандидатом `Injector Flow Scaling` из A2WC012E definition. Само совпадение двух источников повышает доверие, но статус прямой калибровочной правки должен фиксироваться отдельно в основной карте ROM.

## CEL hooks

```text
sCelTrigger           0x0004C4FC
hCelSignal            0x0004C614
pCelSignalOem         0xFFFFC692
```

## WGDC hooks

```text
hWgdc                 0x00010FF8
sWgdc                 0x00013350
```

## Primary Open Loop Fueling hooks

```text
pPolf4Byte            0xFFFFB6E8
tPolf                 0x00054A90
pPolfEnrich           0xFFFFB6E8
```

## Timing runtime pointers

```text
pBaseTiming           0xFFFFB9F8
pKcaIam               0xFFFFBB60
```

Это runtime RAM pointers, а не адреса calibration tables `Base Timing` / `KCA Max` в BIN.

## Clutch flag

```text
pClutchFlags          0xFFFFB1E9
ClutchBitMask         0x80
```

Полезно для исследования launch control / flat-foot shifting, но назначение конкретного bit должно подтверждаться поведением и кодом.

## Runtime engine parameters

```text
pFbkc1                        0xFFFFB364
pFbkc4                        0xFFFFBB1C
pIam1                         0xFFFFB369
pIam4                         0xFFFF822C
pEngineSpeed                  0xFFFFB218
pVehicleSpeed                 0xFFFFB208
pCoolantTemp                  0xFFFF90C8
pAtmoPress                    0xFFFF9134
pDeltaMap                     0xFFFFAF88
pManifoldAbsolutePressure     0xFFFFAF94
pIntakeAirTemp                0xFFFF90B8
pMassAirFlow                  0xFFFF90F4
pMafSensorVoltage             0xFFFF9022
pEngineLoad                   0xFFFFB0E0
pThrottlePlate                0xFFFFB024
pCurrentGear                  0xFFFFB319
```

### Особо важная пара для dMAP

```text
pDeltaMap     0xFFFFAF88
pEngineSpeed  0xFFFFB218
```

Эта пара сейчас используется в экспериментальной работе над отдельной Delta MAP compensation table.

## Load smoothing

```text
dLoadSmoothingA        0x0005774C
dLoadSmoothingB        0x00057750
dLoadSmoothingFinal    0x00057754
```

Интересно, что эти значения лежат сразу после известного `MAF Limit (Maximum) 0x57748`. Это полезный ориентир при исследовании соседней airflow/load logic, но назначение каждого параметра нужно проверять отдельно.

## Memory reset

```text
sMemoryReset           0x0000F280
hMemoryReset           0x0000CC84
pMemoryResetLimit      0xFFFFDFFB
hMemoryResetLimit      0x0000F468
```

## Текущая конфигурация Gratis, которую мы исследовали

В `Gratis.h`:

```text
MEMORY_HACKS  1
SD_HACKS      1
REVLIM_HACKS  1
SPARK_HACKS   0
CEL_HACKS     0
BOOST_HACKS   0
```

В `EcuHacks.h` также присутствовали:

```text
WGDC_MAIN_HOOK 1
POLF_MAIN_HOOK 1
```

При анализе patch нельзя делать вывод о реально активной функции только по имени исходника: нужно смотреть итог препроцессора, linker map и S-record.

## 🧪 Delta MAP Mini — текущая экспериментальная ветка исследования

Для проверки отдельной компенсации был подготовлен standalone-вариант `DMapMini`:

```text
Columns (Delta MAP): 0, 333, 666, 1000, 1333, 1666, 2000
Rows (RPM):          500, 800, 1000, 1200, 2000, 3000, 6000
Cells:               7 x 7
Initial value:       16384 ≈ 1.0
Multiplier:          0.000061037
Pull3D:              0x00002110
Delta MAP RAM:       0xFFFFAF88
Engine Speed RAM:    0xFFFFB218
```

Логика тестовой функции:

```text
DMapApply(sdmaf) = sdmaf × DMapComp(DeltaMAP, RPM)
```

Статус: **EXPERIMENTAL**. Нейтральная таблица и сборка сами по себе ещё не подтверждают корректность hook, единиц `Delta MAP`, RAM lifetime или поведения на автомобиле.

## Как повышать статус адреса

Для каждого REFERENCE address желательно иметь хотя бы одно независимое подтверждение:

- совпадение с полным A2WC012E BIN/definition;
- дизассемблирование вызова/обращения;
- binary diff известного рабочего patch;
- runtime log/read;
- подтверждённое изменение поведения при одной контролируемой правке.

До этого target header используется как **карта для исследования**, а не как инструкция «писать по этому адресу».

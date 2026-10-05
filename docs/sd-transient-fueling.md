# SD transient fueling — A2WC0MME vs CarBerry 4.2

Этот документ фиксирует исследование бедного провала при разгоне в Speed Density и сравнение текущего Forester BIN с CarBerry 4.2.

Главная цель сравнения — понять, почему у CarBerry VE-карта может оставаться гладкой, а переходный AFR при разгоне не требует искусственных бугров в VE.

> Важно: CarBerry 4.2 работает на старом 16-bit Denso 68HC16Y5, а A2WC012E/A2WC0MME — на 32-bit SH7055. Адреса, machine code и hooks между этими ECU напрямую не переносятся. Сравнивается только логика калибровки и поведение подсистем.

## Контрольные BIN

### Forester

~~~text
File:    Forester_SG9_MAP_clean_v25.bin
Size:    524288 bytes
SHA256:  2ca539d0c47e3b1eec96c41e1e514c7b19b0e3786e9d826a41d3a3505b4c5d99
ROM:     A2WC012E / patched internal ID A2WC0MME
CPU:     SH7055
~~~

### CarBerry reference

~~~text
File:    work2_100+95_3D04EA4605_CarBerry42_FULL_160KiB.bin
Size:    163840 bytes
SHA256:  b06e1282a4b274db856d250ae8a1babaf175729f7f9e9fec12e465fb774a4483
ECUID:   3D04EA4605
Platform: CarBerry 4.2
CPU:     68HC16Y5
~~~

## ✅ Current Forester SD structure

На Forester_SG9_MAP_clean_v25.bin подтверждена следующая структура MerpMod SD:

~~~text
Speed Density Mode:              0x69DD4

Volumetric Efficiency Table 1:   0x69EA4
  MAP axis:                      0x69DE4
  RPM axis:                      0x69E44

Atmospheric Pressure Compensation:
  table:                         0x6A378
  MAP axis:                      0x6A340
  atmospheric pressure axis:     0x6A35C

SD Blending Table:
  table:                         0x6A448
  MAP axis:                      0x6A3F8
  RPM axis:                      0x6A420
~~~

### Delta MAP clarification

0x6A378 — **Atmospheric Pressure Compensation**, а не Delta MAP Compensation.

Для upstream A2WC012E target MerpMod:

~~~c
#define SD_DMAP 0
~~~

и в target header A2WC012E отсутствует определение pDeltaMap.

Следовательно, в clean v25 нет скомпилированной SDDeltaMapTable и нет отдельного Delta MAP multiplier в SD calculation.

Это не отменяет существования исторических custom-веток проекта вроде DMapMini: они являются отдельными экспериментальными patch-ветками и не должны использоваться как доказательство того, что Delta MAP присутствует в clean/upstream SD build.

## ✅ CarBerry действительно работает в full Speed Density

В reference BIN по 0xFA68 находится CarBerry signature режима:

~~~text
37 E5 10 80 37 EA 17 98 37 35 FF FF 37 6A 10 7E 27 F7
~~~

Definition CarBerry 4.2 определяет её как **Speed Density**.

Дополнительно:

~~~text
Force Full Time Open Loop @ 0x2DCF7 = 0
~~~

То есть машина не получает нормальный разгон просто потому, что всегда находится в Open Loop.

## ✅ Load/MAP smoothing не объясняет гладкую VE

У CarBerry есть:

- Engine Load Smoothing по Delta MAP и MAF/SD blend ratio;
- отдельные MAP smoothing thresholds.

Но в reference BIN строка Engine Load Smoothing для **100% SD** равна:

~~~text
0  0  0  0  0  0 %
~~~

То есть в full SD эта таблица фактически не сглаживает load.

MAP signal smoothing присутствует:

~~~text
до 2500 rpm:
  decreasing: -0.013332 bar/sample
  increasing: +0.013332 bar/sample

выше 2500 rpm:
  decreasing: -0.019998 bar/sample
  increasing: +0.019998 bar/sample
~~~

Это полезная фильтрация сигнала, но она не добавляет переходное топливо.

## ✅ Основной механизм переходного топлива — Throttle Tip-in Enrichment

Обе системы имеют отдельный Tip-in Enrichment.

Definition описывает его как дополнительное обогащение при положительном изменении throttle. Это **отдельный дополнительный firing форсунок**, а не изменение основной VE-карты.

Именно поэтому VE может описывать steady-state volumetric efficiency, а короткий переходный дефицит топлива при открытии дросселя закрывается другой подсистемой.

### CarBerry 4.2

~~~text
Throttle Tip-in Enrichment:
  table:                         0x29414
  Delta TPS axis:                0x29400

Minimum Tip-in Activation:       0x293FA = 0.384 ms
Minimum Delta TPS Activation:    0x293F8 = ~1.63 %

Injector Flow Scaling:           ~562.45 cc/min
~~~

### Forester A2WC0MME v25

~~~text
Throttle Tip-in Enrichment:
  table:                         0x59B84
  Delta TPS axis:                0x59B3C

Minimum Tip-in Activation:       0x58DA8 = 1.000 ms
Minimum Delta TPS Activation:    0x58DA4 = 0.20 %

Injector Flow Scaling:           750.00 cc/min
~~~

### Сравнение самой Tip-in карты

Интерполяция базовых таблиц:

| Delta TPS | CarBerry | Forester |
|---:|---:|---:|
| 2% | 0.360 ms | 0.464 ms |
| 3% | 0.468 ms | 0.552 ms |
| 4% | 0.576 ms | 0.648 ms |
| 5% | 0.685 ms | 0.822 ms |
| 6% | 0.793 ms | 0.984 ms |
| 8% | 1.009 ms | 1.152 ms |
| 10% | 1.224 ms | 1.323 ms |
| 20% | 2.219 ms | 2.416 ms |
| 30% | 3.119 ms | 3.730 ms |

То есть сама Forester Tip-in table **не слабее**. Во многих точках она даже даёт больше дополнительного pulse width.

Разница — в пороге, после которого рассчитанный Tip-in вообще разрешается применить.

При прогретом моторе, RPM выше зоны низкооборотной RPM-compensation и boost-error compensation в нейтральной области:

~~~text
CarBerry:
  threshold 0.384 ms
  base table crosses it at ~2.2% Delta TPS

Forester:
  threshold 1.000 ms
  base table crosses it at ~6.2% Delta TPS
~~~

Следовательно, при умеренно быстром открытии дросселя примерно на 3–6%:

~~~text
CarBerry  -> Tip-in уже применяется
Forester  -> рассчитанный Tip-in ещё ниже 1.000 ms и отбрасывается
~~~

Это сильный кандидат на объяснение бедной ямы при разгоне.

## Сопутствующие Tip-in compensations

CarBerry дополнительно имеет:

- Tip-in compensation по RPM;
- Tip-in compensation по positive boost error;
- Tip-in compensation по ECT;
- counters / cumulative throttle limits.

В reference BIN:

~~~text
RPM compensation:
  800 rpm:  -9.375%
  1200 rpm: -6.25%
  >=1600:    0%

Positive boost error:
  0.000 / 0.085 bar: -50%
  >=~0.171 bar:        0%

ECT:
  >=80 C: 0%
  ниже температуры enrichment увеличивается
~~~

Forester также имеет compensation по Boost Error и ECT. На прогретом моторе их форма близка по смыслу: при достаточно большом positive boost error correction становится нейтральной, а при ECT около 80 C и выше дополнительная температурная прибавка исчезает.

Поэтому различие 0.384 ms vs 1.000 ms остаётся существенным именно в типичном прогретом разгоне/спуле.

## CarBerry Port Temperature Estimation

В reference BIN CarBerry Port Temp Estimation включён.

IAT usage зависит от airflow примерно так:

~~~text
~6 g/s   -> 69.9% IAT
~8 g/s   -> 76.2%
~12 g/s  -> 84.0%
~20 g/s  -> 92.2%
~40 g/s  -> 98.0%
~60 g/s  -> 100% IAT
~~~

После этого применяется SD load compensation по IAT/estimated port temperature.

Примеры multiplier:

~~~text
-40 C -> 1.1500
  0 C -> 1.0850
 20 C -> 1.0525
 40 C -> 1.0200
 70 C -> 0.9967
100 C -> 0.9617
110 C -> 0.9500
~~~

Это помогает корректно считать air charge в разных тепловых режимах, но по масштабу и назначению не выглядит главным объяснением короткой lean spike при открытии газа.

## 🟡 Working hypothesis — почему Forester VE стала негладкой

Рабочая гипотеза:

~~~text
steady-state:
MAP + RPM + VE -> SD airflow -> всё нормально

transient:
throttle opens
    ↓
real cylinder filling changes quickly
    ↓
Forester calculates Tip-in
    ↓
calculated value < 1.000 ms
    ↓
Tip-in is not applied
    ↓
short lean event
~~~

Если такой lean event исправлять самой VE-картой, в ячейках разгона появляются локальные бугры.

Тогда одна карта вынуждена одновременно решать две разные задачи:

1. steady-state volumetric efficiency;
2. transient wall-wetting / acceleration enrichment.

CarBerry позволяет держать VE более гладкой, потому что переходное топливо раньше забирает на себя Tip-in subsystem.

Статус этой причинной связи: **PROBABLE**, пока нет controlled before/after log на Forester.

## 🧪 Предлагаемый controlled test

Не менять одновременно VE и саму Tip-in curve.

Первый тест:

~~~text
Minimum Tip-in Enrichment Activation
0x58DA8

1.000 ms -> 0.600 ms
~~~

Если результат направленно положительный, отдельным следующим тестом рассмотреть:

~~~text
0.600 ms -> 0.500 ms
~~~

Не копировать CarBerry 0.384 ms напрямую: ECU, форсунки, engine dynamics и реализация различаются.

### Логировать

- RPM;
- throttle / throttle delta, если доступен;
- MAP;
- boost error;
- Injector Pulse Width;
- Wideband AFR/lambda;
- commanded/final fueling target;
- SD calculated airflow / Engine Load;
- ECT;
- IAT;
- AF Correction / Learning;
- Tip-in related runtime parameter, если его удастся вывести в logger.

### Условия теста

- полностью прогретый двигатель;
- одинаковая передача;
- близкий стартовый RPM;
- одинаковый тип нажатия педали;
- несколько повторов baseline и test;
- VE не менять между baseline и threshold-test.

### Критерий успеха

После снижения threshold:

1. lean spike при открытии дросселя уменьшается;
2. нет нового чрезмерного rich spike;
3. нет рывка/заливания при малых движениях педали;
4. steady-state AFR не требует новых VE corrections;
5. повторяемость результата сохраняется в нескольких разгонах.

Если это подтвердится, следующий этап — разгладить VE на основе steady-state данных, не используя её как acceleration-enrichment table.

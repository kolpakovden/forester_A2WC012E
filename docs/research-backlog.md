# Research backlog

Незакрытые вопросы проекта. Пока пункт находится здесь, его нельзя считать подтверждённым правилом настройки.

## High priority


### SD transient lean-out / Tip-in threshold validation

Сравнение Forester_SG9_MAP_clean_v25.bin с CarBerry 4.2 показало:

~~~text
Forester Minimum Tip-in Activation: 1.000 ms
CarBerry reference:                 0.384 ms

Forester base Tip-in crosses threshold: ~6.2% Delta TPS
CarBerry base Tip-in crosses threshold: ~2.2% Delta TPS
~~~

Сама Forester Tip-in curve не слабее CarBerry; проблема может быть именно в позднем разрешении дополнительного pulse.

Нужен controlled test без одновременной правки VE:

1. baseline на 1.000 ms;
2. test 0.600 ms;
3. при направленно положительном результате отдельный test 0.500 ms.

Логировать:

- RPM;
- throttle / Delta TPS, если доступен;
- MAP;
- boost error;
- Injector Pulse Width;
- Wideband AFR/lambda;
- final/commanded fueling;
- SD airflow / Engine Load;
- ECT / IAT;
- AF Correction / Learning;
- Tip-in runtime value, если удастся вывести.

Критерий подтверждения гипотезы: lean spike уменьшается без нового rich spike/рывка, steady-state не требует ухудшения VE и результат повторяется.

Не копировать CarBerry 0.384 ms напрямую.

Подробности: [sd-transient-fueling.md](sd-transient-fueling.md).

Статус: **PROBABLE / HIGH PRIORITY TEST**.

### v69 Clean Spark Cut validation

v68 `LC Cut Mode = 1` был проверен на автомобиле и дал заметно более сильный spool, но Injector Pulse Width всё ещё периодически падал до ~`0.77 ms`; значит LC fuel cut оставался активен.

Для v69 собран clean-spark вариант, который во время `LC Engaged && LC Cut Mode == 1` переводит active `RevLimCut/RevLimResume` к normal RedLineCut и оставляет отдельный spark scheduler на launch RPM.

Нужно подтвердить на полностью прогретом моторе коротким логом:

- `LC Engaged`;
- RPM;
- MAP;
- Injector Pulse Width;
- Ignition Total Timing;
- Wideband AFR;
- `LC Spark Cut Active @ 0xFFCA78`;
- `LC Spark Event Counter @ 0xFFCA79`;
- `RevLim Active Cut RPM @ 0xFFCA44`.

Критерии успеха:

1. active cut RPM в clean-spark LC уходит к normal RedLineCut;
2. IPW больше не циклически проваливается к ~`0.77 ms` из-за launch limiter;
3. spark flag/counter подтверждает pattern `2/5`;
4. RPM остаётся контролируемым около launch target;
5. ordinary RedLine fuel cut остаётся рабочей защитой.

Статус: **EXPERIMENTAL / DO NOT MARK STABLE BEFORE LOG**.

### A/F Learning #1 Modify Airflow Limit (Max)

- В custom definition указан offset `0x58BF8`.
- Одна тестовая прямая правка закончилась плохой работой двигателя и откатом.
- Требуется заново определить datatype, scale, фактическое назначение байтов и подтвердить offset через controlled diff.

Статус: **DO NOT PATCH / REVALIDATE**.

### Injector scalar / latency

Исторически использовались несколько scalar: `503.93`, `541.25`, `552.12`, `564.93 cc/min`.

Нужно собрать по каждому варианту связанные логи и отделить:

- ошибку scalar;
- ошибку latency;
- остаточную ошибку MAF;
- влияние A/F Learning.

До этого не назначать одно из тестовых значений «финальным» только по имени ROM.

### TGV calibration after hardware delete

DTC отключены, но нужно окончательно проверить наличие активных TGV-dependent:

- fueling compensation;
- ignition/idle compensation;
- cold-start logic;
- переключение альтернативных таблиц.

### A/F Learning D

Перенос нижней границы D `60 → 40 g/s` не решил проблему как standalone fix.

Нужно определить реальную логику выбора learning range и условия применения накопленного learning в OL.

## Medium priority

### Primary OL vs Final Fueling Base

Зафиксировано существенное расхождение Primary OL и фактического AFR в отдельных режимах.

Нужно построить полную цепочку:

```text
Primary Open Loop Fueling
→ minimum enrichment / compensation
→ learning/other correction
→ Final Fueling Base
→ injector command
→ measured WB AFR
```

### Atmospheric pressure / boost compensation

В логах атмосферное давление наблюдалось около `0.95 bar`. Ранее в таблицах встречались значения:

```text
Target Boost Compensation (Atm. Pressure) Multiplier: 0.75537
Target Boost Compensation (Atm. Pressure) Multiplier Offset: 0.2500
```

Нужно подтвердить, как именно эти таблицы участвуют в расчёте target boost на A2WC012E, прежде чем менять их.

### Launch Control / Flat Foot Shifting — remaining questions

Базовая LC state/limits и несколько patch-related offsets уже документированы. После v69 validation ещё остаётся отдельно проверить:

- поведение FFS с новыми spark hooks;
- отсутствие нежелательного влияния OCR/GR hooks вне LC;
- корректный reset spark event counter при выходе из LC;
- thermal behavior при повторных коротких launch events;
- нужен ли отдельный combo-cut mode после clean-spark validation.

Подробности текущей ветки: [`launch-control-spark-cut.md`](launch-control-spark-cut.md).

## Правило закрытия backlog

Пункт можно убрать из backlog только после появления:

1. точного ROM/version;
2. конкретного изменения;
3. before/after diff;
4. контрольного лога/теста;
5. понятного результата;
6. записи в `known-results.md` или `rejected-experiments.md`.

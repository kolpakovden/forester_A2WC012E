# Research backlog

Незакрытые вопросы проекта. Пока пункт находится здесь, его нельзя считать подтверждённым правилом настройки.

## High priority

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

### Launch Control / Flat Foot Shifting

Патчи присутствовали/ожидались в отдельных ROM, но их адреса и состояние должны документироваться отдельно от штатных calibration tables.

Перед переносом в stable definition нужно подтвердить:

- patch signature;
- activation settings;
- связанные limits;
- отсутствие пересечения с другими ручными patch.

## Правило закрытия backlog

Пункт можно убрать из backlog только после появления:

1. точного ROM/version;
2. конкретного изменения;
3. before/after diff;
4. контрольного лога/теста;
5. понятного результата;
6. записи в `known-results.md` или `rejected-experiments.md`.

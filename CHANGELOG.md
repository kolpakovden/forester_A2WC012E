# Changelog

Этот файл фиксирует только осмысленные этапы настройки. Неудачные эксперименты описываются в `docs/rejected-experiments.md` и при необходимости сохраняются отдельно как rejected ROM.

## Правила версий

Рекомендуемый формат:

- `v0.x.y` — этапы настройки до окончательной стабильной конфигурации;
- `v1.0.0` — первая полностью проверенная конфигурация;
- patch (`x.x.1`) — небольшая локальная правка без смены логики настройки;
- minor (`x.1.0`) — новый этап: MAF, injectors, fueling, ignition и т.п.;
- major (`1.0.0`) — новая базовая конфигурация железа/ECU или принципиально новая калибровка.

Каждая версия должна содержать:

- базовый ROM;
- список изменённых таблиц;
- причину изменения;
- связанные параметры, которые проверялись;
- лог проверки;
- итоговый статус.

## Шаблон записи

```text
## v0.x.y — краткое название

Base ROM:
- filename.bin

Изменения:
- Table A: что изменено
- Table B: что изменено

Проверка:
- запуск: OK / FAIL
- реакция на педаль: OK / FAIL
- ХХ: OK / FAIL
- CL: OK / FAIL
- OL: OK / FAIL
- WOT: OK / FAIL
- IAM / FBKC / FLKC: результат
- AFR/WB: результат

Логи:
- filename.csv

Статус:
- CONFIRMED / PROBABLE / EXPERIMENTAL / REJECTED

Примечания:
- ...
```

## 2026-08-19 — project identity correction

- Исправлена ошибочная идентификация автомобиля в документации: автомобиль проекта — **Subaru Forester STI SG9, JDM / RHD**, а не SH5.
- `sg9` в именах BIN соответствует реальной модели автомобиля проекта и не является legacy-обозначением другой машины.
- Исправлены `README.md` и `docs/known-results.md`.
- Старые commit messages с `SH5` остаются только в истории Git и считаются документированной ошибкой, а не фактом о машине.

## 2026-08-19 — address research / MerpMod map

- Добавлен `docs/address-research-workflow.md` с фактической методикой поиска и подтверждения новых offsets: полный BIN → source/reference → проверка datatype/axis/scaling → controlled edit → binary diff.
- Зафиксировано правило разделять calibration/code addresses и runtime RAM pointers.
- Добавлен `docs/merpmod-a2wc012e-address-map.md` с A2WC012E target map MerpMod: ROM/code hooks, RAM engine parameters, load smoothing и memory-reset references.
- `dRomHoleStart 0x00069C10` отмечен как source-corroborated: адрес совпадает в target header и существующем A2WC012E MerpMod patch.
- Подтверждено наличие второй 16-point idle timing table: `Base Timing Idle B @ 0x5B167` с общей ECT axis `0x5AFDC`; конкретная логика выбора A/B и связь с TGV пока остаются `PROBABLE`.
- В основную карту добавлены связанные idle/load/IAT candidates из рабочего definition без повышения их до `CONFIRMED`.
- Добавлен `docs/experimental-map-series.md`: отдельная история experimental изменений v36, v37, v38, v40 и v41 с точными offsets и old/new values.
- Зафиксирована текущая экспериментальная ветка Delta MAP compensation (`DMapMini`): 7×7 neutral table, `Pull3D 0x00002110`, `pDeltaMap 0xFFFFAF88`, `pEngineSpeed 0xFFFFB218`. Статус — `EXPERIMENTAL`, без утверждения о подтверждённом поведении на автомобиле.

## 2026-08-18 — collaboration / repository hardening

- Зафиксировано, что автомобиль проекта — **Subaru Forester STI SG9, JDM / RHD**, ECU/ROM **A2WC012E**.
- Уточнено, что `sg9` в именах BIN соответствует автомобилю проекта; прежняя трактовка как legacy filename была ошибочной.
- Добавлен `CONTRIBUTING.md` для совместной работы.
- Расширена карта зависимостей таблиц.
- Добавлены отдельные зависимости для idle catch и airflow/load limits.
- Зафиксировано правило: связанную таблицу нужно проверять, но не обязательно менять.
- Уточнены критерии `stable`, `experimental/PRECHECK` и `rejected` ROM.
- Исторические BIN не переименовываются задним числом, если это ломает связь с логами и предыдущими версиями.

## 2026-08-18 — initial knowledge base

- Создана структура базы знаний.
- Зафиксирован workflow MAF → OL → fueling/injectors → ignition/boost.
- Добавлена карта зависимостей таблиц.
- Отдельно фиксируются неудачные эксперименты.
- Фактические ROM и логи добавляются только вместе с описанием версии и статуса.

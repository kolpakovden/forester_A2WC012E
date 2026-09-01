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

## 2026-09-02 — v69 Clean Spark Cut LC

Base ROM:
- `forester_sg9_sti_MAP_IAT_GM_dMap_v68_SPARK_CUT_ENABLED.bin`
- SHA256 `8f02eecf37fad5340baf0ba5d66e62308a979660b4926c6ad0559fc53f869ecc`

Новый основной test ROM:
- `forester_sg9_sti_MAP_IAT_GM_dMap_v69_CLEAN_SPARK_CUT.bin`
- SHA256 `02581366d410326102c8ca7ffe7f483e2b1ecdc1f7363cd8a7eac663c8d6e4aa`

Fallback:
- `forester_sg9_sti_MAP_IAT_GM_dMap_v69_CLEAN_SPARK_SAFE.bin`
- SHA256 `b3bb642372636c7abb312e7659f91ad4e69d683afe0a2d4d681eb3a405715ec2`

Изменения:
- `LC Cut Mode = 1` в основном BIN; fallback использует mode 0.
- Spark pattern уменьшен `3/5 → 2/5`.
- POLF wrapper перенесён на `0x6B000`; pointer `0x1132C` изменён `0x0006AE00 → 0x0006B000`.
- Пока `LC Engaged && LC Cut Mode == 1`, active MerpMod `RevLimCut @ 0xFFFFCA44` и `RevLimResume @ 0xFFFFCA48` поднимаются до normal `RedLineCut @ 0xFFFFCA4C`.
- Ниже RedLineCut очищается только rev-limit fuel-cut bit `0x80` в `pFlagsRevLim @ 0xFFFFB868`.
- Normal RedLineCut logic/calibration не удалены и остаются hard fuel-cut protection.
- DeltaMAP, Advanced LC fuel/timing, OCR/GR hooks и revlim code сохранены в ожидаемых областях.

Новый logger:
- `A2WC0MME LC Spark Cut Active @ 0xFFCA78`.
- `A2WC0MME LC Spark Event Counter @ 0xFFCA79`.

Статус:
- **EXPERIMENTAL / awaiting vehicle validation**.

Ожидаемая проверка:
- на clean-spark LC active cut RPM должен стать normal RedLineCut;
- Injector Pulse Width не должен циклически падать к ~`0.77 ms` из-за LC limiter;
- spark-cut flag/counter должны показать event pattern;
- тест короткий, только на полностью прогретом моторе/масле.

## 2026-09-02 — v68 spark-cut vehicle result

Test ROM:
- `forester_sg9_sti_MAP_IAT_GM_dMap_v68_SPARK_CUT_ENABLED.bin`
- SHA256 `8f02eecf37fad5340baf0ba5d66e62308a979660b4926c6ad0559fc53f869ecc`
- `LC Cut Mode = 1`, initial pattern `3/5`.

Лог:
- `romraiderlog_20260902_001107.csv` — пользователь подтвердил, что он записан именно на v68 enabled.

Подтверждено логом:
- limiter region примерно `4.4–4.6k rpm`;
- MAP вырос примерно до `1.93 bar absolute`;
- Injector Pulse Width продолжал повторно падать до ~`0.77 ms` между нормальными/high-IPW samples;
- значит LC fuel cut оставался активен параллельно с новым режимом;
- logged timing на limiter в части выборки около `+3…+4°`;
- ECT в тесте около `61°C`, поэтому этот прогон не использовать как нормальный thermal baseline.

Вывод:
- v68 сохраняется как **EXPERIMENTAL / vehicle-tested evidence**, но не считается clean spark-cut реализацией.
- прямой spark-cut-active channel в этом логе отсутствовал, поэтому per-event spark suppression не объявляется CONFIRMED только по этому CSV.

## 2026-08-19 — project identity correction

- Исправлена ошибочная идентификация автомобиля в документации: автомобиль проекта — **Subaru Forester STI SG9, JDM / RHD**, а не SH5.
- `sg9` в именах BIN соответствует реальной модели автомобиля проекта и не является legacy filename другой машины.
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

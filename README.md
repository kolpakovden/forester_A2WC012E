# A2WC012E ECU Tuning Knowledge Base — Subaru Forester STI SG9

Практическая база знаний по исследованию и настройке ECU/ROM **A2WC012E** для **Subaru Forester STI SG9, JDM / RHD**, собранная из реальных изменений, binary diff, логов, исходников patch и проверок на автомобиле.

> Основной объект этого репозитория — именно **ROM ID A2WC012E**. Значения, offsets и выводы нельзя автоматически переносить на другие ROM ID, даже если двигатель, ECU или модель автомобиля похожи.

> **Важно про имена файлов:** `sg9` в исторических BIN соответствует автомобилю проекта — **Subaru Forester STI SG9**. Это не legacy-обозначение другой модели.

## Зачем этот репозиторий

Цель — не хранить все эксперименты подряд, а фиксировать:

- проверенные рабочие изменения;
- промежуточные стабильные ROM;
- логи, которыми подтверждена конкретная версия;
- зависимости между таблицами;
- последовательность настройки;
- подтверждённые адреса таблиц;
- методику поиска новых адресов;
- code hooks и runtime RAM references отдельно от calibration offsets;
- неудачные подходы, чтобы не повторять их;
- незакрытые гипотезы отдельно от проверенных фактов.

## Статусы

- ✅ **CONFIRMED** — результат подтверждён поведением автомобиля, ROM diff и/или прямой проверкой структуры A2WC012E.
- 🟡 **PROBABLE** — вывод выглядит обоснованным, но проверки пока недостаточно.
- 🧪 **EXPERIMENTAL** — изменение находится в процессе проверки.
- 📚 **REFERENCE** — адрес/название получены из source map, definition или другого источника и служат ориентиром для исследования.
- ❌ **REJECTED** — подход не дал ожидаемого результата либо вызвал проблему.

## Основные правила

1. Одна логическая группа изменений — одна версия/commit.
2. Не менять одновременно MAF, injector scaling, fueling и ignition без необходимости.
3. После каждой существенной правки записывать лог.
4. Стабильная ROM должна иметь описание изменений и связанный лог.
5. Неудачная ROM не удаляется: причина отказа документируется отдельно.
6. Любая прямая правка бинарника требует подтверждённого адреса/definition и проверки diff.
7. Перед записью в ECU всегда сохранять заведомо рабочую предыдущую ROM.
8. Аппаратную конфигурацию автомобиля фиксировать отдельно для каждой значимой версии, чтобы не смешивать особенности железа с особенностями ROM.
9. Исторические файлы не переименовывать задним числом, если это ломает связь с логами и предыдущими обсуждениями.
10. Не смешивать ROM/code addresses и runtime RAM pointers: одинаковая подсистема может иметь несколько разных адресов с разным назначением.

## Структура

```text
.
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── docs/
│   ├── workflow.md
│   ├── table-dependencies.md
│   ├── address-research-workflow.md
│   ├── a2wc012e-map.md
│   ├── merpmod-a2wc012e-address-map.md
│   ├── experimental-map-series.md
│   ├── maf-scaling.md
│   ├── gm-iat-scaling.md
│   ├── tgv-delete.md
│   ├── known-results.md
│   ├── rejected-experiments.md
│   └── research-backlog.md
├── definitions/
│   └── README.md
├── evidence/
│   └── README.md
├── roms/
│   └── README.md
└── logs/
    └── README.md
```

## Быстрые ссылки

- [`docs/workflow.md`](docs/workflow.md) — порядок настройки и проверки после прошивки.
- [`docs/table-dependencies.md`](docs/table-dependencies.md) — что проверять при изменении каждой группы таблиц.
- [`docs/address-research-workflow.md`](docs/address-research-workflow.md) — как искать, проверять и переводить новые адреса в CONFIRMED.
- [`docs/a2wc012e-map.md`](docs/a2wc012e-map.md) — подтверждённые и неподтверждённые calibration offsets A2WC012E.
- [`docs/merpmod-a2wc012e-address-map.md`](docs/merpmod-a2wc012e-address-map.md) — target/source map MerpMod: ROM/code hooks, runtime RAM и ROM-hole.
- [`docs/experimental-map-series.md`](docs/experimental-map-series.md) — история последних experimental v36→v41 и точные изменения.
- [`docs/maf-scaling.md`](docs/maf-scaling.md) — методика CL/OL MAF, формулы и реальные фильтры логов.
- [`docs/gm-iat-scaling.md`](docs/gm-iat-scaling.md) — GM 25036751 / ACDelco 213-190 IAT: offsets A2WC012E, штатная кривая, рассчитанный 30-point scaling и план проверки на автомобиле.
- [`docs/tgv-delete.md`](docs/tgv-delete.md) — TGV DTC delete и найденная вторая Idle Timing table.
- [`docs/known-results.md`](docs/known-results.md) — уже установленные факты проекта.
- [`docs/rejected-experiments.md`](docs/rejected-experiments.md) — то, что не сработало или дало проблему.
- [`docs/research-backlog.md`](docs/research-backlog.md) — вопросы, которые ещё нельзя считать закрытыми.
- [`evidence/`](evidence/) — проверочные артефакты, hashes и результаты binary diff.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — как другому человеку безопасно продолжать работу с проектом.

## Текущий порядок работы

Предпочтительная последовательность:

1. Проверить базовую исправность автомобиля и датчиков.
2. Зафиксировать исходную рабочую ROM.
3. Настроить MAF в Closed Loop.
4. Проверить переход CL → OL.
5. Настроить верх MAF по широкополосной лямбде в Open Loop.
6. Только после стабилизации MAF оценивать injector scalar/latency и Primary Open Loop Fueling.
7. Затем корректировать ignition/boost и связанные компенсации.
8. Для SD/patch-разработки отдельно проверять hooks, RAM pointers и linker map.
9. После каждого этапа создать контрольную стабильную версию.

## Уже подтверждённые технические точки

Для A2WC012E подтверждены, среди прочего:

```text
MAF Voltage axis:     0x5E538
MAF Flow table:       0x5E610
Target Throttle:      0x5D6AC
Requested Torque:     0x5DB70
Base Timing Idle A:   0x5B157
Base Timing Idle B:   0x5B167
Idle ECT axis:        0x5AFDC
```

Для `Base Timing Idle B` подтверждены наличие и адрес; конкретная логика выбора A/B всё ещё исследуется.

Подробности и уровень доверия к каждому адресу — в [`docs/a2wc012e-map.md`](docs/a2wc012e-map.md).

## Как войти в проект новому участнику

Минимальный порядок чтения:

1. `README.md` — назначение и правила проекта.
2. `docs/known-results.md` — что уже считается подтверждённым.
3. `docs/rejected-experiments.md` — что уже пробовали и не нужно повторять без новых данных.
4. `docs/address-research-workflow.md` — как здесь подтверждаются новые offsets.
5. `docs/table-dependencies.md` — какие параметры проверять при каждой правке.
6. `docs/a2wc012e-map.md` и `docs/merpmod-a2wc012e-address-map.md` — две разные карты адресов.
7. `CHANGELOG.md` — история осмысленных этапов.
8. Только после этого — текущий BIN, definition и соответствующие логи.

Если новый участник предлагает изменение, желательно сначала сформулировать:

- какую проблему решаем;
- какую таблицу/функцию меняем;
- какие связанные таблицы/параметры должны быть проверены;
- какой тип адреса используется: calibration / code / RAM;
- какой результат ожидаем увидеть в логе;
- какая ROM остаётся гарантированной точкой отката.

## Важно

Это база знаний по конкретному ROM и конкретным проверенным экспериментам, а не универсальная готовая к заливке прошивка. Аппаратная конфигурация — форсунки, MAF, топливо, впуск, выпуск и другие изменения — всегда должна учитываться при интерпретации логов и переносе калибровок между автомобилями.

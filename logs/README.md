# Log storage

Каждый важный лог должен быть связан с конкретной ROM/версией и задачей теста.

Рекомендуемая структура:

```text
logs/
├── v0.1.0/
├── v0.2.0/
└── rejected/
```

Для каждого набора логов желательно иметь небольшой `README.md`:

```text
ROM:
Date:
Fuel:
Ambient conditions:
Purpose:
Relevant parameters:
Result:
```

## Минимальный набор параметров

Подбирать по задаче, но для основных топливных/MAF тестов полезны:

- RPM;
- Engine Load;
- MAF Voltage;
- MAF g/s;
- throttle;
- A/F Correction #1;
- A/F Learning #1;
- CL/OL state;
- commanded/final fueling, если доступно;
- Wideband AFR;
- IAM;
- FBKC;
- FLKC;
- IAT;
- ECT.

Для boost-настройки дополнительно:

- manifold/boost pressure;
- target boost;
- wastegate duty;
- atmospheric pressure.

## Launch Control / Spark Cut logging

Для текущей A2WC0MME LC-ветки желательно одновременно писать:

- RPM;
- MAP absolute;
- throttle;
- Injector Pulse Width;
- Ignition Total Timing;
- Final Fueling Base;
- Wideband AFR;
- LC Engaged;
- `LC Spark Cut Active @ 0xFFCA78`;
- `LC Spark Event Counter @ 0xFFCA79`;
- `RevLim Active Cut RPM @ 0xFFCA44`, если доступно;
- ECT/IAT.

### Последний подтверждённый v68 test log

`romraiderlog_20260902_001107.csv` записан на `v68_SPARK_CUT_ENABLED`, `LC Cut Mode = 1` — это пользователь подтвердил отдельно.

В логе MAP достигал примерно `1.93 bar absolute`, но IPW продолжал периодически падать до ~`0.77 ms`. Поэтому v68 зафиксирован как mixed-cut/неполный spark-cut этап, а v69 должен проверить удаление LC fuel-cut component.

Подробности: [`../docs/launch-control-spark-cut.md`](../docs/launch-control-spark-cut.md).

## Правило

Не хранить лог без понимания, на какой ROM он записан. Файл без версии прошивки сильно теряет диагностическую ценность.

Не делать вывод о фактическом AFR отдельного рабочего цикла только по wideband во время limiter/misfire/fuel-cut событий: при пропусках и cut в выпуск попадает свободный кислород, и wideband может показывать «бедно» при совершенно другой причине.

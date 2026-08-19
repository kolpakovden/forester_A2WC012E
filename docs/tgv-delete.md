# TGV Delete — заметки проекта

## Исходное состояние

На автомобиле TGV hardware отсутствует: нет моторчиков и датчиков положения заслонок.

В ходе проекта были отключены связанные DTC:

```text
P2004
P2005
P2006
P2007
P2008
P2009
P2011
P2012
P2016
P2017
P2021
P2022
```

## Что это решает

Отключение DTC предотвращает диагностические ошибки по отсутствующим цепям TGV.

## Что это НЕ доказывает

Отключение кодов само по себе не подтверждает, что в конкретном ROM отсутствуют или не используются:

- TGV-related fueling compensation;
- ignition compensation;
- cold-start logic;
- airflow/load compensation;
- другие таблицы, которые могут зависеть от статуса TGV.

Поэтому правило проекта такое:

> DTC delete и calibration delete — это разные задачи.

## Найденная вторая Idle Timing table

При исследовании области idle timing в A2WC012E обнаружены две последовательные 16-point таблицы с общей ECT axis:

```text
ECT axis:            0x5AFDC
Base Timing Idle A:  0x5B157
Base Timing Idle B:  0x5B167
```

Наличие второй таблицы и её структура подтверждаются данными ROM: `0x5B167` идёт сразу после 16 байт первой таблицы и корректно декодируется по той же температурной оси.

В working definition она отображается как:

```text
Base Timing Idle B (In-Gear)
```

При этом базовое описание definition допускает связь переключения A/B с TGV, но **для A2WC012E мы пока не считаем доказанным**, что именно TGV status выбирает эту карту или что название `In-Gear` полностью описывает её условие выбора.

Поэтому разделяем два факта:

```text
наличие/адрес Base Timing Idle B — CONFIRMED
условие выбора A/B и связь с TGV — PROBABLE
```

Практический вывод: при TGV delete эту таблицу **нужно учитывать и сравнивать**, но не следует автоматически копировать A → B или менять её только из-за предположения о TGV.

## Что ещё смотреть рядом

В working definition также присутствуют кандидаты:

```text
Base Timing Idle Minimum
  table: 0x5B148
  axis:  0x5B10C

Base Timing Idle Minimum Vehicle Speed Enable
  0x5AD20
```

Они полезны для исследования idle/idle-catch, но до отдельной проверки остаются `PROBABLE`.

## После TGV delete проверить

- холодный запуск;
- горячий запуск;
- ХХ;
- падение оборотов и idle catch;
- переходные режимы;
- CL trims;
- AFR в OL;
- IAM / FBKC / FLKC;
- отсутствие новых DTC.

Если исследуется выбор Idle Timing A/B, дополнительно логировать/сопоставлять:

- gear / neutral / clutch state;
- vehicle speed;
- ECT;
- RPM;
- commanded/final timing;
- throttle/load.

## Статус

- DTC list: **CONFIRMED as applied**.
- Base Timing Idle B `0x5B167`: **CONFIRMED presence/address**.
- Конкретная логика выбора Idle A/B: **PROBABLE**.
- Необходимость дополнительных TGV calibration changes: **PROBABLE / требует отдельной проверки definition, ROM и runtime behavior**.

Пока не найдено и не подтверждено конкретное связанное значение, не менять таблицу только потому, что в её названии присутствует TGV.

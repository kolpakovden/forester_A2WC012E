# RomRaider definitions

Здесь хранятся XML definitions и patch/addon definitions, которые реально относятся к ROM проекта.

Для каждого definition фиксировать:

- ROM ID / patched internal ID;
- источник/базовый definition;
- какие таблицы добавлялись вручную;
- какие адреса подтверждены;
- какие таблицы пока считаются экспериментальными.

## Текущая Launch Control ветка — v69

Для v69 в репозитории лежит компактный standalone LC definition:

`ecu_defs_A2WC012E_v69_LC_ONLY.xml`

Он содержит именно параметры, нужные для текущей LC-ветки:

```text
Rev Limit (Redline)                 0x6A4D0
LC Maximum Speed Threshold          0x6A4EC
Rev Limit (Launch Control)          0x6A4F0
LC Minimum Throttle Threshold       0x6A514
LC Advanced Fuel Mode               0x6AD78
LC Advanced Fuel Target             0x6AD7C
LC Advanced Timing Mode             0x6ADB8
LC Advanced Base Timing Lock        0x6ADBC
LC Cut Mode                         0x6ADC4
LC Spark Events Cut                 0x6ADC8
LC Spark Event Cycle                0x6ADCC
```

Это **LC-only definition**, а не замена полного большого ECU definition со всеми штатными таблицами. Его удобно использовать для проверки/редактирования именно launch-control параметров.

Для logger добавлен:

`logger_A2WC0MME_v69_sparkcut_addon.xml`

Это addon/snippet с диагностическими каналами:

```text
MerpMod Delta MAP                    0xFFAF88
A2WC0MME LC Spark Cut Active         0xFFCA78
A2WC0MME LC Spark Event Counter      0xFFCA79
```

Его ecuparam-блоки нужно добавить в используемый полный RomRaider logger definition.

## Полные XML

Полные рабочие v69 ECU/logger definitions существуют в локальном наборе артефактов проекта, но в `main` пока **не публикуются как огромные XML-файлы**, чтобы не выдавать неполную/повреждённую загрузку за рабочий definition. До отдельной проверенной публикации источником истины в Git являются LC-only definition, logger addon, точные адреса и ROM builder.

## Главное правило

Наличие красивого имени таблицы в XML не подтверждает правильность её адреса.

Для вручную добавленной таблицы должны быть проверены ROM address, datatype, endian, scaling и соответствие ожидаемым байтам в BIN.

v69 status: **EXPERIMENTAL / awaiting vehicle validation**.

Подробности: [`../docs/launch-control-spark-cut.md`](../docs/launch-control-spark-cut.md).

# Связи таблиц и параметров

Цель этого файла — отвечать на вопрос: **если правим одну таблицу, что ещё обязательно проверить?**

Это не означает, что связанные таблицы всегда нужно менять. Сначала их нужно проверить по логам и понять, участвуют ли они в текущем режиме.

## MAF Sensor Scaling

**Изменяем:**
- MAF Sensor Scaling.

**Проверяем одновременно:**
- MAF Voltage;
- MAF g/s;
- Engine Load;
- A/F Correction #1;
- A/F Learning #1;
- Closed Loop / Open Loop status;
- Wideband AFR в OL;
- Final Fueling Base / итоговую цель смеси, если параметр доступен.

**Связи:**
- ошибка MAF влияет на расчёт нагрузки;
- нагрузка влияет на выбор ячеек fueling и ignition;
- поэтому неверный MAF нельзя рассматривать только как «ошибку смеси».

## Injector Flow Scaling

**Изменяем:**
- Injector Flow Scaling / Injector Scalar.

**Обязательно проверить:**
- Injector Latency;
- A/F Correction;
- A/F Learning;
- AFR на ХХ и cruise;
- AFR в OL;
- MAF Scaling.

**Важно:**
Если MAF ещё содержит систематическую ошибку, коррекция injector scalar может просто замаскировать её.

## Injector Latency

**Изменяем:**
- Injector Latency по напряжению.

**Проверяем:**
- AFR/trims на ХХ;
- AFR/trims при малом pulse width;
- напряжение бортовой сети;
- поведение trims при изменении нагрузки;
- scalar форсунок.

Если ошибка сильнее на малых импульсах, а под нагрузкой уменьшается, latency становится более вероятной причиной, чем scalar.

## Primary Open Loop Fueling

**Изменяем:**
- Primary Open Loop Fueling.

**Проверяем:**
- фактический Wideband AFR;
- Final Fueling Base / итоговую цель;
- A/F Learning, если она сохраняет влияние в данном режиме/ROM;
- температурные компенсации;
- enrichment/transition compensation;
- Engine Load и RPM, чтобы убедиться в правильной выбранной ячейке.

**Не делать:**
Не сравнивать WB AFR только с числом из Primary OL и сразу считать разницу ошибкой MAF.

## A/F Learning ranges

**Изменяем:**
- границы диапазонов A/B/C/D либо разрешение обучения.

**Проверяем:**
- в каком диапазоне реально накапливается learning;
- остаётся ли эта коррекция при переходе в OL;
- не маскирует ли learning ошибку MAF или injector scaling.

Изменение границы диапазона само по себе не гарантирует исчезновения нежелательной коррекции.

## Ignition tables

**Изменяем:**
- Base Timing / Advance-related таблицы.

**Проверяем:**
- IAM;
- FBKC;
- FLKC;
- Engine Load;
- RPM;
- AFR;
- IAT;
- ECT.

После изменения fueling зажигание нужно оценить повторно, даже если timing tables не менялись.

## Boost / Target Boost

**Изменяем:**
- Target Boost и/или связанные compensation tables.

**Проверяем:**
- фактический boost;
- wastegate duty;
- атмосферное давление;
- Target Boost Compensation (Atm. Pressure);
- multiplier/offset, если они используются данным ROM;
- AFR;
- knock;
- load limits.

## TGV delete

**Изменяем/отключаем:**
- DTC, относящиеся к отсутствующим TGV motor/sensor цепям.

**Проверяем:**
- отсутствие новых DTC;
- запуск и ХХ;
- переходные режимы;
- наличие дополнительных TGV compensation tables в definition/ROM.

Отключение DTC не доказывает автоматически, что все связанные с TGV калибровки можно оставить без проверки.

## Прямая правка BIN без definition

Если нужная таблица отсутствует в definition:

1. найти адрес и структуру таблицы;
2. подтвердить адрес по корректному definition/сигнатурам/соседним данным;
3. проверить datatype, endian, scale и размер;
4. изменить только ожидаемые байты;
5. сделать binary diff;
6. проверить checksum, если применимо;
7. только после этого тестировать ROM.

Прямая запись по предположительному offset без проверки — запрещённый для stable workflow подход.

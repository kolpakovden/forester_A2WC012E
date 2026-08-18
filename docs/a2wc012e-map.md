# A2WC012E — карта подтверждённых и референсных адресов

Этот файл специально разделяет **подтверждённые на A2WC012E адреса** и адреса, которые пока известны только по близкому definition A2WC011E или кастомным XML.

Нельзя использовать разделы `PROBABLE`/`EXPERIMENTAL` для прямого binary patch без дополнительной проверки.

## ✅ CONFIRMED — проверено на полном BIN A2WC012E

Контрольный полный BIN:

```text
File:        forester_sg9_sti_v2 (1).bin
Size:        524288 bytes
Internal ID: A2WC012E @ 0x2000
SHA-256:     50cbcb183775b10f75a4c12022842647bc036a078f991aec2629b084fd6af82a
```

### MAF Sensor Scaling

Адреса подтверждены отдельной проверкой MAF Scaling 11 на полном 524288-байтном ROM:

```text
MAF Voltage axis: 0x5E538
MAF Flow table:   0x5E610
Points:           54
```

При контрольной правке было изменено 20 точек / 57 байт, а проверка binary diff показала `0` изменённых байт вне MAF Flow table.

Это делает пару `0x5E538 / 0x5E610` пригодной для статуса **CONFIRMED на A2WC012E**.

### Target Throttle Plate Position

```text
X axis:  0x5D628
Y axis:  0x5D66C
Table:   0x5D6AC
```

Проверенный диапазон значений таблицы: примерно `0.000 ... 84.000`.

### Requested Torque (Accelerator Pedal)

```text
X axis:  0x5DAEC
Y axis:  0x5DB28
Table:   0x5DB70
```

Проверенный диапазон значений: примерно `0.000 ... 320.000`.

### Связь DBW-таблиц

При изменении реакции педали нельзя рассматривать только одну таблицу:

```text
Accelerator Pedal
      ↓
Requested Torque (Accelerator Pedal)
      ↓
Target Throttle Plate Position
      ↓
фактическое открытие дросселя / torque model / load
```

Если правится `Requested Torque`, обязательно проверить `Target Throttle Plate Position`, фактический throttle, load и переходные режимы.

---

## 🟡 PROBABLE — адреса из близкого A2WC011E/custom definition

Ниже адреса, известные по JDM Forester STI `A2WC011E_v1` и производным A2WC012E XML. Часть структуры уже совпала с A2WC012E, но каждый оставшийся адрес всё равно нужно подтверждать отдельно.

Использовать их как карту для поиска, а не как готовые offsets для записи.

```text
MAF Limit (Maximum)
  0x57748

Engine Load Limit (Maximum)
  0x17E14

Injector Flow Scaling
  0x589B0

Injector Latency
  table: 0x5E28C
  Y axis: 0x5E278

Primary Open Loop Fueling
  table: 0x59F4C
  X axis: 0x59EC4
  Y axis: 0x59F04

A/F Learning #1 Limits
  0x58BE0

A/F Learning #1 Airflow Ranges
  0x58BEC

Base Timing
  table: 0x5B998
  X axis: 0x5B910
  Y axis: 0x5B950

Knock Correction Advance Max
  table: 0x5BDB0
  X axis: 0x5BD28
  Y axis: 0x5BD68
```

---

## 🧪 / ❌ A/F Learning #1 Modify Airflow Limit (Max)

В одном из кастомных A2WC012E definitions эта таблица была добавлена как:

```text
A/F Learning #1 Modify Airflow Limit (Max)
address: 0x58BF8
```

Но конкретная тестовая ROM после прямой правки в этой области дала тяжёлый сбой поведения двигателя: троение и отсутствие нормальной реакции на педаль, после чего потребовался откат.

Поэтому текущий статус адреса `0x58BF8`:

```text
DO NOT PATCH
НЕ CONFIRMED
требуется повторная независимая валидация datatype/scale/назначения
```

Не считать саму идею ограничения A/F Learning ошибочной — отклонена конкретная правка/идентификация адреса.

## Как перевести PROBABLE → CONFIRMED

Для каждого адреса:

1. открыть полный A2WC012E BIN;
2. проверить, что данные по адресу имеют ожидаемый datatype/endian;
3. проверить оси и размерность;
4. сопоставить значения с тем, что показывает RomRaider;
5. изменить одну тестовую ячейку в копии через известный корректный editor/definition;
6. сделать binary diff и подтвердить точный offset;
7. вернуть исходное значение либо сохранить только после осмысленной калибровки;
8. добавить подтверждение в этот файл.

## Главное правило

Если адрес не подтверждён на A2WC012E, прямой patch в BIN не делать. Адрес из XML — это гипотеза до тех пор, пока она не подтверждена самим ROM/diff.

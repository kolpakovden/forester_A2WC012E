# A2WC012E — карта подтверждённых и референсных адресов

Этот файл специально разделяет **подтверждённые на A2WC012E адреса** и адреса, которые пока известны только по близкому definition A2WC011E.

Нельзя использовать раздел `PROBABLE` для прямого binary patch без дополнительной проверки.

## ✅ CONFIRMED — проверено на полном BIN A2WC012E

Контрольный полный BIN:

```text
File:        forester_sg9_sti_v2 (1).bin
Size:        524288 bytes
Internal ID: A2WC012E @ 0x2000
SHA-256:     50cbcb183775b10f75a4c12022842647bc036a078f991aec2629b084fd6af82a
```

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

## 🟡 PROBABLE — адреса из близкого A2WC011E definition

Ниже адреса из JDM Forester STI definition `A2WC011E_v1`. Часть структуры совпадает с подтверждёнными адресами A2WC012E (например DBW), но это **не является доказательством**, что каждый адрес идентичен.

Использовать их как карту для поиска, а не как готовые offsets для записи.

```text
MAF Sensor Scaling
  table: 0x5E610
  Y axis: 0x5E538

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

Если адрес не подтверждён на A2WC012E, прямой patch в BIN не делать. Именно такой контроль должен предотвращать повторение истории с проблемной тестовой ROM после правки неизвестного airflow-limit offset.

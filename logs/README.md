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

## Правило

Не хранить лог без понимания, на какой ROM он записан. Файл без версии прошивки сильно теряет диагностическую ценность.

# Experimental MAP series — v36 → v41

Этот файл фиксирует последние изменения experimental ROM, чтобы сохранить причинно-следственную связь между версиями.

> Здесь перечислены **фактически внесённые изменения**, а не утверждение, что каждая версия успешно проверена на автомобиле. До отдельного подтверждения логом/поведением статус — **EXPERIMENTAL**.

Историческое `sg9` в именах файлов — legacy filename. Проект относится к ROM **A2WC012E**.

## v36 — Idle Speed Target + первые VE idle cells

В `forester_sg9_sti_MAP_v36_changes.csv` зафиксировано повышение горячего target idle до `850 rpm` сразу в трёх группах таблиц A/B/C.

Примеры адресов:

```text
Idle Speed Target A
0x5CA3C ... 0x5CA62

Idle Speed Target B
0x5CA7C ... 0x5CAA2

Idle Speed Target C
0x5CABC ... 0x5CAE2
```

Для горячих колонок изменялись значения `700/800 → 850 rpm`.

Дополнительно были затронуты первые VE cells около `800 rpm`, например:

```text
0x69ED6: 129.83 → 131.78
0x69ED8: 131.71 → 134.34
```

Статус: **EXPERIMENTAL checkpoint**.

## v37 — overrun RPM threshold candidate

В `forester_sg9_sti_MAP_v37_OVERRUN_changes.csv` изменены четыре точки по ECT:

```text
ECT 80°C   0x57B40   1024.023 → 2000 rpm
ECT 90°C   0x57B42   1024.023 → 2000 rpm
ECT 100°C  0x57B44   1024.023 → 2000 rpm
ECT 110°C  0x57B46   1024.023 → 2000 rpm
```

Raw:

```text
5243 → 10240
```

Рабочая интерпретация: кандидат порога overrun/decel logic.

Статус имени/назначения: **PROBABLE / EXPERIMENTAL**. Сам offset и факт изменения известны, окончательное назначение должно подтверждаться поведением/дизассемблированием.

## v38 — overrun initial injector enrichment candidate

В `forester_sg9_sti_MAP_v38_OVERRUN_changes.csv` зафиксирована одна правка:

```text
Offset:             0x58DA0
Old raw float:      2800.0
New raw float:      1000.0
Working interpretation:
                    2.8 ms → 1.0 ms
```

Рабочее имя кандидата: `Overrun initial injector enrichment (pulsewidth)`.

Статус: **EXPERIMENTAL**. Не считать название таблицы окончательно подтверждённым только по scaling/поведению.

## v40 — SD idle catch VE

В `forester_sg9_sti_MAP_v40_SD_IDLE_CATCH_VE_changes.csv` изменена низовая область VE около `500 rpm`.

Примеры:

```text
MAP abs ≈ 0.400 bar  0x69EA8  127.68 → 121.30   ×0.95
MAP abs ≈ 0.533 bar  0x69EAA  161.42 → 132.36   ×0.82
MAP abs ≈ 0.667 bar  0x69EAC  175.65 → 108.90   ×0.62
MAP abs ≈ 0.800 bar  0x69EAE  176.94 → 102.63   ×0.58
MAP abs ≈ 0.933 bar  0x69EB0  178.43 → 107.06   ×0.60
```

Это направленная попытка изменить поведение SD в зоне падения оборотов/idle catch.

Статус: **EXPERIMENTAL**.

## v41 — более локальная VE-коррекция 500/800 rpm

В `forester_sg9_sti_MAP_v41_changes.csv` изменение сделано более локально:

```text
500 rpm:
0x69EA6  123.12 → 110.81   ×0.90
0x69EA8  121.30 → 106.74   ×0.88
0x69EAA  132.36 → 119.12   ×0.90

800 rpm:
0x69ED6  131.78 → 121.24   ×0.92
0x69ED8  134.34 → 120.91   ×0.90
0x69EDA  161.20 → 151.53   ×0.94
```

Статус: **EXPERIMENTAL**.

## Почему сохраняем CSV diff рядом с версиями

Для каждой такой версии полезно хранить:

```text
ROM filename
base ROM
SHA-256
change CSV
точные offsets
old/new values
причину изменения
контрольный log
результат проверки
```

Это позволяет отличить:

- «мы предполагаем, что таблица отвечает за X»;
- «мы точно изменили байты Y»;
- «машина реально отреагировала ожидаемым образом».

Эти три утверждения имеют разный уровень доказательности и не должны смешиваться.

## Следующий шаг для promotion в stable

Версию можно повышать из `EXPERIMENTAL` только после:

1. нормального запуска и прогрева;
2. проверки idle / idle catch;
3. нескольких повторяемых переходов throttle → overrun → idle;
4. AFR / trims / load / MAP / RPM в логе;
5. IAM / FBKC / FLKC без новых проблем;
6. сравнения с предыдущей заведомо рабочей ROM;
7. документирования результата в `CHANGELOG.md`.

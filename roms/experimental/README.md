# Experimental ROM inventory

Здесь хранятся **тестовые/промежуточные** ROM A2WC012E. Наличие файла в этой директории не означает, что его можно считать `stable`.

## Правило для BIN

Перед добавлением каждого `.bin` проверить:

```text
size == 524288 bytes
internal/base family == A2WC012E
SHA-256 записан в manifest/SHA256SUMS
есть описание base ROM и изменений
есть статус EXPERIMENTAL / PRECHECK / REJECTED / CONFIRMED
```

Не восстанавливать старый тестовый BIN только из `changes.csv` и не выдавать реконструкцию за исходный артефакт: кроме калибровочных изменений в ROM могут присутствовать checksum, patch code, metadata и изменения предыдущих версий.

## Инвентарь

### v36 — IDLE_CATCH_PRECHECK

```text
Source filename:     forester_sg9_sti_MAP_v36_IDLE_CATCH_PRECHECK(1).bin
Repository filename: A2WC012E_MAP_v36_IDLE_CATCH_PRECHECK.bin
Size:                524288 bytes
SHA-256:              8194b6598f72fe32dc88d7df67073e0a44c841e6a6aa65810d3cc09a203a4105
Status:               EXPERIMENTAL / PRECHECK
```

В `v36/` уже лежат README, checkpoint, SHA256SUMS и `changes.csv`.

### v37 — overrun resume 2000 rpm

Точная правка сохранена в `v37/changes.csv`.

```text
Status: EXPERIMENTAL
BIN bytes: pending original artifact retrieval
```

### v38 — overrun initial enrichment candidate

Точная правка сохранена в `v38/changes.csv`.

```text
Status: EXPERIMENTAL
BIN bytes: pending original artifact retrieval
```

### v40 — SD idle catch VE

Точная правка сохранена в `v40/changes.csv`.

```text
Status: EXPERIMENTAL
BIN bytes: pending original artifact retrieval
```

### v41 — localized SD idle catch VE

Точная правка сохранена в `v41/changes.csv`.

```text
Status: EXPERIMENTAL
BIN bytes: pending original artifact retrieval
```

### v44 — working MerpMod/SD base

Из истории проекта:

```text
Artifact: forester_sg9_sti_MAP_v44.bin
Size:     524288 bytes
Role:     working A2WC012E / MerpMod SD base
SD hook:  0x77B4 -> 0x6A558
Status:   experimental working base
```

SHA-256 нужно снять непосредственно с исходного серверного файла перед публикацией.

### v45 — DMAP test

Из истории проекта:

```text
Role:    v45_DMAP_TEST based on working v44
Size:    524288 bytes
SHA-256: 487bc4333b7e985e4dce5473b4525cd5be206e72c066b864ef19bcd225bdca20
Hook:    4-byte patch @ 0x6A612
Block:   0x6AC40-0x6AD43
Status:  EXPERIMENTAL
```

Оригинальный BIN был сгенерирован на рабочем сервере; публиковать нужно именно его байты и подтвердить приведённый SHA-256.

## Почему здесь могут временно отсутствовать `.bin`

GitHub connector умеет работать с binary blob, но для публикации нужен сам бинарный payload. Метаданные, SHA-256, change CSV и история не позволяют безопасно восстановить **точно тот же** test artifact побайтно.

Поэтому до получения оригинального payload запись остаётся как `pending original artifact retrieval`, а не заменяется самодельной реконструкцией.

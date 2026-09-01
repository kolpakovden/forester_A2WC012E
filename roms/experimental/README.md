# Experimental ROM inventory

Здесь хранятся **тестовые/промежуточные** ROM A2WC012E/A2WC0MME. Наличие файла в этой директории не означает, что его можно считать `stable`.

## Правило для BIN

Перед добавлением каждого `.bin` проверить:

```text
size == 524288 bytes
internal/base family == A2WC012E / documented patched ID
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

### v45 — DMAP test / checksum-fixed artifact

Предоставлен и побайтно проверен файл:

```text
Artifact:   forester_sg9_sti_MAP_v45_DMAP_TEST_CHECKSUM.bin
Size:       524288 bytes
SHA-256:    92e0ff671bda35fe7951d68513c2ed188035b950556ffbe3e1e7cb603f241329
Patched ID: A2WC0MME @ 0x2000
MeRpMoD:    present
Hook:       0x6A612
DMAP block: 0x6AC40-0x6AD43
Status:     EXPERIMENTAL
```

Ранее записанный SHA-256 `487bc4333b7e985e4dce5473b4525cd5be206e72c066b864ef19bcd225bdca20` относится к **другому побайтовому состоянию v45** и не является checksum для предоставленного `*_CHECKSUM.bin`.

Подробности: [`v45/README.md`](v45/README.md).

### v68 — experimental spark-cut LC

```text
ENABLED SHA256: 8f02eecf37fad5340baf0ba5d66e62308a979660b4926c6ad0559fc53f869ecc
SAFE SHA256:    b9da808571b17bcd38bae71c6949c3da6d7ebcc2e17759abded1e6c1c0766466
Status:         EXPERIMENTAL / VEHICLE TESTED
Mode:           1 for ENABLED / 0 for SAFE
Pattern:        3/5
```

Vehicle log `romraiderlog_20260902_001107.csv` was confirmed to be recorded on v68 ENABLED. MAP reached about `1.93 bar absolute`, but Injector Pulse Width still repeatedly fell to ~`0.77 ms`, confirming that LC fuel cut was still present.

Files/details: [`v68/README.md`](v68/README.md).

### v69 — Clean Spark Cut LC

```text
CLEAN SHA256: 02581366d410326102c8ca7ffe7f483e2b1ecdc1f7363cd8a7eac663c8d6e4aa
SAFE SHA256:  b3bb642372636c7abb312e7659f91ad4e69d683afe0a2d4d681eb3a405715ec2
Status:       EXPERIMENTAL / AWAITING VEHICLE VALIDATION
Mode:         1 for CLEAN / 0 for SAFE
Pattern:      2/5
```

Purpose: remove the LC fuel-cut component by moving active MerpMod rev-limit thresholds to normal RedLineCut while clean-spark LC is engaged; retain normal high-RPM fuel-cut protection.

Files/details: [`v69/README.md`](v69/README.md).

Full LC technical notes: [`../../docs/launch-control-spark-cut.md`](../../docs/launch-control-spark-cut.md).

## Почему здесь могут временно отсутствовать `.bin`

Метаданные, SHA-256, change CSV и история не позволяют безопасно восстановить **точно тот же** test artifact побайтно. Поэтому до получения исходного binary payload запись остаётся как `pending original artifact retrieval`, а не заменяется самодельной реконструкцией.

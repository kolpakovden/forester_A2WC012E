# v45 — DMAP_TEST_CHECKSUM

Статус: **EXPERIMENTAL**.

Фактический бинарник, предоставленный из истории проекта:

```text
Filename: forester_sg9_sti_MAP_v45_DMAP_TEST_CHECKSUM.bin
Size:     524288 bytes (512 KiB)
SHA-256:  92e0ff671bda35fe7951d68513c2ed188035b950556ffbe3e1e7cb603f241329
```

## Binary artifact в репозитории

Из-за ограничения GitHub connector исходный payload сохранён в `main` как **побайтно обратимый XZ-архив**:

```text
forester_sg9_sti_MAP_v45_DMAP_TEST_CHECKSUM.bin.xz
XZ size:    192132 bytes
XZ SHA-256: a52b8efa8e0e188a444e9efc32dd9042b2d5e83c8ab052b43596a244dfa95ff2
```

Распаковка:

```bash
xz -dk forester_sg9_sti_MAP_v45_DMAP_TEST_CHECKSUM.bin.xz
sha256sum forester_sg9_sti_MAP_v45_DMAP_TEST_CHECKSUM.bin
```

После распаковки **обязан** получиться исходный 524288-байтный BIN с SHA-256:

```text
92e0ff671bda35fe7951d68513c2ed188035b950556ffbe3e1e7cb603f241329
```

То есть архив — не реконструкция по таблицам и не новый ROM, а сжатое представление именно предоставленного файла.

## Проверенная идентификация

```text
Patched ID @ 0x2000: A2WC0MME
Original A2WC012E string: present in ROM
Patch signature: MeRpMoD
```

## DMAP layout

В предоставленном BIN подтверждено наличие ожидаемой экспериментальной DMAP-разметки:

```text
Hook area:  0x6A612
Hook bytes: A3 85 00 09 ...
DMAP block: 0x6AC40-0x6AD43
ROM size:   0x80000
```

Это соответствует рабочей ветке `v45_DMAP_TEST`.

## Отдельно про предыдущий SHA

Ранее в заметках проекта был записан SHA-256:

```text
487bc4333b7e985e4dce5473b4525cd5be206e72c066b864ef19bcd225bdca20
```

Он **не совпадает побайтно** с предоставленным `*_CHECKSUM.bin`. Поэтому старый hash сохраняется как предыдущий/отдельный артефакт v45 и не должен использоваться для проверки данного checksum-fixed файла.

По имени `CHECKSUM` и месту в истории наиболее вероятно, что предоставленный файл — финальная версия после исправления контрольной суммы, но это происхождение не подменяет побайтную идентификацию: эталон для данного файла — SHA-256 `92e0ff...1329`.

## Правило использования

Не считать `v45` stable только по наличию корректного checksum. Перед повышением статуса нужны запуск/лог и проверка DMAP поведения на автомобиле.

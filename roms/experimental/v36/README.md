# v36 — MAP / IDLE_CATCH_PRECHECK

Текущий промежуточный checkpoint проекта. **Не считать stable/final ROM.**

## Файл

```text
Source filename:
forester_sg9_sti_MAP_v36_IDLE_CATCH_PRECHECK(1).bin

Repository filename:
A2WC012E_MAP_v36_IDLE_CATCH_PRECHECK.bin
```

## Идентификация

```text
Base ROM family: A2WC012E
Patched ID @ 0x2000: A2WC0MME
Patch signature: MeRpMoD
ROM size: 524288 bytes (512 KiB)
```

Внутри ROM присутствует исходный идентификатор `A2WC012E`, а рабочий ID в заголовке изменён патчем MeRpMoD на `A2WC0MME`.

## SHA-256

```text
8194b6598f72fe32dc88d7df67073e0a44c841e6a6aa65810d3cc09a203a4105
```

После загрузки/скачивания BIN этот SHA-256 должен совпасть побайтно.

## Статус

```text
EXPERIMENTAL
CURRENT CHECKPOINT
PRECHECK
```

## Назначение

По имени и месту в истории проекта:

- MAP configuration;
- текущая v36;
- IDLE_CATCH precheck;
- базовая точка для последующих сравнений/diff.

## Что ещё нужно подтвердить логами

- запуск;
- стабильность ХХ;
- idle catch;
- реакцию на педаль;
- DTC;
- CL trims;
- OL/WOT AFR;
- IAM / FBKC / FLKC;
- работу MAP/VE-related изменений.

После подтверждения конкретных режимов статус можно повысить, но `PRECHECK` не переносить в `stable` автоматически.

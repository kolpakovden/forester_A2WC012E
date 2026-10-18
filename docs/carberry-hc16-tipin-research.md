# CarBerry 4.2 → Forester SH7055: HC16 reverse engineering log

**Дата фиксации:** 2026-10-18  
**Статус:** RESEARCH / экспериментальный дизассемблер; **не является готовым патчем**.  
**Цель:** восстановить переносимую логику CarBerry (сначала Tip-in / transient fueling) и в дальнейшем реализовать её независимо на Forester A2WC012E/A2WC0MME, не переносить код Motorola непосредственно в SH7055.

## 1. Исходные объекты и инструменты

| Объект | Характеристика |
|---|---|
| CarBerry reference | `work2_100+95_3D04EA4605_CarBerry42_FULL_160KiB.bin`, 163840 bytes (0x28000), 68HC16Y5, ECUID в XML `3D04EA4605` |
| SHA-256 CarBerry | `b06e1282a4b274db856d250ae8a1babaf175729f7f9e9fec12e465fb774a4483` (ранее зафиксировано в проекте) |
| Forester reference | `Forester_SG9_MAP_clean_v25.bin`, 524288 bytes, SH7055, `A2WC012E` / patched `A2WC0MME` |
| SHA-256 Forester v25 | `2ca539d0c47e3b1eec96c41e1e514c7b19b0e3786e9d826a41d3a3505b4c5d99` |
| Ghidra | 12.1.4 on Windows, custom `rimwall/Ghidra-HC16-Processor` (work in progress); manually added `Module.manifest` |
| ECUFlash | 1.44.4347; added `Carberry 4.2_Metric.xml` and `CarberryBASE_MAP.xml` (Crowley2012/SubaruTuning, ECUFlash/MAP Axis) |

Ghidra импорт: Raw Binary, language `HC-16:BE:16:default:default`, file offset zero mapped to address zero; initial block `0x000000–0x027FFF` renamed to `CarBerry_ROM`. Processor spec attempted to add RAM at `0x20000–0x27FFF`, conflicting with imported BIN. The BIN bytes remain available; that conflict **does not validate the RAM/ROM hardware map**. Default peripheral/IMB block `0xF0000–0xFFFFF`.

**ВАЖНО:** Скриншоты дизассемблирования подтверждают отображаемые инструкции и ссылки в установленном экспериментальном SLEIGH-модуле, но не абсолютную корректность всех его инструкций, контекста банков или анализа потоков. `XREF` из Ghidra проверять вручную.

## 2. XML-адрес ↔ file offset (отдельно от CPU runtime address)

ECUFlash успешно распознаёт BIN после добавления CarBerry 4.2 XML и CarBerryBASE. Некоторые XML адреса (например `0x29414`) больше размера 160-КБ BIN. Для **проверенной группы Tip-in** байты обнаруживаются при вычитании `0x8000`:

| Элемент | XML/CPU address в Ghidra | BIN/file offset | Свидетельство |
|---|---:|---:|---|
| Minimum Tip-in Activation (Throttle) | `0x293F8` | `0x213F8` | байты `82 04`, требуют аккуратного учёта типа оси |
| Minimum Tip-in Enrichment Activation | `0x293FA` | `0x213FA` | `00 60` (uint16 BE = 96, scaling `x*0.004` = **0.384 ms**) |
| Delta TPS axis | `0x29400` | `0x21400` | ось начинается `80 84 88 8C 90...` |
| Throttle Tip-in table | `0x29414` | `0x21414` | первые 18 uint8: `06 0E 16 1E 26 2D 34 3C 43 4C 53 59 60 63 64 64 64 64` |

Tip-in values scaling in base XML: `AdditionalInjectorPulseWidth(ms) = x * 0.032`; first values **0.192, 0.448, 0.704, 0.960 ms** etc., в ECUFlash округляются. Порог TPS в XML задаётся соответствующей шкалой `ThrottleAngleChange(%)` и оценивается около **1.63%**; при дальнейшей проверке необходимо подтвердить границы и размеры каждого элемента XML, а не предполагать, что `82 04` — одно uint16 значение.

Это соответствие `-0x8000` пока **не распространять без проверки** на весь BIN и все XML адреса. Не доказано, что образ «обрезан на 32 КиБ»: наличие 192-КБ адресного диапазона в XML само по себе этого не доказывает. **Не добавлять нули в BIN**.

Control signature at Ghidra/file address `0xFA68`:
`37 E5 10 80 37 EA 17 98 37 35 FF FF 37 6A 10 7E 27 F7` (совпала с предыдущим исследованием).

## 3. Reset / hardware init (контекст, НЕ переносить)

Стартовые векторы по данным Ghidra: `0x0: 02 20`, `0x2: 02 20`, `0x4: 07 F6`, `0x6: 00 00`; `0x8: 02 40`. По `0x220` — `7A 00 09 AA`, Ghidra: `JMP 0x09AA`. `0x09AA` содержит `ORP`, `ANDP`, `JMP 0x7144`. `0x7144` — системная инициализация (SCIMCR, SYNCR, RAMMCR, RAMBAH/RAMBAL, chip selects); адрес `0x240` содержит цикл `BRA 0x250` и похож на обработчик исключений. Это **аппаратно-зависимый код HC16**, не переносится в SH7055.

## 4. Tip-in: найденные кодовые участки (наблюдение по Ghidra)

### Путь вызовов

```text
FUN_000BA6
  ...
  0x000BE4: JSR FUN_00A164
  0x000BE8: JSR FUN_00A7C4  <- подтверждённая работа с порогами Tip-in
  0x000BEC: JSR FUN_00AC68
  ...
FUN_00A164:
  0xA164: JSR FUN_00A2B8
  0xA168: JSR FUN_00A314
  0xA16C: JSR FUN_00A2EE
  0xA170: RTS
FUN_00AC68:
  JSR FUN_00AA7E
  JSR FUN_00AA8C
  JSR FUN_00A9B2
  JSR FUN_00AC7E
  JSR FUN_00AC98
  RTS
```

Это **порядок вызовов**, а не доказанная частота исполнения и не доказанный поток данных между соседними функциями.

### FUN_00A7C4 — условные проверки и accumulation/reset

Наблюдаемые инструкции/операнды:

- `0xA7D6`: `CMPA 0x293FE,EK`;
- `0xA7EC`: `CMPA 0x293FF,EK`;
- `0xA7F2`: `CLRD`; `0xA7F4`: `STD 0x0B04,IZ` (**явное обнуление** при выполнении соответствующей ветки);
- `0xA802`: `CMPA 0x293F8,EK` (**TPS threshold**);
- `0xA80E`: `CMPB 0x293F9,EK` (пересекающийся адрес, семантика требует проверки);
- `0xA81C`: `LDD 0x0B04,IZ`; `0xA820`: `CPD 0x293FC,EK`;
- `0xA8B8`: `CPE 0x293FA,EK` (**minimum post-compensation pulse threshold**), далее `BCS 0xA90C`;
- `0xA8F2` и `0xA8FE`: `ADDD 0x0B04,IZ` (поиск байтов `0B 04` показал обе инструкции); `0xA908`: `STD 0x0B04,IZ`; `0xA90C`: `RTS`.

Участок `0xA872–0xA8B8` содержит умножение (`MUL`, `EMUL`), сдвиги, сравнение с `0x400`, обработку пределов `0xFFFF`. **Точные единицы измерения, арифметика и знаковость ещё не восстановлены.**

Промежуточное поле `0x0B04,IZ`: оно читается, обнуляется, складывается с новым значением и сохраняется. Обозначать как `tipin_accumulator_candidate`, **не** как окончательную команду на форсунки. `0xA90C` — общий `RTS`; проход к нему **не доказывает** нулевой импульс, поскольку значение может сохраняться.

### Другие процедуры

- `FUN_00A2B8`: обращение к `0x29141`, операции с `0x0AAA,IZ`, вероятно счётчик (точная семантика неизвестна).
- `FUN_00A2EE`: обращения к `0x29135`, `0x29139`, `0x2913F`; обновляет `0x0AAC,IZ`.
- `FUN_00A314`: `LDY #0x9160`; `LDD 0xF8,IZ`; `JSR FUN_008360`; затем `SUBA 0xE6,IZ`, `SUBA 0x29143,EK`, устанавливает/сбрасывает флаг `0x10` в `0xA9A,IZ`. **Это кандидат на обработку изменения сигнала, не подтверждённо TPS.**
- `FUN_008360` -> `FUN_00836E`: широко используемая процедура с индексной адресацией, условными ветками и вызовами `FUN_00844C`, `FUN_0084F4`, `FUN_00850C`. Возможно универсальное чтение/интерполяция; **не подтверждено**.
- `FUN_00AC68`: последующая последовательность обработчиков; на просмотренных участках `FUN_00AC7E`/`FUN_00AC98` нет прямой ссылки на `0x0B04,IZ`.
- `FUN_00A90E`: обращения к `0x29514` и `0x293F6`, возможная соседняя логика; связь с финальным впрыском не доказана.

## 5. Критически невыясненное

1. Реальное соответствие расширенных CPU адресов `0x29xxx` и файлового `0x21xxx`, настройка банков `EK`, физическая/логическая память.
2. Полная логика сравнения и направления ветвлений CPU16, контекст EK/IZ и перенос результата между D/E. Проверять по CPU16RM и при необходимости исправлять SLEIGH.
3. Раскладка `0x293F8–0x294xx` по XML с размерами типов, знаками и scale.
4. Семантика `0x0B04,IZ`, `0x0B02,IZ`, флагов `0xA9A/0xAFA`; где находится выдача отдельного injector firing.
5. Источник Delta TPS и частота исполнения диспетчера `FUN_000BA6`.
6. Сопоставление цепочки с исходной логикой MerpMod SH7055, расположение пригодного hook, footprint ROM/RAM.

## 6. Следующие действия

1. В Ghidra проверить `FUN_00844C` / `FUN_00850C` и контракт универсальной функции `FUN_008360`, не объявляя её табличной до доказательства.
2. Структурировать `FUN_00A7C4` в flowchart с RAM-полями, путями сброса, накопления, saturation и выходов.
3. Найти потребителя `0x0B04,IZ` через контекстный поиск индексных обращений/трассировку, а не только raw XREF.
4. Составить псевдокод и unit tests **вне ECU** с отдельно помеченными допущениями.
5. Только затем сверять с Forester v25/v84 и планировать порт. **Не изменять, не прошивать v84 до статической и стендовой проверки.**

См. также [sd-transient-fueling.md](sd-transient-fueling.md) и [merpmod-a2wc012e-address-map.md](merpmod-a2wc012e-address-map.md).

## 7. Update 2026-10-18: full Ghidra decompile of FUN_00A7C4, compensation calibration

Full decompiler output was supplied by the user for `FUN_00A7C4(ushort param_1)`. **Important:** this is *not* reference-quality C. HC16 SLEIGH/decompiler tracks banked registers, custom call conventions and return registers imperfectly (variables `extraout_A`, `undefined2`, apparently incorrect `iVar2` expression).

### Calibrations verified with ECUFlash / XML

- `0x29429` descriptor area / RPM table address `0x2942A`; visible RPM compensation: 800:-9.38%, 1200:-6.25%, >=1600:0% (at displayed RPM axis points).
- `0x29438` descriptor / Positive Boost Error table `0x29439`; values 0 and 1.24 psi: -50%, >=2.48 psi displayed: 0%.
- `0x29445` descriptor / ECT table `0x29446`; ECT -40:+221.88%, -30:+196.88%, -20:+171.88%, -10:+150%, 0:+125%, 10:+100%, 20:+78.12%, 30:+59.38%, 40:+40.62%, 50:+25%, 60:+15.62%, 70:+6.25%, >=80°C displayed: 0%.
- Both boost/ECT compensation tables use `ThrottleTip-inEnrichmentCompensation(%)1`, `uint8`, `raw*3.125 - 100`. 0% correction is a neutral compensation, **not necessarily zero injection**.
- `LDY #0x9429/#0x9438/#0x9445` preceding respective `FUN_008360` calls. Context `EK=2` at `0xA85C` in Ghidra, and `FUN_008360` begins `TEKB; TBXK; TBYK` (copies EK low nibble to banks). Corresponding banked addresses `0x29429/0x29438/0x29445`, nominal file offsets `0x21429/0x21438/0x21445`. Context `EK=2` is Ghidra inferred, runtime bank state remains to be proved.

### Key observations from decompiler (checked against earlier disassembly)

- `0x0B02` increments with saturation at 255; reset based on `0x293FF`.
- `0x0B01` reset based on `0x293FE`, incremented after successful threshold test.
- `0x0B04` zeroed depending on accumulated/reset condition, otherwise used in activation check against `0x293FC` and updated after accepted Tip-in pulse. **Better interpretation: cumulative throttle activity**, not directly injector output.
- Activation requires TPS delta against `0x293F8`, application counter against `0x293F9`, cumulative against `0x293FC`, and several bit flags. Some decompiled bitwise negation expressions are suspicious and must be reconciled with actual BSET/BRSET/BRCLR semantics.
- Three `FUN_008360` lookups: RPM at `0x9429` -> `0x0B09`; boost error at `0x9438` -> `0x0B08`; ECT at `0x9445` -> `0x0B0E`. Precise input unit/interpolation still not recovered.
- `FUN_00FF7C()` stores into `0x0B06`. Meaning and scaling unknown.
- `0x0B0A`: post-multiplication computed value, compared to `0x293FA` (=0.384 ms according to XML).
- On accepted result, saturating addition to `0x09A8` stored into `0x0B0C`, then `FUN_0027DC()` is called; this routine is a **priority next target** to verify separate injector firing / control.
- Following accepted event: increment `0x0B01`, reset `0x0B02`, and update `0x0B04` with branch-specific saturation/zero rules.

### Major arithmetic caveat

The decompiler emits `iVar2 = (uint)uVar4 * (uint)((uVar4 & 0xff) >> 2)` but assembly has `TDE; LDAA 0x0B0E,IZ; CLRB; LSRD; LSRD; EMUL` which clearly involves a **third operand read from `0x0B0E`**, omitted from the decompiler expression. It must not be used as-is in any Forester port. Reconstruct exact E/D register flow, multiplication, shifts and overflow handling using Motorola CPU16 instruction semantics.

### Revised status and priority

The Tip-in state machine and table **locations** are substantially established, not the validated mathematical model or injection actuator path. Before writing a Forester ROM patch:
1. inspect `FUN_0027DC` and the call chain to injector firing;
2. trace `FUN_00FF7C` to clarify `0x0B06`;
3. restore fixed-point arithmetic from `0xA872–0xA8B8` using register-by-register symbolic execution;
4. unit-test equivalent C code on a PC and verify behavior at threshold/overflow extremes.

## 8. Update 2026-10-18: FUN_002744 is confirmed TPU host-service interface

The user provided four 14-byte channel descriptors in ROM at 0x266A–0x26A1, and HC16 listing for `FUN_002744`. Channel index n=0..3 computes `X=0x266A + 14*n`.

| n | +0 | +2 | +4 | +6 | +8 | +A | +C | TPU channel |
|---|---|---|---|---|---|---|---|---|
| 0 | FF00 | 0002 | 0001 | 0001 | 0002 | FE1A | FE16 | 8 |
| 1 | FF10 | 0008 | 0004 | 0004 | 0008 | FE1A | FE16 | 9 |
| 2 | FF20 | 0020 | 0010 | 0010 | 0020 | FE1A | FE16 | 10 |
| 3 | FF30 | 0080 | 0040 | 0040 | 0080 | FE1A | FE16 | 11 |

All words big-endian. Datasheet MC68HC16Y1TS TPU map identifies `0xFFFE1A` as **HSRR1 (Host Service Request Register 1)** and `0xFFFE16` as **HSQR1 (Host Sequence Register 1)**. HSRR1 allocates two bits per channel 8..15: masks `1,4,0x10,0x40` select TPU8..TPU11 with request code 01 each. See https://www.nxp.com/docs/en/data-sheet/MC68HC16Y1TS.pdf and https://www.nxp.com/docs/en/application-note/TPUPN06.pdf.

In `FUN_002744`: bank X=0, select channel descriptor; bank Y=F and Y=FE00; `STE 0x1FE,IY` writes to physical `0xFFFFE` (TPU parameter RAM, channel 15 last word, likely shared staging/parameter data; semantics not yet identified). `LDD +4,IX` fetches request mask; `LDY +A,IX` gets register offset FE1A; `STD 0,IY` issues TPU host service request; poll until `LDD 0,IY == 0`. The poll indicates request serviced/cleared, **not** necessarily end of electrical injector pulse. P register temporarily modified and restored.

Previous thought that 4 channels were injector cylinders gains plausibility but **not proved**. These are definitely TPU channels 8,9,10,11; assigning them to injector outputs requires tracing TPU CFSR/HSQR/CPR initialization, parameter RAM FF00/FF10/FF20/FF30 layout, and board wiring or corroborating code. More importantly the actual channel function / microcode dictates what request code 01 does.

Next research: find code writing `0xFFFE0C..0xFFFE12` (CFSR0..3), `0xFFFE16` HSQR1, `0xFFFE1E` CPR1, and TPU parameter RAM for channels 8..11 (e.g. `0xFFFF80..0xFFFFBF` if channel indexing in standard 16-byte units; verify exact addressing). Locate other uses of descriptor +0/+2/+6/+8/+C. Avoid assuming raw Ghidra C accurately models banked I/O. No production ROM changes made.

# Tip-in v32: layout and checksum preflight (2026-10-20)

**OFFLINE ONLY — no ECU flash.**

## Verified from v25/v30 ROM comparison
- Both 524288 bytes. Original v25 SHA-256 `2ca539d0c47e3b1eec96c41e1e514c7b19b0e3786e9d826a41d3a3505b4c5d99`; v30 LAB SHA-256 `accd26e250cba8b8757718a6fdcb5aa2a080f3b7774a6712f9006c7515f2ff08`.
- Exact ROM internal ID `A2WC0MME` at `0x2000`; descriptive marker `STi SH7055SF` at `0x2010`.
- `0x1FFC` = `34 11 00 01`, which differs from a `31 91 00 05` signature mentioned by third-party SH7055-family documentation. Do not infer checksum family from the latter.
- v30 has exactly **15** differing byte offsets: `0x105C5..0x105C7` (pointer `0x105C4: 0x00024A04 → 0x0006AC40`) and `0x6AC40..0x6AC4B` (12-byte tail-jump wrapper).
- The baseline erased interval `[0x6AC3D,0x7FAF8)` is 85,691 bytes. `0x6AC40` is inside it; **FF is not proof of executable or safely unused memory**.
- There is populated code/data before the erased span near `0x6AC20` and populated tail data at `0x7FAF8`, `0x7FF00`, `0x7FFF8`. Never classify the entire ROM tail as blank.

## Checksum status
A correction/verification algorithm specific to **A2WC0MME** is **not established**. Generic byte/word sums are not Subaru checksums. OpenRemap documents SH7055 checksum layouts as CAL-ID dependent and provides no verified SH7055 checksums in its stated corpus. Other Subaru metadata examples include `subarudbw`, but are **not matched to this CAL ID**.

Sources:
- https://docs.openremap.com/manufacturers/denso/sh7055
- https://docs.openremap.com/checksum/cli
- https://minkara.carview.co.jp/group/openecu/bbs/2375979/

## Blocking items before bench flash
1. Retrieve and inspect **actual A2WC0MME EcuFlash metadata** (`checksummodule`, `flashmethod`, `memmodel`).
2. Independently validate SH7055SF CPU flash execute range and sectors: is `0x6AC40` physically fetchable, reserved, flashed, or covered by an integrity check?
3. Validate integrity using the actual target tool/loader scheme, including original v25, then modified v30; **no checksum was computed or corrected by this audit**.
4. Dynamic timing / PR-R2-context verification and spare-ECU recovery strategy still outstanding.

Run: `python3 tools/tipin-v32/audit_v32.py clean_v25.bin v30_LAB.bin`. Read-only; no modified firmware is produced.

# v33 — EcuFlash checksum behavior: empirical notes (2026-10-20)

**Research only; no flash-ready image.**

## User-run EcuFlash 1.44.4347 checks
- A new local EcuFlash XML was copied from `A2WC012E.xml` and only `xmlid`/`internalidstring` changed to `A2WC0MME`. It selects `flashmethod=sti04`, `memmodel=SH7055`, `checksummodule=subarudbw`. This is a **candidate XML**, not proven correct for `A2WC0MME`; `ecuid=3B02594316` remains copied from A2WC012E.
- EcuFlash logs: `checksum module "subarudbw" loaded.`, and for opened BINs `using metadata XML ID A2WC0MME`, read 524288 bytes.
- Saving clean v25 as a copy produced a byte-identical image.
- Saving v30 neutral hook as a copy produced a byte-identical image.
- A deliberately one-byte altered v25 image at `0x58DAB: 00 -> 01` opened without `Checksum Incorrect` warning; no writes were attempted. **This does not establish whether the checksum was disabled, deferred, excluded, or unchanged by this address.**
- Pinned hash clean v25: `2ca539d0c47e3b1eec96c41e1e514c7b19b0e3786e9d826a41d3a3505b4c5d99`.
- Hash v30: `accd26e250cba8b8757718a6fdcb5aa2a080f3b7774a6712f9006c7515f2ff08`.
- Probe hash: `0790a0888d7c1a1863d387055af9d87d995758cdea2885adab83a4f01a25eed6`.

## EcuFlash executable, offline observation
- User supplied EcuFlash 1.44 PE32 i386 `ecuflash.exe`.
- Static ASCII strings in EXE include `subarudbw`, `SubaruDBWChecksumModule`, `Checksum Incorrect`, and `The ROM you have loaded has one or more incorrect checksum values. Do you wish to correct them?`.
- Embedded strings confirm some checksum capability exists; **strings do not prove code path, algorithm, header addresses, or the applicability to A2WC0MME**.
- Source code for independent SH7055 flash utilities uses communication CRC, which must not be confused with the EcuFlash ROM fixup algorithm.

## Next analysis
Disassemble `SubaruDBWChecksumModule` in the EcuFlash EXE (or obtain authoritative module source), identify ROM region/table/flags and dispatch conditions. Verify a known-good original and a known-bad controlled offline image against the recovered algorithm before any decision on memory placement or on-ECU testing.

**Prohibition:** Do not flash the neutral v30, altered probe, or any test image on a running vehicle.

#!/usr/bin/env python3
"""Read-only v30 preflight for Forester clean v25; never writes a ROM."""
import csv
import hashlib
import pathlib
import struct
import sys

PIN="2ca539d0c47e3b1eec96c41e1e514c7b19b0e3786e9d826a41d3a3505b4c5d99"
SIZE=524288
ROOT=pathlib.Path(__file__).resolve().parent
def sha(data): return hashlib.sha256(data).hexdigest()
def verify(rom, rows):
    data=rom.read_bytes()
    assert len(data)==SIZE, "Incorrect ROM size"
    assert sha(data)==PIN, "Wrong firmware revision: original v25 SHA-256 mismatch"
    assert struct.unpack_from(">f", data, 0x58DA4)[0] > 0.19
    assert struct.unpack_from(">f", data, 0x58DA8)[0] == 250.0
    assert data[0x12AC:0x12AE] == bytes.fromhex("43 2E"), "VBR installation opcode mismatch"
    assert data[0x1364:0x1368] == bytes.fromhex("00 00 1F 4C"), "VBR literal mismatch"
    for row in rows:
        s=int(row["start"],16); e=int(row["end_exclusive"],16)
        assert e-s==int(row["size_bytes"]), row["name"]
        assert sha(data[s:e])==row["sha256"], "Region drift: "+row["name"]
        assert data[s:s+32]==bytes.fromhex(row["first_32_bytes"]), "First bytes drift: "+row["name"]
    print("PASS: pinned v25, VBR opcode/literal, 5 code regions; no writes")
    return data
def check_v26(original, path):
    lab=path.read_bytes()
    differences=[i for i,(a,b) in enumerate(zip(original,lab)) if a!=b]
    assert len(lab)==SIZE and differences==[0x58DA9], "Unexpected v26 modifications"
    assert struct.unpack_from(">f",lab,0x58DA8)[0]==200.0, "Unexpected v26 floor"
    print("PASS: v26 laboratory delta only at 0x58DA9; NOT for flash")
if __name__=="__main__":
    if len(sys.argv) not in (2,3):
        raise SystemExit("usage: verify_baseline.py clean_v25.bin [lab_v26.bin]")
    with (ROOT/"region_fingerprints.csv").open(newline="") as f:
        data=verify(pathlib.Path(sys.argv[1]),list(csv.DictReader(f)))
    if len(sys.argv)==3: check_v26(data,pathlib.Path(sys.argv[2]))

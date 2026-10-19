#!/usr/bin/env python3
"""Build a NON-FLASHABLE neutral tail-jump research sample from pinned v25."""
from pathlib import Path
import hashlib, struct, sys
PIN='2ca539d0c47e3b1eec96c41e1e514c7b19b0e3786e9d826a41d3a3505b4c5d99'
POINTER=0x105C4
OEM=0x24A04
ENTRY=0x6AC40
# SH2 big endian: MOV.L @(1,PC),R2; JMP @R2; NOP; NOP; literal OEM.
WRAPPER=bytes.fromhex('D2 01 42 2B 00 09 00 09 00 02 4A 04')

def sha(b): return hashlib.sha256(b).hexdigest()

def build(source: Path, out: Path):
    b=bytearray(source.read_bytes())
    assert len(b)==0x80000 and sha(b)==PIN, 'ROM not pinned clean v25'
    assert b[0x103F0:0x103F6]==bytes.fromhex('D2 74 42 0B 00 09')
    assert struct.unpack_from('>I',b,POINTER)[0]==OEM
    assert b[OEM:OEM+4]==bytes.fromhex('2F E6 2F D6')
    assert b[ENTRY:ENTRY+len(WRAPPER)]==b'\xff'*len(WRAPPER), 'site not FF'
    assert ((ENTRY+4)&~3)+4==ENTRY+8, 'PC-relative literal mismatch'
    original=bytes(b)
    b[ENTRY:ENTRY+len(WRAPPER)] = WRAPPER
    struct.pack_into('>I',b,POINTER,ENTRY)
    diffs=[i for i,(x,y) in enumerate(zip(original,b)) if x!=y]
    expected={POINTER+1,POINTER+2,POINTER+3} | set(range(ENTRY,ENTRY+len(WRAPPER)))
    assert set(diffs)==expected, ([hex(i) for i in diffs])
    assert b[0x103F0:0x103F6]==original[0x103F0:0x103F6]
    assert b[OEM:0x24B74]==original[OEM:0x24B74]
    assert b[0x58DA8:0x58DAC]==original[0x58DA8:0x58DAC]
    out.write_bytes(b)
    print('v25 SHA256:',sha(original),'LAB SHA256:',sha(b))
    print('15 modified byte offsets; never flash this lab image')

if __name__=='__main__':
    if len(sys.argv)!=3: raise SystemExit('usage: build_neutral_hook_lab.py v25.bin out_LAB.bin')
    build(Path(sys.argv[1]),Path(sys.argv[2]))

#!/usr/bin/env python3
"""Read-only byte-level boundary survey for pinned v25. NOT a checksum calculator."""
from pathlib import Path
import hashlib,sys
SHA='2ca539d0c47e3b1eec96c41e1e514c7b19b0e3786e9d826a41d3a3505b4c5d99'
SPANS=[(0x6AC20,0x6AC40),(0x7FAF0,0x7FB08),(0x7FF00,0x7FF30),(0x7FFF0,0x80000)]
def main(p):
 b=Path(p).read_bytes()
 assert len(b)==0x80000 and hashlib.sha256(b).hexdigest()==SHA
 assert b[0x6AC3D:0x7FAF8]==b'\xff'*(0x7FAF8-0x6AC3D)
 for a,z in SPANS:print(f'{a:06X}..{z-1:06X}  {b[a:z].hex(" ")}')
 print('A2WC0MME header:', b[0x2000:0x2008])
 print('Execution mapping: NOT VERIFIED; checksum routine: NOT IDENTIFIED')
if __name__=='__main__':
 if len(sys.argv)!=2:raise SystemExit('usage: survey_layout_v34.py clean_v25.bin')
 main(sys.argv[1])

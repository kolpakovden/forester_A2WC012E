#!/usr/bin/env python3
"""Offline checksum repair for pinned A2WC0MME v30 neutral LAB. Never flashes a vehicle."""
from pathlib import Path
import hashlib,struct,sys
MAGIC=0x5AA5A55A
PIN={'original':'2ca539d0c47e3b1eec96c41e1e514c7b19b0e3786e9d826a41d3a3505b4c5d99',
     'v30':'accd26e250cba8b8757718a6fdcb5aa2a080f3b7774a6712f9006c7515f2ff08'}
def hash_bytes(b):return hashlib.sha256(b).hexdigest()
def calc(b):
 assert len(b)==0x80000
 a,z,c=struct.unpack_from('>III',b,0x7FB80)
 assert (a,z)==(0x2000,0x7FAF7)
 assert all(struct.unpack_from('>III',b,0x7FB80+12*i)==(0,0,MAGIC) for i in range(1,17))
 s=sum(struct.unpack('>%dI'%((z+1-a)//4),b[a:z+1]))&0xffffffff
 return s,c,(s+c)&0xffffffff
def main(argv):
 if len(argv)!=4:raise SystemExit('usage: build_checksum_v41.py ORIGINAL_V25.bin NEUTRAL_V30.bin OUT_BENCH_ONLY.bin')
 a=Path(argv[1]).read_bytes();b=Path(argv[2]).read_bytes()
 assert hash_bytes(a)==PIN['original'] and hash_bytes(b)==PIN['v30']
 assert calc(a)==(0x344B7833,0x265A2D27,MAGIC)
 assert calc(b)==(0x065C66AA,0x265A2D27,0x2CB693D1)
 x=bytearray(b);struct.pack_into('>I',x,0x7FB88,(MAGIC-calc(b)[0])&0xffffffff)
 assert calc(x)==(0x065C66AA,0x54493EB0,MAGIC)
 assert hash_bytes(x)=='26e3f36ad835000286f85d896506825bea1e24be0167c28efae6a584d92fe13b'
 assert [i for i,(p,q) in enumerate(zip(b,x)) if p!=q]==list(range(0x7FB88,0x7FB8C))
 Path(argv[3]).write_bytes(x)
 print('CHECKSUM PASS. BENCH ONLY, NOT VALIDATED FOR ECU FLASH.')
if __name__=='__main__':main(sys.argv)

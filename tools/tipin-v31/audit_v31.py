#!/usr/bin/env python3
"""Read-only v31 static audit: NOT a checksum validator and NOT for flashing."""
import hashlib, struct, sys, json
from pathlib import Path

V25='2ca539d0c47e3b1eec96c41e1e514c7b19b0e3786e9d826a41d3a3505b4c5d99'
V30='accd26e250cba8b8757718a6fdcb5aa2a080f3b7774a6712f9006c7515f2ff08'
W=0x6ac40
P=0x105c4
OEM=0x24a04
CODE=bytes.fromhex('d2 01 42 2b 00 09 00 09 00 02 4a 04')
def sha(b):return hashlib.sha256(b).hexdigest()
def sums(b):return {'byte_sum_mod_65536':hex(sum(b)&0xffff),'be_word_sum_mod_65536':hex(sum(struct.unpack_from('>H',b,i)[0] for i in range(0,len(b),2))&0xffff),'be_dword_sum_mod_2pow32':hex(sum(struct.unpack_from('>I',b,i)[0] for i in range(0,len(b),4))&0xffffffff)}
def audit(a,b):
 assert len(a)==len(b)==0x80000
 assert sha(a)==V25 and sha(b)==V30,'Unexpected firmware hashes'
 assert a[0x103f0:0x103f6]==b'\xd2\x74\x42\x0b\x00\x09'
 assert b[0x103f0:0x103f6]==a[0x103f0:0x103f6]
 assert struct.unpack_from('>I',a,P)[0]==OEM
 assert struct.unpack_from('>I',b,P)[0]==W
 assert a[W:W+12]==b'\xff'*12 and b[W:W+12]==CODE
 assert a[OEM:0x24b74]==b[OEM:0x24b74]
 assert ((W+4)&~3)+4==W+8
 diffs=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
 assert set(diffs)==set(range(P+1,P+4))|set(range(W,W+12)),[hex(x) for x in diffs]
 start=W
 while start and a[start-1]==255:start-=1
 end=W
 while end<len(a) and a[end]==255:end+=1
 return {'status':'OFFLINE_ONLY_NOT_FLASHABLE','changed_bytes':len(diffs),'diff_offsets':[hex(i) for i in diffs],'wrapper':hex(W),'literal':hex(P),'oem':hex(OEM),'ff_run':{'start':hex(start),'end_exclusive':hex(end),'size_bytes':end-start},'checksums_NOT_ECU':{'v25':sums(a),'v30':sums(b)},'tail_32_equal':a[-32:]==b[-32:],'unverified':['ECU checksum algorithm','execute mapping for upper ROM','FF run allocation','runtime safety and timing']}
if __name__=='__main__':
 if len(sys.argv)!=3:raise SystemExit('usage: audit_v31.py v25.bin v30_LAB.bin')
 print(json.dumps(audit(Path(sys.argv[1]).read_bytes(),Path(sys.argv[2]).read_bytes()),indent=2))

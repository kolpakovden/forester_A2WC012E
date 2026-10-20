#!/usr/bin/env python3
"""Static PE string cross-reference locator; no execution, no ROM modification."""
import hashlib,struct,sys
from pathlib import Path
EXE_SHA='80ab6e185ac2383651b592751e0c9db1a7cf2cbe3c039e6363d90cdf7cea74dd'
SECTIONS=[('.text',0x400,0x74f1ce,0x401000),('.rdata',0x74f600,0x3152f7,0xb51000),('.data',0xa64a00,0x19000,0xe67000)]
TERMS=[b'subarudbw',b'SubaruDBWChecksumModule',b'Checksum Incorrect',b'WARNING: this ROM']
def addr(off):
 for n,start,size,va in SECTIONS:
  if start<=off<start+size:return va+off-start,n
 return None,None
def main(p):
 b=Path(p).read_bytes()
 assert hashlib.sha256(b).hexdigest()==EXE_SHA,'Unexpected ecuflash.exe; this script is version pinned'
 for term in TERMS:
  cursor=0
  while True:
   off=b.find(term,cursor)
   if off<0:break
   va,sec=addr(off)
   needle=struct.pack('<I',va) if va else b''
   refs=[]
   if needle:
    t=b.find(needle)
    while t!=-1:
     rva,rs=addr(t)
     refs.append({'file_offset':hex(t),'virtual_address':hex(rva) if rva else None,'section':rs})
     t=b.find(needle,t+1)
   print({'term':term.decode(),'file_offset':hex(off),'va':hex(va) if va else None,'section':sec,'absolute_pointer_refs':refs})
   cursor=off+1
if __name__=='__main__':
 if len(sys.argv)!=2:raise SystemExit('usage: xrefs_v35.py path/to/ecuflash.exe')
 main(sys.argv[1])

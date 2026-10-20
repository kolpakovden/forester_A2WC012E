#!/usr/bin/env python3
"""Pinned read-only PE pointer survey, NOT a checksum algorithm."""
from pathlib import Path
import hashlib,struct,sys,json
SHA="80ab6e185ac2383651b592751e0c9db1a7cf2cbe3c039e6363d90cdf7cea74dd"
SECTION=[("text",0x400,0x74f1ce,0x401000),("rdata",0x74f600,0x3152f7,0xb51000),("data",0xa64a00,0x19000,0xe67000)]
QUERIES={"module_ascii":b"subarudbw","class_ascii":b"SubaruDBWChecksumModule",
         "incorrect_title":b"Checksum Incorrect"}
def va_at(offset):
 for name,fo,size,va in SECTION:
  if fo<=offset<fo+size:return va+offset-fo,name
 return None,None
def scan_all(b,pattern):
 result=[];at=0
 while True:
  at=b.find(pattern,at)
  if at<0:return result
  result.append(at);at+=1
def run(path):
 b=Path(path).read_bytes()
 assert len(b)==11370696 and hashlib.sha256(b).hexdigest()==SHA
 report={}
 for name,pattern in QUERIES.items():
  places=[]
  for off in scan_all(b,pattern):
   va,sec=va_at(off)
   absolute=scan_all(b,struct.pack("<I",va)) if va else []
   places.append({"offset":hex(off),"va":hex(va) if va else None,"section":sec,
                  "absolute_refs":[{"offset":hex(j),"va":hex(va_at(j)[0]) if va_at(j)[0] else None} for j in absolute]})
  report[name]=places
 # The contiguous-looking table is a CANDIDATE only. Do not call it SubaruDBW vtable.
 report["nearby_candidate_pointer_words"]=[
  {"va":hex(0xb51f80+4*i),"value":hex(struct.unpack_from("<I",b,0x750580+4*i)[0])} for i in range(12)]
 report["algorithm_recovered"]=False
 report["checksum_validated_for_A2WC0MME"]=False
 print(json.dumps(report,indent=2))
if __name__=="__main__":
 if len(sys.argv)!=2:raise SystemExit("usage: pe_candidate_survey_v36.py ecuflash.exe")
 run(sys.argv[1])

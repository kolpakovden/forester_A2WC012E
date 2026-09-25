#!/usr/bin/env python3
"""Materialize A2WC0MME v85 FFS Spark Cut from the exact v84 base ROM."""
from pathlib import Path
import argparse, hashlib
EXPECTED_SIZE=524288
EXPECTED_BASE_SHA256="30b1994039775bbef362bcd166d6fcfbde3d618585115a7a44edeb53f3bae278"
EXPECTED_OUTPUT_SHA256="61e7802c2f6594ccc8046c72c0fbd1d31fdbec62c79dfc3a900bf0b19d3f6d57"
PATCHES=[
(0xA13A,"b100"),(0x1132E,"b0"),(0x6ADC8,"02"),
(0x6B000,"4f22d322430b0009d121601088028b1cd120601220088b06d22060222102d11ed21f60222102d11f6012d21c2202d21c2202d11d6012d21b632233068b22d11b6010c97f2100a01d0009e000d1112102d1112102d116601020088913d115601088018b0fd10f6012d20c2202d20c2202d10d6012d20b632233068b03d10b6010c97f21004f26000b00090009000228c4"),
(0x6B092,"ca3c"),(0x6B096,"ca7c"),(0x6B09A,"ca80"),(0x6B09E,"ca44"),(0x6B0A2,"ca48"),(0x6B0A6,"ca4c"),(0x6B0AA,"b218"),(0x6B0AE,"b868"),(0x6B0B2,"ca3b0006adc4"),
(0x6B100,"d029e10020108f4c63d33348633f43118d0163536d43336c523122d16d23d0236100601388028b0bd0216102d021620222288b01d020620231268b2fa00e0009d01e610021188929d01d600088018b25d0176102d01b620231268b1fd01a670027788b00e701d01962003726890ad00ee1012010e00362e35132302c21012d21a00000097701d01262002228890137268b00e701d00c2070a0030009e701d00a2070000b00090009"),
(0x6B1AA,"ca78"),(0x6B1AE,"ca3c"),(0x6B1B2,"b218"),(0x6B1B6,"ca7c"),(0x6B1BA,"ca44"),(0x6B1BE,"ca3b0006adc40006a4f0"),(0x6B1CA,"ca790006adc80006adcc")]
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--input",required=True,type=Path); ap.add_argument("--output",required=True,type=Path); a=ap.parse_args()
 src=a.input.read_bytes()
 if len(src)!=EXPECTED_SIZE: raise SystemExit(f"bad size: {len(src)}")
 got=hashlib.sha256(src).hexdigest()
 if got!=EXPECTED_BASE_SHA256: raise SystemExit(f"bad v84 SHA256: {got}")
 if src[0x2000:0x2008]!=b"A2WC0MME": raise SystemExit("bad internal ID")
 dst=bytearray(src)
 for off,h in PATCHES:
  data=bytes.fromhex(h); dst[off:off+len(data)]=data
 sha=hashlib.sha256(dst).hexdigest()
 if sha!=EXPECTED_OUTPUT_SHA256: raise SystemExit(f"output hash mismatch: {sha}")
 a.output.write_bytes(dst); print(f"{sha}  {a.output}")
if __name__=="__main__": main()

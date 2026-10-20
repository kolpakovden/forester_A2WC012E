#!/usr/bin/env python3
from pathlib import Path
import hashlib
root=Path(__file__).resolve().parents[2]
p=root/'work2_100+95_3D04EA4605_CarBerry42_FULL_160KiB.bin'
b=p.read_bytes()
assert hashlib.sha256(b).hexdigest()=='b06e1282a4b274db856d250ae8a1babaf175729f7f9e9fec12e465fb774a4483'
for a,hexval in [(0x4e58,'176517da'),(0x4e5c,'176a17d9'),(0x6d5c,'176a17d9'),(0xa7d0,'17e517d9'),(0xa7fe,'176517d9')]:
 assert b[a:a+4]==bytes.fromhex(hexval)
 print(hex(a),b[a:a+4].hex())
print('OFFLINE ONLY. Indexed IZ base / bank context remains unverified.')

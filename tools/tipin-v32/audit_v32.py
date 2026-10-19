#!/usr/bin/env python3
"""Read-only Forester Tip-in v32 audit, not flash authorization."""
import hashlib,json,struct,sys
from pathlib import Path
A='2ca539d0c47e3b1eec96c41e1e514c7b19b0e3786e9d826a41d3a3505b4c5d99'
B='accd26e250cba8b8757718a6fdcb5aa2a080f3b7774a6712f9006c7515f2ff08'
def audit(a,b):
 assert len(a)==len(b)==524288
 assert hashlib.sha256(a).hexdigest()==A and hashlib.sha256(b).hexdigest()==B
 assert a[0x2000:0x2008]==b'A2WC0MME'
 assert a[0x2010:0x201C]==b'STi SH7055SF'
 assert a[0x103F0:0x103F6]==b[0x103F0:0x103F6]==bytes.fromhex('D2 74 42 0B 00 09')
 assert struct.unpack_from('>I',a,0x105C4)[0]==0x24A04
 assert struct.unpack_from('>I',b,0x105C4)[0]==0x6AC40
 assert a[0x6AC40:0x6AC4C]==b'\xff'*12
 assert b[0x6AC40:0x6AC4C]==bytes.fromhex('D2 01 42 2B 00 09 00 09 00 02 4A 04')
 assert a[0x6AC3D:0x7FAF8]==b'\xff'*(0x7FAF8-0x6AC3D)
 ds=[i for i,(u,v) in enumerate(zip(a,b)) if u!=v]
 assert set(ds)==set(range(0x105C5,0x105C8))|set(range(0x6AC40,0x6AC4C))
 return {'result':'PASS_STATIC_ONLY','diff_count':len(ds),'ff_range':['0x6AC3D','0x7FAF8'],'rom_id':'A2WC0MME','cpu_label':'STi SH7055SF','header_0x1FFC':a[0x1FFC:0x2000].hex(' '),'populated_tail_hex':{'0x7FAF8':a[0x7FAF8:0x7FB00].hex(' '),'0x7FF00':a[0x7FF00:0x7FF20].hex(' '),'0x7FFF8':a[0x7FFF8:0x80000].hex(' ')},'checksum_verified':False,'execute_region_verified':False,'ready_for_flash':False}
if __name__=='__main__':
 if len(sys.argv)!=3:raise SystemExit('usage: audit_v32.py v25.bin v30_LAB.bin')
 print(json.dumps(audit(Path(sys.argv[1]).read_bytes(),Path(sys.argv[2]).read_bytes()),indent=2))

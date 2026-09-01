from pathlib import Path
import argparse, struct, hashlib, xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(description='Build A2WC012E v68 experimental LC spark-cut ROMs and RomRaider definition from v67.')
parser.add_argument('--input', required=True, type=Path, help='v67 input BIN')
parser.add_argument('--definition', required=True, type=Path, help='v64 Advanced LC RomRaider definition')
parser.add_argument('--out-dir', required=True, type=Path, help='output directory')
args = parser.parse_args()
args.out_dir.mkdir(parents=True, exist_ok=True)
INP = args.input
DEF_IN = args.definition
OUT_SAFE = args.out_dir / 'forester_sg9_sti_MAP_IAT_GM_dMap_v68_SPARK_CUT_SAFE.bin'
OUT_TEST = args.out_dir / 'forester_sg9_sti_MAP_IAT_GM_dMap_v68_SPARK_CUT_ENABLED.bin'
REPORT = args.out_dir / 'forester_sg9_sti_MAP_IAT_GM_dMap_v68_SPARK_CUT_report.txt'
DEF_OUT = args.out_dir / 'ecu_defs_A2WC012E_MerpMod_DMAP_ADV_LC_SPARK_v68.xml'

ROM_SIZE=524288
# Existing validated Advanced LC addresses
H_POLF=0x1132C
OLD_POLF_WRAPPER=0x6AD50
NEW_POLF_WRAPPER=0x6AE00
H_TIMING=0x113D8
TIMING_WRAPPER=0x6AD90
TIMING_TARGET=0x6ADBC

# New calibration words (first byte used for uint8 fields)
CUT_MODE=0x6ADC4      # 0 = current MerpMod fuel cut; 1 = experimental spark cut
SPARK_EVENTS_CUT=0x6ADC8
SPARK_EVENTS_CYCLE=0x6ADCC

# Ignition scheduler hooks, reverse-engineered from A2WC012E binary and matched to Merp SparkHacks OEM sequences
OCR_SITE_START=0xA126
OCR_SITE_END=0xA13E  # exclusive; continuation is A13E
GR_SITE_START=0xA188
GR_SITE_END=0xA1A0   # exclusive; original BRA target is A1E4
OCR_ROUTINE=0x6AE80
GR_ROUTINE=0x6AF40

# Existing ROM / RAM addresses
OEM_POLF=0x000228C4
LC_ENGAGED_RAM=0xFFFFCA3B
ENGINE_SPEED_RAM=0xFFFFB218
FLAGS_REVLIM_RAM=0xFFFFB868
REDLINE_ROM=0x0006A4D0
LAUNCH_CUT_ROM=0x0006A4F0
FUEL_MODE=0x0006AD78
FUEL_TARGET=0x0006AD7C
P_POLF_ENRICH=0xFFFFB6E8

# Two bytes immediately after known Gratis RevLimiter RAM variables (last exposed float ends at CA74 +4)
SPARK_CURRENT_CUT_RAM=0xFFFFCA78
SPARK_EVENT_COUNTER_RAM=0xFFFFCA79

EXPECTED_OCR = bytes.fromhex('8f0a000963d33348633f43118d0163536d43336c523122d1')
EXPECTED_GR = bytes.fromhex('62e33248622f42118d01e0016e43356c80765352a02223e1')

class Asm:
    def __init__(self, origin):
        self.origin=origin; self.buf=bytearray(); self.labels={}; self.fixups=[]
    @property
    def pc(self): return self.origin+len(self.buf)
    def label(self,n):
        if n in self.labels: raise ValueError('duplicate '+n)
        self.labels[n]=self.pc
    def w(self,x): self.buf += int(x & 0xffff).to_bytes(2,'big')
    def nop(self): self.w(0x0009)
    def rts(self): self.w(0x000B)
    def mov_imm(self,n,imm): self.w(0xE000 | ((n&15)<<8) | (imm&0xff))
    def mov_reg(self,m,n): self.w(0x6003 | ((n&15)<<8) | ((m&15)<<4))
    def movb_at(self,m,n): self.w(0x6000 | ((n&15)<<8) | ((m&15)<<4))
    def movw_at(self,m,n): self.w(0x6001 | ((n&15)<<8) | ((m&15)<<4))
    def movl_at(self,m,n): self.w(0x6002 | ((n&15)<<8) | ((m&15)<<4))
    def movb_to_at(self,m,n): self.w(0x2000 | ((n&15)<<8) | ((m&15)<<4))
    def movw_to_at(self,m,n): self.w(0x2001 | ((n&15)<<8) | ((m&15)<<4))
    def movl_to_at(self,m,n): self.w(0x2002 | ((n&15)<<8) | ((m&15)<<4))
    def movl_disp(self,m,n,disp):
        assert disp%4==0 and 0 <= disp//4 <= 15
        self.w(0x5000 | ((n&15)<<8) | ((m&15)<<4) | (disp//4))
    def movb_r0_disp(self,n,disp):
        assert 0<=disp<=15
        self.w(0x8000 | ((n&15)<<4) | disp)
    def sub(self,m,n): self.w(0x3008 | ((n&15)<<8) | ((m&15)<<4))
    def add(self,m,n): self.w(0x300C | ((n&15)<<8) | ((m&15)<<4))
    def add_imm(self,n,imm): self.w(0x7000 | ((n&15)<<8) | (imm&0xff))
    def exts_w(self,m,n): self.w(0x600F | ((n&15)<<8) | ((m&15)<<4))
    def cmp_pz(self,n): self.w(0x4011 | ((n&15)<<8))
    def cmp_hi(self,m,n): self.w(0x3006 | ((n&15)<<8) | ((m&15)<<4))
    def tst(self,m,n): self.w(0x2008 | ((n&15)<<8) | ((m&15)<<4))
    def cmp_eq_imm_r0(self,imm): self.w(0x8800 | (imm&0xff))
    def and_imm_r0(self,imm): self.w(0xC900 | (imm&0xff))
    def or_imm_r0(self,imm): self.w(0xCB00 | (imm&0xff))
    def jsr(self,n): self.w(0x400B | ((n&15)<<8))
    def jmp(self,n): self.w(0x402B | ((n&15)<<8))
    def sts_l_pr_predec_r15(self): self.w(0x4F22)
    def lds_l_postinc_r15_pr(self): self.w(0x4F26)
    def branch8(self,kind,label):
        op={'bt':0x8900,'bf':0x8B00,'bt/s':0x8D00,'bf/s':0x8F00}[kind]
        pos=self.pc; self.w(op); self.fixups.append(('b8',pos,label,op))
    def bra(self,label):
        pos=self.pc; self.w(0xA000); self.fixups.append(('b12',pos,label,0xA000))
    def movl_pc(self,n,label):
        pos=self.pc; self.w(0xD000 | ((n&15)<<8)); self.fixups.append(('movlpc',pos,label,n))
    def align4(self):
        while self.pc%4: self.nop()
    def data32(self,label,val):
        self.align4(); self.label(label); self.buf += int(val & 0xffffffff).to_bytes(4,'big')
    def resolve(self):
        for typ,pos,label,base in self.fixups:
            if label not in self.labels: raise KeyError(label)
            tgt=self.labels[label]; off=pos-self.origin
            if typ=='b8':
                d=(tgt-(pos+4))//2
                if tgt != pos+4+d*2 or not -128<=d<=127: raise ValueError((typ,hex(pos),label,hex(tgt),d))
                w=base | (d & 0xff)
            elif typ=='b12':
                d=(tgt-(pos+4))//2
                if tgt != pos+4+d*2 or not -2048<=d<=2047: raise ValueError((typ,hex(pos),label,hex(tgt),d))
                w=base | (d & 0xfff)
            else:
                pcbase=(pos+4)&~3
                diff=tgt-pcbase
                if diff%4 or not 0<=diff//4<=255: raise ValueError((typ,hex(pos),label,hex(tgt),diff))
                w=0xD000 | ((base&15)<<8) | (diff//4)
            self.buf[off:off+2]=w.to_bytes(2,'big')
        return bytes(self.buf)


def build_polf():
    a=Asm(NEW_POLF_WRAPPER)
    a.sts_l_pr_predec_r15()
    a.movl_pc(3,'oem_polf'); a.jsr(3); a.nop()
    # If LC is not engaged, no custom LC work.
    a.movl_pc(1,'lc_eng_ptr'); a.movb_at(1,0); a.tst(0,0); a.branch8('bt','done')
    # In spark mode, clear only the rev-limit fuel-cut bit while below hard redline.
    a.movl_pc(1,'cut_mode_ptr'); a.movb_at(1,0); a.cmp_eq_imm_r0(1); a.branch8('bf','fuel_override')
    a.movl_pc(1,'engine_speed_ptr'); a.movl_at(1,0)
    a.movl_pc(2,'redline_ptr'); a.movl_at(2,3)
    # cmp/hi r0,r3 => T=1 when redline > rpm; never suppress hard-redline fuel cut.
    a.cmp_hi(0,3); a.branch8('bf','fuel_override')
    a.movl_pc(1,'flags_revlim_ptr'); a.movb_at(1,0); a.and_imm_r0(0x7F); a.movb_to_at(0,1)
    a.label('fuel_override')
    a.movl_pc(1,'fuel_mode_ptr'); a.movb_at(1,0); a.tst(0,0); a.branch8('bt','done')
    a.movl_pc(1,'fuel_target_ptr'); a.movl_at(1,0)
    a.movl_pc(2,'p_polf_enrich'); a.movl_to_at(0,2)
    a.label('done')
    a.lds_l_postinc_r15_pr(); a.rts(); a.nop()
    a.data32('oem_polf',OEM_POLF)
    a.data32('lc_eng_ptr',LC_ENGAGED_RAM)
    a.data32('cut_mode_ptr',CUT_MODE)
    a.data32('engine_speed_ptr',ENGINE_SPEED_RAM)
    a.data32('redline_ptr',REDLINE_ROM)
    a.data32('flags_revlim_ptr',FLAGS_REVLIM_RAM)
    a.data32('fuel_mode_ptr',FUEL_MODE)
    a.data32('fuel_target_ptr',FUEL_TARGET)
    a.data32('p_polf_enrich',P_POLF_ENRICH)
    return a.resolve(),a


def build_ocr():
    a=Asm(OCR_ROUTINE)
    # Avoid a stale per-event flag even if original BF/S exits immediately. MOVs don't alter T.
    a.movl_pc(0,'cur_cut_ptr'); a.mov_imm(1,0); a.movb_to_at(1,0)
    # Reproduce OEM A126-A13C exactly in semantics, including incoming T branch behavior.
    a.branch8('bf/s','done'); a.mov_reg(13,3)
    a.sub(4,3); a.exts_w(3,3); a.cmp_pz(3)
    a.branch8('bt/s','not_reached'); a.mov_reg(5,3)
    a.mov_reg(4,13)
    a.label('not_reached')
    a.add(6,3); a.movl_disp(3,2,4); a.movw_to_at(13,2)
    # Keep OCR address in r13 like Merp's experimental SparkHacks implementation.
    a.mov_reg(2,13)
    # Spark cut only when existing LC signal is active AND new mode == 1.
    a.movl_pc(0,'lc_eng_ptr'); a.movb_at(0,1); a.tst(1,1); a.branch8('bt','reset_counter')
    a.movl_pc(0,'cut_mode_ptr'); a.movb_at(0,0); a.cmp_eq_imm_r0(1); a.branch8('bf','reset_counter')
    # Positive IEEE-754 float bit patterns preserve ordering; compare RPM and launch cut as uint32.
    a.movl_pc(0,'engine_speed_ptr'); a.movl_at(0,1)
    a.movl_pc(0,'launch_cut_ptr'); a.movl_at(0,2)
    a.cmp_hi(2,1); a.branch8('bf','reset_counter')
    # Get 1-based event counter.
    a.movl_pc(0,'event_counter_ptr'); a.movb_at(0,7)
    # If RAM was never initialized, start at event 1.
    a.tst(7,7); a.branch8('bf','counter_ok'); a.mov_imm(7,1)
    a.label('counter_ok')
    # Cut first N events of each cycle.
    a.movl_pc(0,'events_cut_ptr'); a.movb_at(0,2)
    a.cmp_hi(2,7); a.branch8('bt','no_cut_event')  # counter > N => fire normally
    # Mark this event cut.
    a.movl_pc(0,'cur_cut_ptr'); a.mov_imm(1,1); a.movb_to_at(1,0)
    # Merp SparkHacks method: collapse OCR/GR timing to suppress coil dwell/spark event.
    a.mov_imm(0,3); a.mov_reg(14,2); a.movl_disp(3,1,8); a.add(2,0); a.movw_to_at(0,1); a.movw_to_at(2,13)
    a.bra('update_counter'); a.nop()
    a.label('no_cut_event')
    # cur_cut already zero from function entry.
    a.label('update_counter')
    a.add_imm(7,1)
    a.movl_pc(0,'cycle_ptr'); a.movb_at(0,2)
    # cycle=0 is invalid; fail safe by resetting to 1 rather than locking cut continuously.
    a.tst(2,2); a.branch8('bt','counter_reset_to_one')
    a.cmp_hi(2,7); a.branch8('bf','counter_store')
    a.label('counter_reset_to_one'); a.mov_imm(7,1)
    a.label('counter_store'); a.movl_pc(0,'event_counter_ptr'); a.movb_to_at(7,0)
    a.bra('done'); a.nop()
    a.label('reset_counter')
    a.mov_imm(7,1); a.movl_pc(0,'event_counter_ptr'); a.movb_to_at(7,0)
    a.label('done'); a.rts(); a.nop()
    a.data32('cur_cut_ptr',SPARK_CURRENT_CUT_RAM)
    a.data32('lc_eng_ptr',LC_ENGAGED_RAM)
    a.data32('cut_mode_ptr',CUT_MODE)
    a.data32('engine_speed_ptr',ENGINE_SPEED_RAM)
    a.data32('launch_cut_ptr',LAUNCH_CUT_ROM)
    a.data32('event_counter_ptr',SPARK_EVENT_COUNTER_RAM)
    a.data32('events_cut_ptr',SPARK_EVENTS_CUT)
    a.data32('cycle_ptr',SPARK_EVENTS_CYCLE)
    return a.resolve(),a


def build_gr():
    a=Asm(GR_ROUTINE)
    # Same first-side-effect as Merp experimental hook: set OEM post-GR flag.
    a.mov_imm(0,1); a.movb_r0_disp(7,6)
    a.movl_pc(0,'cur_cut_ptr'); a.movb_at(0,1); a.tst(1,1); a.branch8('bf','done')
    # Normal OEM A188-A19E semantics (branch at A19C is handled by the site stub after return).
    a.mov_reg(14,2); a.sub(4,2); a.exts_w(2,2); a.cmp_pz(2)
    a.branch8('bt/s','gr_not_reached'); a.nop()
    a.mov_reg(4,14)
    a.label('gr_not_reached')
    a.add(6,5); a.movl_disp(5,3,8); a.movw_to_at(14,3)
    a.label('done'); a.rts(); a.nop()
    a.data32('cur_cut_ptr',SPARK_CURRENT_CUT_RAM)
    return a.resolve(),a


def make_site_stub(start,end,routine,return_target,literal_at):
    size=end-start
    out=bytearray(b'\x00\x09'*(size//2))
    base=(start+4)&~3
    assert (literal_at-base)%4==0
    disp=(literal_at-base)//4
    assert 0<=disp<=255
    out[0:2]=(0xD300|disp).to_bytes(2,'big') # mov.l routine,r3
    out[2:4]=(0x430B).to_bytes(2,'big')       # jsr @r3
    out[4:6]=(0x0009).to_bytes(2,'big')       # nop delay
    pc=start+6
    d=(return_target-(pc+4))//2
    assert return_target==pc+4+d*2 and -2048<=d<=2047
    out[6:8]=(0xA000|(d&0xfff)).to_bytes(2,'big')
    out[8:10]=(0x0009).to_bytes(2,'big')
    li=literal_at-start
    out[li:li+4]=routine.to_bytes(4,'big')
    return bytes(out)


def diff_regions(a,b):
    ds=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
    gs=[]
    if ds:
        s=p=ds[0]
        for x in ds[1:]:
            if x==p+1: p=x
            else: gs.append((s,p)); s=p=x
        gs.append((s,p))
    return ds,gs

b=INP.read_bytes()
assert len(b)==ROM_SIZE
assert b[0x2000:0x2008]==b'A2WC0MME'
assert int.from_bytes(b[H_POLF:H_POLF+4],'big')==OLD_POLF_WRAPPER, hex(int.from_bytes(b[H_POLF:H_POLF+4],'big'))
assert int.from_bytes(b[H_TIMING:H_TIMING+4],'big')==TIMING_WRAPPER
assert b[OCR_SITE_START:OCR_SITE_END]==EXPECTED_OCR, b[OCR_SITE_START:OCR_SITE_END].hex()
assert b[GR_SITE_START:GR_SITE_END]==EXPECTED_GR, b[GR_SITE_START:GR_SITE_END].hex()
# New region must be blank in v67.
assert set(b[CUT_MODE:0x6B000]) == {0xFF}, 'new custom area is not blank'

polf,polfasm=build_polf(); ocr,ocrasm=build_ocr(); gr,grasm=build_gr()
print('sizes',len(polf),len(ocr),len(gr))
assert NEW_POLF_WRAPPER+len(polf) <= OCR_ROUTINE
assert OCR_ROUTINE+len(ocr) <= GR_ROUTINE
assert GR_ROUTINE+len(gr) < 0x6B000

rom=bytearray(b)
# Keep current Advanced LC fuel/timing enabled from v67, but return tested timing lock from -5 to -2 deg.
rom[TIMING_TARGET:TIMING_TARGET+4]=struct.pack('>f',-2.0)
# New LC cut controls. Safe defaults to existing fuel-cut mode.
rom[CUT_MODE:CUT_MODE+4]=bytes([0,0,0,0])
rom[SPARK_EVENTS_CUT:SPARK_EVENTS_CUT+4]=bytes([3,0,0,0])
rom[SPARK_EVENTS_CYCLE:SPARK_EVENTS_CYCLE+4]=bytes([5,0,0,0])
# Redirect POLF to enhanced wrapper that suppresses only LC fuel-cut bit in spark mode below hard redline.
rom[H_POLF:H_POLF+4]=NEW_POLF_WRAPPER.to_bytes(4,'big')
rom[NEW_POLF_WRAPPER:NEW_POLF_WRAPPER+len(polf)]=polf
# Hook ignition scheduler with local JSR stubs; mode 0 is pass-through OEM semantics.
ocr_stub=make_site_stub(OCR_SITE_START,OCR_SITE_END,OCR_ROUTINE,OCR_SITE_END,0xA138)
gr_stub=make_site_stub(GR_SITE_START,GR_SITE_END,GR_ROUTINE,0xA1E4,0xA198)
rom[OCR_SITE_START:OCR_SITE_END]=ocr_stub
rom[GR_SITE_START:GR_SITE_END]=gr_stub
rom[OCR_ROUTINE:OCR_ROUTINE+len(ocr)]=ocr
rom[GR_ROUTINE:GR_ROUTINE+len(gr)]=gr

# Core integrity checks
assert rom[0x6AC40:0x6AD44] == b[0x6AC40:0x6AD44]  # DMAP table/code through return literal untouched
# Existing Advanced LC block is preserved except for the intentional -5 -> -2 deg timing target change.
assert rom[0x6AD50:TIMING_TARGET] == b[0x6AD50:TIMING_TARGET]
assert rom[TIMING_TARGET+4:0x6ADC4] == b[TIMING_TARGET+4:0x6ADC4]
assert struct.unpack('>f',rom[TIMING_TARGET:TIMING_TARGET+4])[0] == -2.0
assert int.from_bytes(rom[H_POLF:H_POLF+4],'big')==NEW_POLF_WRAPPER
assert int.from_bytes(rom[H_TIMING:H_TIMING+4],'big')==TIMING_WRAPPER
# Ordinary redline's RevLimiter code and fuel-bit operations remain byte-for-byte unchanged.
assert rom[0x25758:0x25840] == b[0x25758:0x25840]
# OEM code around hooks outside replaced blocks unchanged.
assert rom[0xA100:OCR_SITE_START]==b[0xA100:OCR_SITE_START]
assert rom[OCR_SITE_END:GR_SITE_START]==b[OCR_SITE_END:GR_SITE_START]
assert rom[GR_SITE_END:0xA220]==b[GR_SITE_END:0xA220]

OUT_SAFE.write_bytes(rom)
rom_test=bytearray(rom); rom_test[CUT_MODE]=1
OUT_TEST.write_bytes(rom_test)

# Definition update: add abstract tables once and physical A2WC0MME mappings once.
tree=ET.parse(DEF_IN); root=tree.getroot()
parents={c:p for p in root.iter() for c in p}
fuel_abs=None
for t in root.iter('table'):
    if t.get('name')=='LC Advanced Fuel Mode' and t.get('storageaddress') is None:
        fuel_abs=t; break
if fuel_abs is None: raise RuntimeError('abstract LC Advanced Fuel Mode not found')
abs_parent=parents[fuel_abs]
existing_abs={t.get('name') for t in abs_parent.findall('table')}

def add_abs(name,units,desc,axis):
    if name in existing_abs: return
    t=ET.Element('table', {'type':'2D','name':name,'category':'MerpMod - Launch Control Advanced','storagetype':'uint8','endian':'big','sizey':'1','userlevel':'1'})
    ET.SubElement(t,'scaling', {'units':units,'expression':'x','to_byte':'x','format':'#','fineincrement':'1','coarseincrement':'1'})
    ay=ET.SubElement(t,'table', {'type':'Static Y Axis','name':'Advanced Launch Control'})
    ET.SubElement(ay,'data').text=axis
    ET.SubElement(t,'description').text=desc
    abs_parent.append(t)

add_abs('LC Cut Mode','Mode (0=Fuel, 1=Spark)','0 = existing MerpMod fuel-cut launch limiter. 1 = experimental A2WC012E spark-cut path. In spark mode the custom POLF wrapper clears only the rev-limit fuel-cut bit while LC is engaged and RPM is below the normal redline; the normal hard-redline fuel cut remains intact. First flash/test should use mode 0.','Limiter Strategy')
add_abs('LC Spark Events Cut','Events','Number of ignition events suppressed at the start of each spark-cut cycle while RPM is above the existing Launch Control RPM. Recommended initial value: 3. Must be <= LC Spark Event Cycle.','Spark Events Cut')
add_abs('LC Spark Event Cycle','Events','Total 1-based event cycle length for experimental spark cut. Recommended initial value: 5 (3 cut / 5 total). A value of 0 fails safe to a one-event counter reset but should not be used.','Spark Event Cycle')

phys_fuel=None
for t in root.iter('table'):
    if t.get('name')=='LC Advanced Fuel Mode' and (t.get('storageaddress') or '').lower()=='0x6ad78':
        phys_fuel=t; break
if phys_fuel is None: raise RuntimeError('physical LC Advanced Fuel Mode @0x6AD78 not found')
phys_parent=parents[phys_fuel]
existing_phys={(t.get('name'),(t.get('storageaddress') or '').lower()) for t in phys_parent.findall('table')}
for name,addr in [('LC Cut Mode','0x6ADC4'),('LC Spark Events Cut','0x6ADC8'),('LC Spark Event Cycle','0x6ADCC')]:
    if (name,addr.lower()) not in existing_phys:
        ET.SubElement(phys_parent,'table', {'name':name,'storageaddress':addr})

try: ET.indent(tree, space='    ')
except Exception: pass
tree.write(DEF_OUT, encoding='utf-8', xml_declaration=True)
ET.parse(DEF_OUT)

sha_in=hashlib.sha256(b).hexdigest(); sha_safe=hashlib.sha256(rom).hexdigest(); sha_test=hashlib.sha256(rom_test).hexdigest()
ds,gs=diff_regions(b,rom)
report=[]
report += ['A2WC012E / A2WC0MME v68 experimental LC spark-cut patch','',f'Input: {INP.name}',f'  SHA256 {sha_in}',f'  size {len(b)}',f'  Internal ID {b[0x2000:0x2008].decode()}','']
report += [f'Stage1 output (safe first flash, LC Cut Mode=0/Fuel): {OUT_SAFE.name}',f'  SHA256 {sha_safe}',f'  changed bytes vs v67: {len(ds)}','']
report += [f'Stage2 output (experimental, LC Cut Mode=1/Spark): {OUT_TEST.name}',f'  SHA256 {sha_test}',f'  changed bytes vs v67: {len([i for i,(x,y) in enumerate(zip(b,rom_test)) if x!=y])}','']
report += ['Validated preserved areas:','  Delta MAP block 0x6AC40-0x6AD43: byte-for-byte unchanged','  Existing Advanced LC block 0x6AD50-0x6ADC3 preserved except intentional Base Timing Lock -5.0 -> -2.0 deg','  MerpMod RevLimiter code 0x25758-0x2583F: byte-for-byte unchanged','  Normal hard-redline fuel-cut logic therefore remains in place','']
report += ['Changes:','  0x6ADBC Base Timing Lock: -5.0 -> -2.0 deg','  0x6ADC4 LC Cut Mode: 0 (Stage1) / 1 (Stage2)','  0x6ADC8 LC Spark Events Cut: 3','  0x6ADCC LC Spark Event Cycle: 5',f'  0x1132C POLF wrapper pointer: 0x{OLD_POLF_WRAPPER:08X} -> 0x{NEW_POLF_WRAPPER:08X}',f'  0x{NEW_POLF_WRAPPER:06X}: enhanced POLF wrapper',f'  0x{OCR_SITE_START:06X}-0x{OCR_SITE_END-1:06X}: OCR ignition scheduler local hook stub',f'  0x{GR_SITE_START:06X}-0x{GR_SITE_END-1:06X}: GR ignition scheduler local hook stub',f'  0x{OCR_ROUTINE:06X}: custom OCR spark-cut routine',f'  0x{GR_ROUTINE:06X}: custom GR spark-cut routine','']
report += ['Spark mode behavior:','  Uses existing MerpMod LC Engaged signal @ FFFFCA3B.','  Uses existing Launch Control RPM ROM value @ 0x6A4F0 as spark-cut threshold.','  At/under threshold ignition fires normally; above threshold first 3 of each 5 events are suppressed.','  While LC spark mode is active below the normal Redline value @ 0x6A4D0, only rev-limit fuel-cut bit 0x80 is cleared.','  At/above normal redline the wrapper does NOT clear the fuel-cut bit, preserving hard-redline protection.','  Outside LC or with Cut Mode=0, fuel-cut behavior remains current MerpMod behavior.','']
report += ['Important status:','  The A2WC012E OCR/GR hook locations were reverse-engineered by exact opcode-sequence match to Merp/MerpMod SparkHacks OEM sequences.','  Upstream MerpMod does NOT ship SPARK_HACKS support for A2WC012E; this port is experimental and has not yet been vehicle-validated.','  SAFE intentionally defaults to Cut Mode=0 so the new hook pass-through can be verified before enabling actual spark suppression.','  Checksum is NOT recalculated here. Open/save with EcuFlash/subarudbw before flashing.','']
report += ['SAFE changed regions vs v67:'] + [f'  0x{s:06X}-0x{e:06X} ({e-s+1} bytes)' for s,e in gs]
REPORT.write_text('\n'.join(report)+'\n',encoding='utf-8')

print(f'input_sha256={sha_in}')
print(f'safe_sha256={sha_safe}')
print(f'enabled_sha256={sha_test}')
print(f'definition_sha256={hashlib.sha256(DEF_OUT.read_bytes()).hexdigest()}')
print(f'changed_bytes_safe={len(ds)}')

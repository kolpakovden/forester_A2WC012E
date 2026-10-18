"""Offline CarBerry Tip-in arithmetic exploration. Never flash calculated values.
Derived from Ghidra HC16 listing; not an independent bit-accurate CPU emulator.
"""
def clamp_u8(v):
    return max(0, min(255, v))

def delta_two_samples(current, history2):
    """FUN_004D5E: encoded 8-bit difference, neutral=0x80."""
    if not all(0 <= x <= 255 for x in (current,history2)):
        raise ValueError("Expected bytes")
    return clamp_u8(128 + current - history2)

def delta_update(current, history1, history2):
    """Return (delta, new history1, new history2) in producer instruction order."""
    return delta_two_samples(current, history2), current, history1

def current_from_working(ram081c, ram03c8, ramdc):
    """0x004D66..004D82: saturating word subtraction, high byte, optional override."""
    if not all(0 <= x <= 65535 for x in (ram081c,ram03c8)):
        raise ValueError("Expected unsigned words")
    if not 0 <= ramdc <= 255:
        raise ValueError("Expected flag byte")
    return 0x0d if (ramdc & 1) else (max(0,ram081c-ram03c8) >> 8)

BASE_AXIS=list(range(0x80,0xC5,4))
BASE_VALUES=[0x06,0x0e,0x16,0x1e,0x26,0x2d,0x34,0x3c,
             0x43,0x4c,0x53,0x59,0x60,0x63,0x64,0x64,0x64,0x64]

def explicit_base_q8_8(x, axis=BASE_AXIS, values=BASE_VALUES):
    """Increasing/flat reference base table. Approximation for general tables."""
    if len(axis)!=len(values):raise ValueError("Axis/value count mismatch")
    if not 0<=x<=255:raise ValueError("Expected byte")
    if x<=axis[0]:return values[0]<<8
    if x>=axis[-1]:return values[-1]<<8
    for i in range(len(axis)-1):
        if axis[i]<=x<axis[i+1]:
            frac=((x-axis[i])<<16)//(axis[i+1]-axis[i])
            return (values[i]<<8)+(((values[i+1]-values[i])*frac)>>8)
    raise AssertionError("no interval")

def compensated_pulse_raw(base_q8_8, rpm_raw, boost_raw, ect_raw):
    """FUN_00A872..00A8B4 provisional 16-bit fixed-point model."""
    f=min(65535,(rpm_raw*boost_raw*ect_raw)>>4)
    return (base_q8_8*f)>>16

def compensated_pulse_ms(base_q8_8, rpm_raw, boost_raw, ect_raw):
    return compensated_pulse_raw(base_q8_8,rpm_raw,boost_raw,ect_raw)*0.004

def uniform_index_fraction(raw, scale, start, intervals, shift):
    """Uniform comp tables; 8-bit coordinates use shift=8, words shift=0."""
    if raw<start:return 0,0
    product=(raw-start)*scale*(1<<shift)
    index=product>>16
    return (intervals,0) if index>=intervals else (index,product&65535)

def interpolate_comp_raw(values,index,fraction):
    """General negative slope still needs exact HC16 rounding validation."""
    if index>=len(values)-1:return values[-1]
    a,b=values[index:index+2]
    if b>=a:return a+(((b-a)*fraction)>>16)
    return a-(((a-b)*fraction+65535)>>16)

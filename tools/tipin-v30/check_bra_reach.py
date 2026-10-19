#!/usr/bin/env python3
"""Read-only candidate analysis. FF fill is NOT proof of free executable ROM."""
import hashlib
from pathlib import Path
import sys

PIN = "2ca539d0c47e3b1eec96c41e1e514c7b19b0e3786e9d826a41d3a3505b4c5d99"
HOOK = 0x24B16

def ff_runs(buf):
    i = 0
    while i < len(buf):
        if buf[i] != 255:
            i += 1
            continue
        j = i + 1
        while j < len(buf) and buf[j] == 255:
            j += 1
        yield i, j
        i = j

def main(path):
    buf = Path(path).read_bytes()
    assert len(buf) == 0x80000, "Expected a 512KiB ROM"
    assert hashlib.sha256(buf).hexdigest() == PIN, "Not clean v25"
    assert buf[HOOK:HOOK+4] == bytes.fromhex("FB EA F3 38"), "Hook area changed"
    # SH BRA disp12: signed 12-bit displacement * 2, relative to PC+4.
    low, high = HOOK + 4 - 4096, HOOK + 4 + 4094
    print(f"SH BRA at {HOOK:#x}: aligned target range {low:#x}..{high:#x}")
    sizes = []
    for start, end in ff_runs(buf):
        if end - start >= 64:
            print(f"Potential FF fill: {start:#x}..{end-1:#x}, {end-start} bytes")
        a, b = max(start, low), min(end, high + 1)
        a += a & 1
        if a < b:
            sizes.append(b - a)
    print("Largest contiguous aligned FF run within BRA reach:", max(sizes, default=0))
    print("Runs >=16 bytes within reach:", sum(n >= 16 for n in sizes))
    print("Read-only: this does not validate any cave, trampoline, or flash safety.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python check_bra_reach.py Forester_SG9_MAP_clean_v25.bin")
    main(sys.argv[1])

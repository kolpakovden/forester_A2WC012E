# v39 — EcuFlash SubaruDBW checksum calculation, offline disassembly

Input EcuFlash PE32 x86 SHA256: 80ab6e185ac2383651b592751e0c9db1a7cf2cbe3c039e6363d90cdf7cea74dd.

The vtable functions 0x4C2A90 and 0x4C2AA0 call 0x4C2910 with mode arguments 0 and 1 respectively. 0x4C2910 checks six-byte CPU model markers at offset +0x3C of a ROM-like object, including SH7055, SH7058, SH7059, SH72531. It calls 0x4C26C0 for the checksum operation. The three model strings are present in the EXE's static data and the SH72531 string is constructed separately. Two block-list addresses passed are 0x13F500 (0x11 records) and 0x13F5E8 (0x02 records): those are application logical addresses and NOT yet mapped to raw 512KiB BIN offsets.

0x4C26C0 allocates record_count*12 bytes, populates it through 0x456EA0, and reads three 32-bit big-endian fields per record using 0x4015D0. It rejects misaligned start addresses, invalid range order and invalid end alignment. It checks a checksum word against the summed data range.

0x457460 calls 0x4017C0 to sum consecutive **big-endian 32-bit words modulo 2^32**. Exact code at 0x4017F4..0x401845, performing add eax,ecx per four bytes.

At 0x4C2818 EcuFlash compares calculated result plus stored compensation word with 0x5AA5A55A. In correction mode it writes (0x5AA5A55A - calculated_sum) via 0x4016A0 to the third word of a 12-byte record in big-endian form. 0x4C2870 prints a warning when checked data length is zero and checksum features seem off.

This confirms the arithmetic and the core validation/fixup loop. It **does not** yet prove which exact bytes in A2WC0MME belong to checksum range lists, or whether an image has a valid checksum.

Next: trace 0x456EA0 ROM address mapping, parse the record-list image for this SH7055 ECU, independently validate original v25 and one-byte probe, and verify ROM hole execution sectors. A2WC0MME.xml ECUID is still unverified. No ECU flashing.

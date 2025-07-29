#!/usr/bin/env python3
import os
import subprocess

data = input('ELF: ')
data = bytes.fromhex(data)[:80]
assert data.startswith(b'\x7fELF'), 'Not an ELF'
assert data[0x12:0x14] == b'\x3e\x00', 'Not an x86-64 executable'

with open('/work/cwd/elf', 'wb') as f:
    f.write(data)
    os.fchmod(f.fileno(), 0o755)

os.chroot('/work')
os.chdir('/cwd')

r = subprocess.run(['./elf'], env={}, stdin=subprocess.DEVNULL, capture_output=True)
assert not r.returncode, 'Sorry, the process died'

print('Congratulations, here is your output:', r.stdout.decode())

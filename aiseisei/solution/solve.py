from pwn import *
import re
import base64
import random
import hashlib

context.log_level = "debug"

io = remote("127.0.0.1", 9999)

def proof_of_work():
  line = io.recvuntil(b":")
  match = re.search(r"\(nonce (.+)\)", line.decode())
  assert match
  nonce = match.group(1)
  nonce = base64.b64decode(nonce)
  while True:
    proof = random.randbytes(16)
    hash = hashlib.sha256(nonce + proof).hexdigest()
    if hash.startswith("111111"):
      io.sendline(base64.b64encode(proof))
      break
  io.recvuntil("hash=")
  io.recvline()

proof_of_work()
with open("input.tiff", "rb") as f:
  data = f.read()
io.sendlineafter(b"Input Image", base64.b64encode(data))
io.interactive()

from Crypto.Util.number import *
import string
from random import choice
import sys
import os

flag = os.getenv("FLAG")

p, q, r, x, y = [getPrime(256) for _ in range(3)] + [getPrime(256) << 128 for _ in range(2)]
secret = "".join([choice(string.ascii_letters) for _ in range(77)])
PR.<i, j, k> = QuaternionAlgebra(Zmod(p*q), -x, -y)
print("🎁 :", [p*q] + list(PR([x+y, p+x, q+y, r])^bytes_to_long(777*secret.encode())))

for attempt in range(3):
    user_input = input("").strip()
    if user_input == secret:
        print("✅ Correct")
        print("🚩 :", flag)
        break
    else:
        print("❌ Wrong")
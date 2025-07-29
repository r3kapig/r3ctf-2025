from Crypto.Util.number import *
from secret import flag
import string

p, q, r, x, y = [getPrime(256) for _ in range(3)] + [getPrime(256) << 128 for _ in range(2)]
secret = "".join([choice(string.ascii_letters) for _ in range(77)])
PR.<i, j, k> = QuaternionAlgebra(Zmod(p*q), -x, -y)
print("🎁 :", [p*q] + list(PR([x+y, p+x, q+y, r])^bytes_to_long(777*secret.encode())))
if(input() == secret):
    print("🚩 :", flag)
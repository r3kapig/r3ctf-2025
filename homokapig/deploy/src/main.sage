import random
import re
load("bfv.sage")

flag = os.getenv("FLAG")

BANNER = br"""
                                                      01
                                                      0001           0
                                                      0000       11000
                                                      0001 1  11  0000
                                                      0000 10000   000
                                                      00001100001  000
                                                      0000000000000000
                                                      0111100000000000
                                                            0000   100
               1101                                         0000     1
            1000000001       01                             0000
           00000000000000000000                             0000
          000000000000000000000100000111                    1111
         1000000000000000000000000000000000001              1  1
          1000000000000000000011        111000001           0111
             000000000000000                  10001         1010
            100000000000001                      1001       1  1
            100000001111                           001      1110     1
             100000   11                       100  101     11 1   111
               000  10001     1001111110001    1001  10     000001  0
              1000   101    001           100         0011110000  1011
           1  1001         01   11     1    00      010111  0000   10
        0     1001        10    00    000   10     11 0 1 0 0000 101
       0 01  1100011       00               00      0 01    0000
         0  010 000  1111   101           101        0  11110000
         11 1    000       001 10000100001          0       0000
           1001 0 1000 001                        01        0000
               10 00000001                     100          0000
                      1000011              10001            0000
                          100000000000000001                0000
                                                            0000
"""

def recv_poly():
    pattern = r"^(.*?) over Z\[X\]/\(X\^(\d+)\+1\) modulo (\d+)$"

    poly = input("")
    match = re.match(pattern, poly)
    if match:
        poly_str, N_str, q_str = match.groups()
        N = int(N_str)
        q = int(q_str)
        return polynomial(q, N, poly_str)
    else:
        raise TypeError("Input is not a valid polynomial")

def send_ct(ct):
    print(ct)

def recv_ct():
    a = recv_poly()
    b = recv_poly()

    return Ciphertext(a, b)

def send_key(key):
    for i in range(len(key)):
        send_ct(key[i])

def main():
    print(BANNER)
    print("Welcome to R3CTF 2025!")
    print("Here is a tiny implementation of BFV scheme.")
    print("You can test by running module_test.sage.")
    print("Now let's start the challenge.")

    N = 1024
    p = 61441
    q = 4123629569
    B = 2
    debug = False

    bfv = tinyBFV(N, p, q, B, debug)

    plain = [random.randint(0, p-1) for _ in range(N)]
    pt = bfv.simd_encode(plain)
    ct = bfv.encrypt(pt)

    send_ct(ct)

    for _ in range(2):
        c = int(input("Please choose operations you want to perform: "))
        assert 0 < c <= 3
        if c == 1:
            print("Please give me ct: ")
            ct = recv_ct()
            msg = bfv.simd_decode(bfv.decrypt(ct))
            print("Give you my decryption: ")
            print(msg)
        if c == 2:
            print("Gen key switching key")
            new_sk = sample_ternery_poly(bfv.Q)
            ksk = bfv.gen_ksk(new_sk)
            send_key(ksk)
        if c == 3:
            print("Gen rotation key")
            step = int(input("Please choose rotation step:"))
            t = (step * 5) % N
            galois_key = bfv.gen_galois_key(t)
            send_key(galois_key)

    print("Give me my secret key: ")
    secret_key = recv_poly()

    if secret_key == bfv.sk:
        print(flag)
        

if __name__ == "__main__":
    main()

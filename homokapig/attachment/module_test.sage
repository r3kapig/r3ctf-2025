import random

load("bfv.sage")
load("gadget.sage")
load("poly.sage")
load("distribution.sage")

def gadget_test():
    N = 4
    q = 23
    B = 3

    poly = "19 + 13*X + 14*X^2 + 17*X^3"
    poly = polynomial(q, N, poly)

    gadget_poly = gadget_decomposition(poly, B)
    assert poly == gadget_recomposition(gadget_poly, B)

def poly_test():
    N = 4
    q = 23

    p1 = "1 + 2*X + 3*X^2 + 4*X^3"
    p1 = polynomial(q, N, p1)

    p2 = "4 + 3*X + 2*X^2 + 1*X^3"
    p2 = polynomial(q, N, p2)

    assert str(p1) == "4*X^3 + 3*X^2 + 2*X + 1 over Z[X]/(X^4+1) modulo 23"
    assert str(p2) == "X^3 + 2*X^2 + 3*X + 4 over Z[X]/(X^4+1) modulo 23"
    assert str(p1 + 10) == "4*X^3 + 3*X^2 + 2*X + 11 over Z[X]/(X^4+1) modulo 23"
    assert str(p1 + p2) == "5*X^3 + 5*X^2 + 5*X + 5 over Z[X]/(X^4+1) modulo 23"
    assert str(p1 - 10) == "4*X^3 + 3*X^2 + 2*X + 14 over Z[X]/(X^4+1) modulo 23"
    assert str(p1 - p2) == "3*X^3 + X^2 + 22*X + 20 over Z[X]/(X^4+1) modulo 23"
    assert str(p1 * 7) == "5*X^3 + 21*X^2 + 14*X + 7 over Z[X]/(X^4+1) modulo 23"
    assert str(p1 * p2) == "7*X^3 + 16*X^2 + 7 over Z[X]/(X^4+1) modulo 23"
    assert str(p1.mapping(3)) == "2*X^3 + 20*X^2 + 4*X + 1 over Z[X]/(X^4+1) modulo 23"

def bfv_test():
    N = 32
    p = 193
    q = 64513
    B = 2

    debug = True

    bfv = tinyBFV(N, p, q, B, debug)

    plain1 = [random.randint(0, p-1) for _ in range(N)]
    plain2 = [random.randint(0, p-1) for _ in range(N)]

    print("Plaintext:")
    print(f"pt1(origin): {plain1}")
    print(f"pt2(origin): {plain2}")

    # Test Encoding / Decoding

    pt1 = bfv.simd_encode(plain1)
    pt2 = bfv.simd_encode(plain2)

    print("Test Encoding and Decoding:")
    print(f"pt1(decoded): {bfv.simd_decode(pt1)}")
    print(f"pt2(decoded): {bfv.simd_decode(pt2)}")
    assert bfv.simd_decode(pt1) == plain1 and bfv.simd_decode(pt2) == plain2

    # Test Encrypt / Decrypt

    ct1 = bfv.encrypt(pt1)
    ct2 = bfv.encrypt(pt2)

    print("Test Encrypt and Decrypt:")
    print(f"pt1(decrypted and decoded): {bfv.simd_decode(bfv.decrypt(ct1))}")
    print(f"pt2(decrypted and decoded): {bfv.simd_decode(bfv.decrypt(ct2))}")
    assert bfv.simd_decode(bfv.decrypt(ct1)) == plain1 and bfv.simd_decode(bfv.decrypt(ct2)) == plain2

    # Test Operations
    print("Test Operations:")
    
    ct_add = bfv.add(ct1, ct2)

    print("Test Addition:")
    print(f"pt(added): {[(plain1[i]+plain2[i]) % p for i in range(N)]}")
    print(f"pt(encrypted and added): {bfv.simd_decode(bfv.decrypt(ct_add))}")
    assert bfv.simd_decode(bfv.decrypt(ct_add)) == [(plain1[i]+plain2[i]) % p for i in range(N)]

    new_sk = sample_ternery_poly(bfv.Q)
    ksk = bfv.gen_ksk(new_sk)
    ct1_switched = bfv.key_switch(ct1, ksk)
    ct2_switched = bfv.key_switch(ct2, ksk)

    print("Test Key Switching:")
    test = bfv.decrypt(ct1_switched, new_sk)
    print(f"pt1(key switched and decrypted): {bfv.simd_decode(bfv.decrypt(ct1_switched, new_sk))}")
    print(f"pt2(key switched and decrypted): {bfv.simd_decode(bfv.decrypt(ct2_switched, new_sk))}")
    assert bfv.simd_decode(bfv.decrypt(ct1_switched, new_sk)) == plain1 and bfv.simd_decode(bfv.decrypt(ct2_switched, new_sk)) == plain2

    rotate_step = 1
    t = rotate_step * 5
    pt1_galois = pt1.mapping(t)
    galois_key = bfv.gen_galois_key(t)
    ct1_galois = bfv.apply_galois(ct1, t, galois_key)

    print("Test Galois:")
    print(f"pt1(mapping and decode): {bfv.simd_decode(pt1_galois)}")
    print(f"pt1(encrypted and mapping): {bfv.simd_decode(bfv.decrypt(ct1_galois))}")
    assert bfv.simd_decode(bfv.decrypt(ct1_galois)) == plain1[1:N//2] + [plain1[0]] + plain1[N//2+1:] + [plain1[N//2]]

if __name__ == "__main__":
    gadget_test()
    poly_test()
    bfv_test()
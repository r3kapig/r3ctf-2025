load("distribution.sage")
load("ciphertext.sage")
load("gadget.sage")

class tinyBFV:
    def __init__(self, N, p, q, B, debug):
        self.N = N
        self.p = p
        self.q = q
        self.B = B
        self.debug = debug
        self.t = ceil(log(self.q, self.B))
        self.gadget = build_gadget(self.q, self.B)
        self.delta = self.q//self.p

        assert self.p % (2 * self.N) == 1 and is_prime(self.p)

        P.<X> = PolynomialRing(Zmod(self.q))
        self.roots = [i[0] for i in (X^self.N+1).change_ring(Zmod(self.p)).roots()]
        self.shift_roots = [pow(self.roots[0], pow(5, i, self.p-1), self.p) for i in range(N//2)] + [pow(self.roots[0], -pow(5, i, self.p-1), self.p) for i in range(N//2)]
        
        assert set(self.shift_roots) == set(self.roots)
        
        Q.<X> = P.quotient(X^N+1)
        self.P = P
        self.Q = Q
        R.<X> = PolynomialRing(Zmod(self.p))
        self.plaintext_ring = R
        self.gen_sk()
        self.gen_relin_key()

    def gen_sk(self):
        self.sk = sample_ternery_poly(self.Q)

    def gen_ksk(self, new_sk):
        ksk = []

        for i in range(self.t):
            if self.debug:
                e = polynomial(self.q, self.N, "0")
            else:
                e = sample_gaussian_poly(self.Q)
            a = sample_uniform_poly(self.Q)
            b = self.sk * self.gadget[i] - (a * new_sk + e)
            ksk.append(Ciphertext(a, b))

        return ksk

    def gen_galois_key(self, t):
        mapping_sk = self.sk.mapping(t)
        new_sk = self.sk
        self.sk = mapping_sk
        galois_key = self.gen_ksk(new_sk)
        self.sk = new_sk

        return galois_key

    def simd_encode(self, vec):
        assert len(vec) == self.N
        encoded_poly = self.plaintext_ring.lagrange_polynomial([(self.shift_roots[i], vec[i]) for i in range(self.N)])
        return polynomial(self.q, self.N, self.Q(encoded_poly.change_ring(ZZ) * self.delta))

    def simd_decode(self, encoded_poly):
        encoded_poly = self.plaintext_ring([round(ZZ(c) / self.delta) for c in encoded_poly.poly.list()])
        return [encoded_poly(i) for i in self.shift_roots]

    def encrypt(self, pt):
        if self.debug:
            e = polynomial(self.q, self.N, "0")
        else:
            e = sample_gaussian_poly(self.Q)
        ct0 = sample_uniform_poly(self.Q)
        ct1 = pt + e - ct0 * self.sk
        return Ciphertext(ct0, ct1)

    def decrypt(self, ct, sk = None):
        ct0, ct1 = ct.a, ct.b
        if sk:
            return ct1 + ct0 * sk
        else:
            return ct1 + ct0 * self.sk

    def add(self, ct1, ct2):
        return ct1 + ct2

    def sub(self, ct1, ct2):
        return ct1 - ct2

    def key_switch(self, ct, ksk):
        a, b = ct.a, ct.b
        decomp_a = gadget_decomposition(a, self.B)

        a1 = polynomial(self.q, self.N, "0")
        b1 = b

        assert len(ksk) == self.t

        for i in range(self.t):
            a1 += ksk[i].a * decomp_a[i]
            b1 += ksk[i].b * decomp_a[i]

        return Ciphertext(a1, b1)

    def apply_galois(self, ct, t, galois_key):
        mapping_ct = Ciphertext(ct.a.mapping(t), ct.b.mapping(t))
        return self.key_switch(mapping_ct, galois_key)

    def multiply(self, ct1, ct2):
        pass

    def gen_relin_key(self):
        pass

    def relin(self, expand_ct, relin_key):
        pass



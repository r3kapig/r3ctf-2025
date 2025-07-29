from sage.stats.distributions.discrete_gaussian_integer import DiscreteGaussianDistributionIntegerSampler
from secrets import randbelow
import random
sigma = 3.2
D = DiscreteGaussianDistributionIntegerSampler(sigma=sigma)

load("poly.sage")

def sample_gaussian_poly(Q):
    q = Q.base_ring().cardinality()
    N = Q.degree()
    return polynomial(q, N, Q([D() for _ in range(N)]))

def sample_uniform_poly(Q):
    q = Q.base_ring().cardinality()
    N = Q.degree()
    return polynomial(q, N, Q([randbelow(int(q)) for _ in range(N)]))

def sample_ternery_poly(Q):
    q = Q.base_ring().cardinality()
    N = Q.degree()
    return polynomial(q, N, Q([random.randint(-1, 1) for _ in range(N)]))

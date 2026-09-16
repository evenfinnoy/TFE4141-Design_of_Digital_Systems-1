"""
Montgomery modular multiplication for RSA modular exponentiation.

Split into two stages, matching the derivation in the note:

    1. montgomery_setup(n, k)   -> computes the constants r, n', R mod n, R^2 mod n
    2. redc / mont_mult / mod_exp_montgomery -> reuse those constants

Core identity being implemented (REDC):

    q = (x mod r) * n' mod r
    a = (x - q*n) / r
    if a >= n: a -= n
"""


def egcd(a, b):
    """Extended Euclidean algorithm, returns (g, x, y) so that a*x + b*y = g"""
    if a == 0:
        return b, 0, 1
    g, x1, y1 = egcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return g, x, y


def modinv(a, m):
    """Modular inverse of a mod m, using the extended Euclidean algorithm"""
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError("no inverse exists, a and m are not coprime")
    return x % m


def montgomery_setup(n, k=None):
    """
    Stage 1: calculate the constants Montgomery reduction needs.

    n : the modulus (must be odd, since r is a power of two and must be
        coprime to n for n' = n^-1 mod r to exist)
    k : number of bits for r = 2**k. Defaults to n.bit_length(), which
        gives the smallest power of two strictly bigger than n.

    Returns a dict with:
        n         the modulus itself
        r         2**k
        k         bit width used
        n_prime   n' = n^-1 mod r
        r_mod_n   R mod n
    """
    if n % 2 == 0:
        raise ValueError("Montgomery reduction needs an odd modulus")

    if k is None:
        k = n.bit_length()

    r = 1 << k
    if r <= n:
        raise ValueError("r = 2^k must be larger than n")

    n_prime = modinv(n, r)

    return {
        "n": n,
        "r": r,
        "k": k,
        "n_prime": n_prime,
        "r_mod_n": r % n,
    }


def redc(x, params):
    """Montgomery reduction, computes x * r^-1 mod n without dividing by n"""
    n = params["n"]
    r = params["r"]
    n_prime = params["n_prime"]

    q = (x % r) * n_prime % r
    a = (x - q * n) // r
    a = a % n

    return a

def to_montgomery(a, params):
    """Converts an ordinary number into Montgomery form"""
    return (a * params["r_mod_n"]) 

def from_montgomery(a_bar, params):
    """Converts a Montgomery form number back into an ordinary number"""
    return redc(a_bar, params)


def mont_mult(a_bar, b_bar, params):
    """Multiplies two Montgomery form numbers, result stays in Montgomery form"""
    return redc(a_bar * b_bar, params)


def mod_exp_montgomery(base, exp, n, k=None):
    """
    Stage 2: modular exponentiation, base**exp mod n, using Montgomery
    multiplication for every squaring and multiplying step (square and
    multiply, same structure as the repeated squaring slides).
    """
    params = montgomery_setup(n, k)

    base_bar = to_montgomery(base, params)
    result_bar = to_montgomery(1, params) 

    e = exp
    while e > 0:
        if e & 1:
            result_bar = mont_mult(result_bar, base_bar, params)
        base_bar = mont_mult(base_bar, base_bar, params)
        e >>= 1

    return from_montgomery(result_bar, params)


if __name__ == "__main__":
    # Small numerical check, same numbers as the worked example in the note
    n = 13
    r_bits = 4  # r = 2**4 = 16
    params = montgomery_setup(n, r_bits)
    print("n_prime:", params["n_prime"], "expected 5")

    x = 37
    print("REDC(37):", redc(x, params))

    # A tiny RSA style check: 7^560 mod 561 style sanity test, small numbers
    # p = 5, q = 11 -> n = 55, pick e = 3, d = 27
    n = 55
    e = 3
    d = 27
    m = 42

    c = mod_exp_montgomery(m, e, n)
    m_back = mod_exp_montgomery(c, d, n)
    print("message:", m, "cipher:", c, "decrypted:", m_back)
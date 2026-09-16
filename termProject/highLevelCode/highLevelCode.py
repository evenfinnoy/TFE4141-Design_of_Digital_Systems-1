"""
|------     ---|---    -------|        
|      |       |       |       
|------        |       |   ---|
|      |       |       |      |
|------     ---|---    |------|  comment

High level implementation of algorithm for M^e mod n, using Montgomery multiplication

Link to algorithm explanations:

Montgromery multiplication:
https://cp-algorithms.com/algebra/montgomery_multiplication.html

Extended Euclidean algorithm:
https://cp-algorithms.com/algebra/extended-euclid-algorithm.html

Specifications:
M < n
r > n

r = 2^x
n = 2m - 1
=> gcd(n,r) = 1

"""

def extended_euclidean_algorithm(a_coeff, b_coeff):
    # Finding coefficients in Bézouts identity: a_coeff*x + b_coeff*y = gcd(a, b)
    # In our case: r * r^-1 + n * n' = 1, since gcd(r, n) = 1
    
    # Reached the base case
    if a_coeff == 0:
        return b_coeff, 0, 1

    # Recursive call until base case reached
    gcd, x_remainder, x_previous = extended_euclidean_algorithm(b_coeff % a_coeff, a_coeff)

    # Update coefficiants
    x = x_previous - (b_coeff // a_coeff) * x_remainder
    y = x_remainder

    return gcd, x, y


def modular_inverse(n, r):
    gcd, n_inverse, _ = extended_euclidean_algorithm(n, r)

    # gcd(n,r) has to be 1 due to Montgomery specifications
    if gcd != 1:
        raise ValueError("no inverse exists, n and r are not coprime")

    # Make sure 0 <= n_inverse < r
    return n_inverse % r


def montgomery_setup(n, k=None):
    # confirm n is odd number
    if n % 2 == 0:
        raise ValueError("Montgomery reduction needs an odd modulus")

    # make r bigger than n if number of bits not specified
    if k is None:
        k = n.bit_length()

    r = 1 << k # 2^k

    if r <= n:
        raise ValueError("r must be larger than n")

    n_prime = modular_inverse(n, r)

    return {
        "n": n,
        "r": r,
        "n_prime": n_prime,
    }


def redc(x, params):
    # Montgomery reduction, computes (x * r^-1) mod n without dividing by n

    n = params["n"]
    r = params["r"]
    n_prime = params["n_prime"]

    # find q so numerator divisable by r
    q = (x % r) * n_prime % r

    a = (x - q * n) // r

    # Make sure 0 <= a < n
    a = a % n
    return a

def to_montgomery(x, params):
    return ((x * params["r"]) % params["n"]) 

def from_montgomery(x_bar, params):
    return redc(x_bar, params)

def montgomery_multiplication(x_bar, y_bar, params):
    return redc(x_bar * y_bar, params)


def rsa_core(base, exponent, n, k=None):

    if base >= n:
        raise ValueError("n must be larger than m")

    params = montgomery_setup(n, k)

    base_bar = to_montgomery(base, params)
    result_bar = to_montgomery(1, params) # cconvert 1 into Montgomery space

    while exponent > 0:
        if exponent & 1:
            result_bar = montgomery_multiplication(result_bar, base_bar, params)
        base_bar = montgomery_multiplication(base_bar, base_bar, params)
        exponent >>= 1

    return from_montgomery(result_bar, params)

if __name__ == "__main__":

    # a simple test
    n = 55
    encrypt_key = 3
    decrypt_key = 27
    message = 35

    c = rsa_core(message, encrypt_key, n)
    m_back = rsa_core(c, decrypt_key, n)
    print("message:", message, "cipher:", c, "decrypted:", m_back)
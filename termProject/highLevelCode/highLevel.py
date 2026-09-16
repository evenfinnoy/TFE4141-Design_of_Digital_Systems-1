# From slide 11 (19) 
def mod_exp(M, e, N, k):
    C = 1
    P = M # can add % N here, for safety, but we dont see why that is better than just giving an error if M is too big
    for i in range(k):
        bit = (e >> i) & 1              # the i'th bit of e, counting from the bottom
        if bit == 1:
            C = mod_mult(C, P, N, k)
        P = mod_mult(P, P, N, k)
    return C

# From slide 12 (22)
def mod_mult(A, B, N, k):
    # Computes A*B mod N, processing B one bit at a time, MSB first
    R = 0
    for i in range(k):
        bit = (B >> (k - 1 - i)) & 1   # the i'th bit of B, counting from the top
        R = 2 * R + A * bit
        if R >= N:
            R -= N
        if R >= N:
            R -= N
    return R

#def mod_montgomery():



N = 3233          # example small modulus, from a toy RSA setup
e = 17
M = 65
k = N.bit_length()

result = mod_exp(M, e, N, k)
expected = pow(M, e, N)

print(result, expected, result == expected)


###------------------------------------KRITAGYA CODE------------------------------------
#We should figure out how the code is good for hardware, and what tools/tricks to utilize?
#^ Best to do that after or before implementing the high level code?

def montgomery_pow(M, e, n):
    """
    Compute M^e mod n using Montgomery multiplication.

    Requirements:
        n must be odd
        e >= 0
    """

    # -------------------------------------------------
    # 1. Choose r = 2^k such that r > n
    # -------------------------------------------------
    k = n.bit_length()
    r = 1 << k

    # n must be odd so gcd(n, r) = 1
    if n % 2 == 0:
        raise ValueError("n must be odd for this implementation")

    # -------------------------------------------------
    # 2. Find n'
    #
    # We want:
    #
    #     r*r_inv + n*n' = 1
    #
    # Therefore:
    #
    #     n*n' = 1 (mod r)
    #
    # so:
    #
    #     n' = n^(-1) mod r
    # -------------------------------------------------
    n_prime = pow(n, -1, r)

    # -------------------------------------------------
    # 3. Montgomery REDC
    #
    # Computes:
    #
    #     x * r^(-1) mod n
    # -------------------------------------------------
    def REDC(x):
        q = ((x % r) * n_prime) % r

        a = (x - q * n) // r

        if a < 0:
            a += n

        return a

    # -------------------------------------------------
    # 4. Montgomery multiplication
    #
    # If a and b are in Montgomery space:
    #
    #     a = A*r
    #     b = B*r
    #
    # then:
    #
    #     REDC(a*b)
    #
    # gives:
    #
    #     A*B*r
    #
    # which is still in Montgomery space.
    # -------------------------------------------------
    def mont_mul(a, b):
        return REDC(a * b)

    # Make sure M is in [0, n-1]
    M %= n

    # -------------------------------------------------
    # 5. Enter Montgomery space
    # -------------------------------------------------

    # M_bar = M*r mod n
    M_bar = (M * r) % n

    # VERY IMPORTANT:
    #
    # The accumulator normally starts at 1.
    # But in Montgomery space, 1 is represented by:
    #
    #     1*r mod n
    #
    result_bar = r % n

    # -------------------------------------------------
    # 6. Square-and-multiply
    # -------------------------------------------------
    while e > 0:

        # If current exponent bit is 1:
        if e & 1:
            result_bar = mont_mul(result_bar, M_bar)

        # Square the base
        M_bar = mont_mul(M_bar, M_bar)

        # Move to next exponent bit
        e >>= 1

    # -------------------------------------------------
    # 7. Leave Montgomery space
    #
    # result_bar = result*r mod n
    #
    # REDC removes the r:
    #
    # REDC(result*r) = result
    # -------------------------------------------------
    result = REDC(result_bar)

    return result


# Example
M = 7
e = 11
n = 13

answer = montgomery_pow(M, e, n)

print("Montgomery:", answer)
print("Python check:", pow(M, e, n))
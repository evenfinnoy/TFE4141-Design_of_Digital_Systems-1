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
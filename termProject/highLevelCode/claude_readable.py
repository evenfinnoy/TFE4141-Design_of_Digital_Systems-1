"""
Montgomery modular multiplication for RSA modular exponentiation.

Split into two stages, matching the derivation in the note:

    1. compute_montgomery_constants(modulus, bit_width)
       computes the constants r, n', R mod n, R^2 mod n

    2. montgomery_reduce / montgomery_multiply / modular_exponentiation_montgomery
       reuse those constants for every squaring and multiplying step

Core identity being implemented (Montgomery reduction, often called REDC):

    quotient = (value mod r) * n_inverse mod r
    reduced  = (value - quotient * modulus) / r
    if reduced >= modulus: reduced -= modulus
"""


def extended_euclidean_algorithm(first_number, second_number):
    """
    Finds integers bezout_x and bezout_y so that
        first_number * bezout_x + second_number * bezout_y = greatest_common_divisor
    This is the standard tool used to compute a modular inverse.
    """
    if first_number == 0:
        # Base case, gcd(0, b) = b, and the coefficients are 0 and 1
        return second_number, 0, 1

    # Recurse on (second_number mod first_number, first_number), this shrinks
    # the numbers the same way long division does
    greatest_common_divisor, bezout_x_of_remainder, bezout_y_of_remainder = (
        extended_euclidean_algorithm(second_number % first_number, first_number)
    )

    # Undo one recursion step to build up the coefficients for the original inputs
    bezout_x = bezout_y_of_remainder - (second_number // first_number) * bezout_x_of_remainder
    bezout_y = bezout_x_of_remainder

    return greatest_common_divisor, bezout_x, bezout_y


def modular_inverse(number, modulus):
    """Returns number^-1 mod modulus, so that (number * result) mod modulus == 1"""
    greatest_common_divisor, bezout_x, _ = extended_euclidean_algorithm(number % modulus, modulus)

    if greatest_common_divisor != 1:
        # An inverse only exists if number and modulus share no common factors
        raise ValueError("no inverse exists, the two numbers are not coprime")

    # bezout_x might be negative, so wrap it back into the range 0..modulus-1
    return bezout_x % modulus


def compute_montgomery_constants(modulus, bit_width=None):
    """
    Stage 1: calculate every constant Montgomery reduction will reuse.

    modulus   : the RSA modulus n (must be odd, since r is a power of two
                and needs to be coprime to n for the inverse below to exist)
    bit_width : number of bits used for r = 2**bit_width. Defaults to
                modulus.bit_length(), the smallest power of two bigger than n.

    Returns a dict with:
        modulus              the modulus itself, n
        montgomery_radix     r = 2**bit_width, this is Montgomery's "R"
        bit_width            bit width used for r
        modulus_inverse      n' = n^-1 mod r
        radix_mod_modulus    R mod n
        radix_squared_mod_modulus   R^2 mod n, used to enter Montgomery form
    """
    if modulus % 2 == 0:
        # r is always a power of two, so it can only be coprime to an odd modulus
        raise ValueError("Montgomery reduction needs an odd modulus")

    if bit_width is None:
        # Pick the smallest power of two radix that is still bigger than n
        bit_width = modulus.bit_length()

    montgomery_radix = 1 << bit_width  # r = 2**bit_width, done as a bit shift

    # n' = n^-1 mod r, this is the constant that lets us pick q without ever dividing by n
    modulus_inverse = modular_inverse(modulus, montgomery_radix)

    return {
        "modulus": modulus,
        "montgomery_radix": montgomery_radix,
        "bit_width": bit_width,
        "modulus_inverse": modulus_inverse,
        "radix_mod_modulus": montgomery_radix % modulus,
        "radix_squared_mod_modulus": (montgomery_radix * montgomery_radix) % modulus,
    }


def montgomery_reduce(value, montgomery_constants):
    """
    Montgomery reduction, computes value * r^-1 mod n without ever
    dividing by n, only by r (which is a power of two, so it is a shift).
    """
    modulus = montgomery_constants["modulus"]
    montgomery_radix = montgomery_constants["montgomery_radix"]
    modulus_inverse = montgomery_constants["modulus_inverse"]

    # Choose quotient so that (value - quotient * modulus) is divisible by r
    quotient = (value % montgomery_radix) * modulus_inverse % montgomery_radix

    # This division is exact by construction of quotient, and is cheap
    # in hardware because montgomery_radix is a power of two
    reduced_value = (value - quotient * modulus) // montgomery_radix

    # The result can land at most one modulus too high or too low, so a
    # single correction in each direction is always enough to fix it
    if reduced_value >= modulus:
        reduced_value -= modulus
    if reduced_value < 0:
        reduced_value += modulus

    return reduced_value


def convert_to_montgomery_form(number, montgomery_constants):
    """Converts an ordinary number into Montgomery form, number * R mod n"""
    # Multiplying by R^2 first and then reducing once is the standard trick
    # to enter Montgomery form using the same reduce function as everything else
    return montgomery_reduce(number * montgomery_constants["radix_squared_mod_modulus"], montgomery_constants)


def convert_from_montgomery_form(number_in_montgomery_form, montgomery_constants):
    """Converts a Montgomery form number back into an ordinary number"""
    # Reducing once removes exactly one factor of R, taking us back to normal form
    return montgomery_reduce(number_in_montgomery_form, montgomery_constants)


def montgomery_multiply(first_factor, second_factor, montgomery_constants):
    """
    Multiplies two Montgomery form numbers together.
    The result is also in Montgomery form, so it can be fed straight
    back into another montgomery_multiply call.
    """
    return montgomery_reduce(first_factor * second_factor, montgomery_constants)


def modular_exponentiation_montgomery(base, exponent, modulus, bit_width=None):
    """
    Stage 2: computes base**exponent mod modulus, using Montgomery
    multiplication for every squaring and multiplying step.
    This follows the same square and multiply structure as the
    repeated squaring slides, just with Montgomery multiplication
    swapped in wherever a modular multiplication is needed.
    """
    montgomery_constants = compute_montgomery_constants(modulus, bit_width)

    # Move the base and the starting value 1 into Montgomery form once, up front
    base_in_montgomery_form = convert_to_montgomery_form(base % modulus, montgomery_constants)
    result_in_montgomery_form = convert_to_montgomery_form(1, montgomery_constants)

    remaining_exponent = exponent
    while remaining_exponent > 0:
        if remaining_exponent & 1:
            # Current lowest exponent bit is 1, so fold the current base into the result
            result_in_montgomery_form = montgomery_multiply(
                result_in_montgomery_form, base_in_montgomery_form, montgomery_constants
            )

        # Square the base for the next bit position, same as the P = P*P step in the slides
        base_in_montgomery_form = montgomery_multiply(
            base_in_montgomery_form, base_in_montgomery_form, montgomery_constants
        )

        # Move to the next exponent bit, same as shifting e right by one
        remaining_exponent >>= 1

    # Convert the final result back out of Montgomery form before returning it
    return convert_from_montgomery_form(result_in_montgomery_form, montgomery_constants)


def test_montgomery_reduce_matches_note_example():
    """Checks montgomery_reduce against the exact worked example in the note, n = 5, r = 8, x = 37"""
    modulus = 5
    bit_width = 3  # r = 2**3 = 8

    montgomery_constants = compute_montgomery_constants(modulus, bit_width)
    print("modulus_inverse:", montgomery_constants["modulus_inverse"], "expected 5")

    value_to_reduce = 37
    quotient = (
        (value_to_reduce % montgomery_constants["montgomery_radix"])
        * montgomery_constants["modulus_inverse"]
        % montgomery_constants["montgomery_radix"]
    )
    print("quotient:", quotient, "expected 1")
    print("montgomery_reduce(37):", montgomery_reduce(value_to_reduce, montgomery_constants), "expected 4")


def test_rsa_encrypt_and_decrypt_round_trip():
    """Checks a full encrypt then decrypt round trip using tiny RSA numbers, p = 5, q = 11, n = 55"""
    modulus = 55
    public_exponent = 3
    private_exponent = 27
    message = 42

    ciphertext = modular_exponentiation_montgomery(message, public_exponent, modulus)
    decrypted_message = modular_exponentiation_montgomery(ciphertext, private_exponent, modulus)

    print("message:", message, "cipher:", ciphertext, "decrypted:", decrypted_message)


if __name__ == "__main__":
    test_montgomery_reduce_matches_note_example()
    test_rsa_encrypt_and_decrypt_round_trip()
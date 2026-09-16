## Modulo Multiplication & Addition

$$
\boxed{(AB)\bmod n = \big((A\bmod n)(B\bmod n)\big)\bmod n}
$$

For **addition**, the corresponding rule is:

$$
\boxed{(A+B)\bmod n = \big((A\bmod n)+(B\bmod n)\big)\bmod n}
$$

## Why the the q-formula works

This is the clever step in Montgomery reduction. The purpose of \(q\) is very specific:

$$
\boxed{\text{Choose }q\text{ so that }x-qn\text{ is divisible by }r.}
$$

Let's derive exactly why

$$
q=(x\bmod r)n' \bmod r.
$$

### 1. What do we want?

The next line of the algorithm is

$$
a=\frac{x-qn}{r}.
$$

We want that division by \(r\) to be **exact**. So we need

$$
x-qn\equiv0\pmod r.
$$

Therefore:

$$
x\equiv qn\pmod r.
$$

### 2. Solve for \(q\)

Because \(n\) and \(r\) are coprime, \(n\) has an inverse modulo \(r\). The article defines

$$
n' = n^{-1}\pmod r.
$$

Multiply both sides of

$$
x\equiv qn\pmod r
$$

by \(n'\):

$$
xn'\equiv qnn'\pmod r.
$$

Since

$$
nn'\equiv1\pmod r,
$$

we get

$$
\boxed{q\equiv xn'\pmod r}.
$$

So we can choose

$$
\boxed{q=xn'\bmod r}.
$$

And because modular multiplication lets us reduce operands first,

$$
xn'\bmod r
=
\boxed{(x\bmod r)n'\bmod r}.
$$

That's exactly the line you're looking at.

---

### Small numerical example

Suppose

$$
n=5,\qquad r=8.
$$

We need

$$
n'=5^{-1}\pmod8.
$$

Since

$$
5\cdot5=25\equiv1\pmod8,
$$

we have \(n'=5\).

Now suppose \(x=37\). Compute:

$$
q=(37\bmod8)\cdot5\bmod8
$$

$$
=5\cdot5\bmod8
=25\bmod8
=\boxed1.
$$

Why did we choose \(q=1\)? Look:

$$
x-qn=37-(1)(5)=32.
$$

And voilà:

$$
32/8=4
$$

is an exact integer.

That's **the entire reason for choosing \(q\) this way**. We manufacture \(q\) so that \(x-qn\) has \(r\) as a factor.

And there's a second clever thing coming: because \(r\) is normally \(2^k\), both `x mod r` and `/ r` are extremely cheap binary operations. That's where Montgomery reduction gets its speed.

# Why / How Montgomery is Good

Exactly — this is the right comparison to make. The algorithm in your image is **already avoiding a general `% N` operation**, so the question becomes: why bother with Montgomery?

The main difference is **how much work is needed per modular multiplication**.

### Your algorithm: bit-by-bit modular multiplication

Your image computes

$$
A B \bmod N
$$

by processing **every bit of \(B\)**:

$$
R \leftarrow 2R + A B_i
$$

and then reducing \(R\) with up to two subtractions:

```text
for each bit of B:
    R = 2R + A*bit

    if R >= N:
        R = R - N

    if R >= N:
        R = R - N
```

Suppose \(B\) is a 2048-bit RSA number. One multiplication requires **2048 iterations**.

Each iteration needs roughly:

```text
shift
+
conditional add
+
compare/subtract
+
compare/subtract
```

So the advantage is that you don't need a divider or a huge multiplier. The disadvantage is that multiplication is **serial**: you process \(B\) one bit at a time.

---

### Montgomery: use a multiplier, then do a cheap reduction

Montgomery takes a different approach.

If your hardware already has a large multiplier, you first calculate

$$
T=A_{\text{Mont}}B_{\text{Mont}}.
$$

That multiplication can potentially be done by a dedicated multiplier much faster than processing one bit per cycle.

You then need to reduce \(T\). Normally you'd want

$$
T\bmod N,
$$

which would involve an awkward division by arbitrary \(N\).

Montgomery instead computes

$$
\operatorname{REDC}(T)=Tr^{-1}\bmod N
$$

using

$$
q=(T\bmod r)n'\bmod r
$$

and

$$
a=\frac{T-qN}{r}.
$$

As your notes point out, choosing

$$
r=2^m
$$

turns the operations involving \(r\) into bit operations: \(T\bmod r\) means selecting the lowest \(m\) bits, and division by \(r\) is a right shift. 

So conceptually:

```text
Your image:

        B0 → iteration
        B1 → iteration
        B2 → iteration
             ...
        B2047 → iteration
                 ↓
              A*B mod N


Montgomery:

          A × B
            ↓
          large T
            ↓
           REDC
            ↓
        result mod N
```

### But Montgomery isn't automatically faster

This is important, especially if you're implementing this in hardware.

If you **don't have a fast multiplier**, Montgomery isn't magically faster. The multiplication

$$
A\times B
$$

and the multiplication

$$
(T\bmod r)n'
$$

still have to be implemented somehow.

Your bit-serial algorithm is actually attractive when you want **small, simple hardware**. It trades speed for area: you can reuse a relatively small datapath over many clock cycles.

Montgomery becomes especially attractive when you're doing something like RSA:

$$
M^e\bmod N,
$$

because modular exponentiation performs **lots and lots of modular multiplications**. You pay once to enter Montgomery space, repeatedly perform efficient Montgomery multiplications, and then pay once to leave Montgomery space. That's also the motivation given in your notes. 

So I would think of the tradeoff like this:

|                                                | Your bit-by-bit algorithm | Montgomery                         |
| ---------------------------------------------- | ------------------------- | ---------------------------------- |
| General division                               | No                        | No                                 |
| Large multiplier required                      | No                        | Usually yes*                       |
| Iterations per multiplication                  | ~number of bits           | Depends on multiplier architecture |
| Hardware area                                  | Potentially small         | Potentially larger                 |
| Good for many repeated modular multiplications | Yes, but slower           | **This is its main use case**      |
| RSA \(M^e\bmod N\)                             | Works                     | Particularly useful                |

*There are also **bit-serial/radix Montgomery multiplier architectures**, so Montgomery itself doesn't inherently require a one-cycle giant multiplier.

And that last point is probably particularly relevant to what you're learning: **Montgomery is a reduction technique, not a particular multiplier architecture.** You can even build a Montgomery multiplier that processes operands bit-by-bit, similar in spirit to the algorithm in your screenshot.

So if your goal is ultimately a VHDL implementation of \(M^e\bmod N\), the interesting comparison isn't really "`%` vs Montgomery"; it's **interleaved modular multiplication vs Montgomery modular multiplication**, including cycles, multiplier size, comparator/subtractor requirements, and critical path.


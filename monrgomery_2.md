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


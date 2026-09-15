Absolutely. Ignore Montgomery for a moment. The orange algorithm is simply a clever way of computing

$$
\boxed{A\cdot B \bmod N}
$$

without ever constructing the potentially huge product \(A\cdot B\).

The slide assumes \(A<N\) and processes the bits of \(B\) one at a time. 

### What is \(B\)?

\(A\) and \(B\) are simply **the two numbers you want to multiply**.

For example, suppose during RSA the green algorithm needs to calculate

$$
C'P\bmod N.
$$

Then you can say

$$
A=C',\qquad B=P.
$$

Or when the green algorithm needs

$$
P\cdot P\bmod N,
$$

you could have

$$
A=P,\qquad B=P.
$$

So \(B\) has nothing specifically to do with RSA's \(M,e,N\). It's just the name given to the **second operand of the modular multiplier**.

---

### Why does processing the bits of \(B\) give \(AB\)?

Suppose, for a small example,

$$
A=5,\qquad B=11.
$$

Binary \(B\) is

$$
B=1011_2.
$$

Therefore

$$
B=1\cdot2^3+0\cdot2^2+1\cdot2^1+1\cdot2^0.
$$

Multiply the whole thing by \(A\):

$$
AB=A(1\cdot2^3+0\cdot2^2+1\cdot2+1).
$$

The algorithm processes those bits from **left to right**:

$$
1,\;0,\;1,\;1.
$$

It starts:

$$
R=0.
$$

For every bit, it performs

$$
\boxed{R\leftarrow2R+A\cdot\text{bit}}.
$$

Let's actually do it.

For the first bit, `1`:

$$
R=2(0)+5(1)=5.
$$

For the second bit, `0`:

$$
R=2(5)+5(0)=10.
$$

For the third bit, `1`:

$$
R=2(10)+5(1)=25.
$$

For the fourth bit, `1`:

$$
R=2(25)+5(1)=55.
$$

And look:

$$
55=5\cdot11=A B.
$$

So this little shift-and-add procedure has constructed the multiplication.

It's basically the binary equivalent of how you can construct decimal 123 one digit at a time:

$$
0\rightarrow1\rightarrow12\rightarrow123
$$

using

$$
x_{\text{new}}=10x_{\text{old}}+\text{next digit}.
$$

In binary, instead of multiplying by 10, you multiply by **2**.

---

## Now add the modulo

Suppose

$$
A=5,\quad B=11,\quad N=13.
$$

We want

$$
5\cdot11\bmod13=55\bmod13=3.
$$

The slide doesn't wait until the end to calculate `% 13`. It reduces \(R\) **during every iteration**:

$$
R\leftarrow2R+A\cdot\text{bit}
$$

followed by

$$
R\leftarrow R\bmod N.
$$



Let's do that:

| Bit of \(B=1011\) | \(2R+A\cdot bit\) | Reduce mod 13 |
| ----------------- | ----------------: | ------------: |
| 1                 |      \(2(0)+5=5\) |             5 |
| 0                 |     \(2(5)+0=10\) |            10 |
| 1                 |    \(2(10)+5=25\) |            12 |
| 1                 |    \(2(12)+5=29\) |             3 |

Result:

$$
\boxed{R=3}.
$$

And indeed,

$$
5\cdot11\bmod13=\boxed3.
$$

This is called **interleaved reduction**: instead of building the entire \(AB\) first and then reducing it, you keep reducing the partial result as you go.

---

# Why are only two subtractions enough?

This is the particularly clever hardware part.

After every iteration's reduction, the algorithm guarantees:

$$
\boxed{0\le R<N}.
$$

Equivalently,

$$
R\le N-1.
$$

Now we enter the **next iteration**:

$$
R_{\text{new}}=2R+A\cdot bit.
$$

We know

$$
R\le N-1.
$$

Therefore:

$$
2R\le2(N-1).
$$

We also know

$$
A\le N-1.
$$

And `bit` is either 0 or 1, so the biggest \(A\cdot bit\) can possibly be is

$$
A\cdot1\le N-1.
$$

Therefore the **absolute largest possible new \(R\)** is

$$
2(N-1)+(N-1).
$$

So

$$
\boxed{R_{\text{new}}\le3N-3}.
$$

That's exactly the bound given on your slide. 

Now consider the worst case:

$$
R_{\text{new}}=3N-3.
$$

Subtract \(N\) once:

$$
3N-3-N=2N-3.
$$

That might still be \(\ge N\), so one subtraction isn't necessarily sufficient.

Subtract \(N\) a **second time**:

$$
2N-3-N=N-3.
$$

And now

$$
N-3<N.
$$

So after at most two subtractions, you're guaranteed to have

$$
\boxed{0\le R<N}.
$$

That's why the slide replaces expensive

```text
R = R mod N
```

with:

```text
if R >= N:
    R = R - N

if R >= N:
    R = R - N
```



The key thing to remember is:

$$
\boxed{
R<N
\;\Longrightarrow\;
2R+A\cdot bit <3N
\;\Longrightarrow\;
\text{at most 2 subtractions of }N
}
$$

And **this orange algorithm is the thing Montgomery multiplication would replace** in your design. The green square-and-multiply algorithm above it remains your exponentiation algorithm.

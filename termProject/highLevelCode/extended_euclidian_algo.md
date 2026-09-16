Yes. These two functions are just there to calculate the modular inverse

$$
\boxed{n' = n^{-1}\pmod r}
$$

that Montgomery setup needs. Your code implements them here. 

Let's keep using

$$
n=13,\qquad r=16.
$$

So ultimately we're trying to find

$$
13^{-1}\pmod{16}.
$$

We already know the answer should be \(5\), because

$$
13\cdot5=65\equiv1\pmod{16}.
$$

## First: what does `egcd` actually do?

Your function is:

```python
def egcd(a, b):
    """Extended Euclidean algorithm,
       returns (g, x, y) so that a*x + b*y = g"""

    if a == 0:
        return b, 0, 1

    g, x1, y1 = egcd(b % a, a)

    x = y1 - (b // a) * x1
    y = x1

    return g, x, y
```

The important thing is the comment:

$$
\boxed{ax+by=g}
$$

where

$$
g=\gcd(a,b).
$$

So `egcd(a,b)` doesn't just find the gcd. It also finds \(x\) and \(y\) satisfying

$$
ax+by=\gcd(a,b).
$$

For our numbers:

$$
\operatorname{egcd}(13,16)
$$

will eventually give us

$$
(1,5,-4)
$$

because

$$
13(5)+16(-4)=1.
$$

Check:

$$
65-64=1.
$$

And **that 5 is exactly the number Montgomery wants.**

Why? Take

$$
13(5)+16(-4)=1
$$

modulo 16:

$$
13(5)+16(-4)\equiv1\pmod{16}.
$$

But

$$
16(-4)\equiv0\pmod{16},
$$

so

$$
13(5)\equiv1\pmod{16}.
$$

Therefore

$$
\boxed{13^{-1}\equiv5\pmod{16}}.
$$

That's the connection between extended Euclid and modular inverse.

---

## Now let's actually execute `egcd(13,16)`

The first call is

```python
egcd(13, 16)
```

`a` isn't zero, so:

```python
g, x1, y1 = egcd(b % a, a)
```

becomes

```python
egcd(16 % 13, 13)
```

and

$$
16\bmod13=3,
$$

so:

```text
egcd(13, 16)
    ↓
egcd(3, 13)
```

Again:

$$
13\bmod3=1
$$

so:

```text
egcd(13, 16)
    ↓
egcd(3, 13)
    ↓
egcd(1, 3)
```

Again:

$$
3\bmod1=0
$$

so:

```text
egcd(13, 16)
    ↓
egcd(3, 13)
    ↓
egcd(1, 3)
    ↓
egcd(0, 1)
```

Now we hit:

```python
if a == 0:
    return b, 0, 1
```

so

```python
egcd(0, 1)
```

returns

```python
(1, 0, 1)
```

because

$$
0(0)+1(1)=1.
$$

Now the recursion starts going **back upward**.

---

### Returning to `egcd(1,3)`

We got:

```python
g  = 1
x1 = 0
y1 = 1
```

The code does:

```python
x = y1 - (b // a) * x1
y = x1
```

Here \(a=1,b=3\):

$$
x=1-(3//1)(0)=1
$$

$$
y=0.
$$

So it returns

```python
(1, 1, 0)
```

Check:

$$
1(1)+3(0)=1.
$$

---

### Returning to `egcd(3,13)`

Now:

```python
g  = 1
x1 = 1
y1 = 0
```

and \(a=3,b=13\).

Therefore:

$$
x=0-(13//3)(1)
$$

$$
=0-4=-4
$$

and

$$
y=1.
$$

So:

```python
egcd(3, 13)
```

returns

```python
(1, -4, 1)
```

Check:

$$
3(-4)+13(1)
=-12+13
=1.
$$

---

### Finally, back to `egcd(13,16)`

Now:

```python
g  = 1
x1 = -4
y1 = 1
```

and \(a=13,b=16\).

So:

$$
x=1-(16//13)(-4)
$$

Since

$$
16//13=1,
$$

we get

$$
x=1-1(-4)=5.
$$

And

$$
y=-4.
$$

So:

```python
egcd(13, 16)
```

returns

$$
\boxed{(1,5,-4)}.
$$

Which tells us:

$$
\boxed{13(5)+16(-4)=1}.
$$

---

## Now `modinv` becomes very simple

Your other function is:

```python
def modinv(a, m):
    """Modular inverse of a mod m,
       using the extended Euclidean algorithm"""

    g, x, _ = egcd(a % m, m)

    if g != 1:
        raise ValueError(
            "no inverse exists, a and m are not coprime"
        )

    return x % m
```

For Montgomery setup, you call:

```python
n_prime = modinv(n, r)
```

so:

```python
modinv(13, 16)
```

First:

```python
g, x, _ = egcd(13 % 16, 16)
```

Since \(13<16\):

$$
13\bmod16=13.
$$

So that's just:

```python
g, x, _ = egcd(13, 16)
```

We just calculated:

```python
(1, 5, -4)
```

Therefore:

```python
g = 1
x = 5
```

The `_` means:

> "There is a third returned value, but I don't care about it."

Then:

```python
if g != 1:
```

checks that the numbers are coprime.

We have

$$
g=1,
$$

so we're good.

Finally:

```python
return x % m
```

gives

$$
5\bmod16=5.
$$

Therefore:

$$
\boxed{\operatorname{modinv}(13,16)=5}
$$

and setup stores

```python
n_prime = 5
```

which means

$$
\boxed{13(5)\equiv1\pmod{16}}.
$$

So the entire chain is:

```text
montgomery_setup(n=13)
        │
        │ r = 16
        ▼
modinv(13, 16)
        │
        ▼
egcd(13, 16)
        │
        │ finds:
        │
        │ 13(5) + 16(-4) = 1
        ▼
      x = 5
        │
        ▼
   5 mod 16
        │
        ▼
    n_prime = 5
```

The one part we haven't really explained yet is **why these strange lines**

```python
x = y1 - (b // a) * x1
y = x1
```

correctly work backward through the Euclidean algorithm. That's the actual mathematical heart of **extended** Euclid, and it's worth deriving separately rather than just accepting those two lines.

# High Level Code

This is the folder where we place everything relevant to the high level code for the algorithm "Montgomery"

# Specifications


```txt
|------     ---|---    -------|        
|      |       |       |       
|------        |       |   ---|
|      |       |       |      |
|------     ---|---    |------|  comment
```



High level implementation of algorithm for M^e mod n, using Montgomery multiplication

Link to algorithm explanations:

Montgromery multiplication:
https://cp-algorithms.com/algebra/montgomery_multiplication.html

Extended Euclidean algorithm:
https://cp-algorithms.com/algebra/extended-euclid-algorithm.html

Specifications:
$M < n$, $r > n$

$r = 2^x$, $n = 2m - 1$ $\rightarrow$ $gcd(n,r) = 1$


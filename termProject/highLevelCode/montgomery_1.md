# Chat-GPT sier: 

**Promt: 
Kan du gå gjennom denne med meg: https://cp-algorithms.com/algebra/montgomery_multiplication.html**

Ja. Siden du jobber med digitaldesign/VHDL, er Montgomery multiplication spesielt relevant fordi hele poenget er å erstatte kostbar **divisjon/modulo med bitoperasjoner, addisjon og multiplikasjon**, som passer mye bedre i hardware. Artikkelen hopper ganske raskt inn i matematikken, så jeg ville bygget forståelsen nedenfra. ([CP-Algorithms][1])

[Montgomery Multiplication – CP-Algorithms](https://cp-algorithms.com/algebra/montgomery_multiplication.html)

## 1. Problemet Montgomery prøver å løse

Vi ønsker ofte å beregne

$$
x\cdot y \pmod n
$$

Eksempel:

$$
7\cdot11 \pmod{13}
$$

Først:

$$
7\cdot11=77
$$

og

$$
77\bmod13=12
$$

Problemet er ikke multiplikasjonen. Problemet er `mod 13`.

For en generell modulus innebærer dette i praksis en form for **divisjon**, og divisjon er relativt dyrt, særlig i hardware og med store tall. Montgomery-metoden gjør derfor noe ganske smart: den endrer representasjonen av tallene slik at reduksjon modulo \(n\) kan utføres uten generell divisjon. ([CP-Algorithms][1])

---

## 2. Vi introduserer \(r\)

Montgomery velger et tall

$$
r\ge n
$$

slik at

$$
\gcd(r,n)=1.
$$

I hardware velger vi nesten alltid

$$
\boxed{r=2^m}
$$

fordi da er:

$$
x\bmod r
$$

bare de nederste \(m\) bitene, og

$$
x/r
$$

bare et høyreskift med \(m\) bits. Det er en enorm fordel i digital hardware. ([CP-Algorithms][1])

Hvis for eksempel

$$
n=13,
$$

kan vi velge

$$
r=16=2^4.
$$

Binært:

$$
r=10000_2.
$$

Da blir eksempelvis

$$
10110110_2\bmod 10000_2=0110_2.
$$

Vi trenger altså bare de **fire nederste bitene**.

---

# 3. Montgomery representation

Nå kommer første litt rare idé.

I stedet for å representere \(x\) som \(x\), representerer vi det som

$$
\boxed{\bar{x}=xr\bmod n}
$$

Artikkelen kaller dette Montgomery space. ([CP-Algorithms][1])

La oss fortsette med

$$
n=13,\qquad r=16.
$$

Hvis

$$
x=7,
$$

blir Montgomery-representasjonen:

$$
\bar{x}=7\cdot16\bmod13.
$$

Siden

$$
112=8\cdot13+8,
$$

får vi

$$
\boxed{\bar 7=8}.
$$

Merk hva dette betyr:

**Tallet 8 representerer nå egentlig tallet 7.**

Det kan virke unødvendig komplisert akkurat nå. Gevinsten kommer når vi skal gjøre **mange multiplikasjoner modulo \(n\)**.

---

# 4. Problemet med vanlig multiplikasjon

Anta at vi har to tall i Montgomery-form:

$$
\bar{x}=xr
$$

og

$$
\bar{y}=yr
$$

(modulo \(n\)).

Hvis vi bare multipliserer dem:

$$
\bar{x}\bar{y}
$$

får vi:

$$
(xr)(yr)
=
xy r^2.
$$

Men Montgomery-representasjonen av \(xy\) skal være

$$
\overline{xy}=xy r.
$$

Vi har altså fått én \(r\) for mye:

$$
xy r^2
$$

i stedet for

$$
xy r.
$$

Derfor må vi på en eller annen måte **dele bort én \(r\)**.

Modulo \(n\) gjør vi dette ved å multiplisere med den modulære inversen:

$$
r^{-1}.
$$

Dermed defineres Montgomery multiplication som

$$
\boxed{
\bar{x}*\bar{y}
=
\bar{x}\bar{y}r^{-1}\pmod n
}
$$

slik artikkelen viser. ([CP-Algorithms][1])

For:

$$
(xr)(yr)r^{-1}
$$

gir

$$
xy r^2r^{-1}
$$

og siden

$$
rr^{-1}\equiv1\pmod n,
$$

får vi

$$
xy r.
$$

Perfekt. Vi er fortsatt i Montgomery representation.

---

# 5. Men hva er \(r^{-1}\)?

Dette er **modular inverse**.

Vi ønsker et tall \(r^{-1}\) slik at

$$
r\cdot r^{-1}\equiv1\pmod n.
$$

Med

$$
r=16,\qquad n=13
$$

kan vi redusere:

$$
16\equiv3\pmod{13}.
$$

Vi trenger derfor:

$$
3r^{-1}\equiv1\pmod{13}.
$$

Prøv \(r^{-1}=9\):

$$
3\cdot9=27
$$

og

$$
27\bmod13=1.
$$

Dermed:

$$
\boxed{r^{-1}=9}.
$$

---

# 6. Så kommer den viktige delen: Montgomery reduction

Så langt kan det virke som om vi bare har flyttet problemet.

Vi ønsker å beregne:

$$
x r^{-1}\pmod n.
$$

Hvis vi faktisk måtte utføre vanlig modulo/divisjon her, hadde vi ikke vunnet noe.

Det er **REDC-algoritmen** som løser dette. Artikkelen introduserer identiteten

$$
\boxed{
rr^{-1}+nn'=1
}
$$

som eksisterer fordi

$$
\gcd(r,n)=1.
$$

Dette kommer fra Bézouts identitet / extended Euclidean algorithm. ([CP-Algorithms][1])

Omskriv:

$$
rr^{-1}=1-nn'
$$

og dermed

$$
r^{-1}=\frac{1-nn'}{r}.
$$

Multipliser med \(x\):

$$
xr^{-1}
=
\frac{x-xnn'}{r}.
$$

Dette er nøkkeluttrykket.

Problemet er at telleren ikke nødvendigvis ser praktisk ut. Derfor velger Montgomery en verdi \(q\) slik at telleren blir **nøyaktig delelig på \(r\)**.

---

# 7. REDC-algoritmen

Artikkelen ender opp med: ([CP-Algorithms][1])

```text
q = (x mod r) * n' mod r

a = (x - q*n) / r

if a < 0:
    a += n

return a
```

Dette ser kanskje fortsatt mystisk ut, men legg merke til operasjonene dersom

$$
r=2^m.
$$

Da blir:

### `x mod r`

Bare:

```text
de m nederste bitene
```

### `... mod r`

Igjen:

```text
de m nederste bitene
```

### `/ r`

Siden

$$
r=2^m
$$

er dette:

```text
shift right m bits
```

Så noe som matematisk ser ganske komplisert ut:

$$
xr^{-1}\pmod n
$$

kan implementeres omtrent med:

```text
bit selection
      ↓
multiplication
      ↓
subtraction
      ↓
shift
      ↓
conditional addition
```

Ingen generell divider.

**Det er dette som er den store ideen bak Montgomery multiplication.**

---

## 8. Hvorfor kan vi bare kaste de nederste bitene?

Dette er kanskje det viktigste å forstå dersom du skal implementere algoritmen i VHDL.

Vi konstruerer:

$$
x-qn
$$

slik at

$$
x-qn\equiv0\pmod r.
$$

Det betyr at tallet er delelig på \(r\).

Hvis

$$
r=2^4=16,
$$

betyr det at de fire nederste bitene må være:

```text
.... 0000
```

Eksempel:

```text
1011010000
      ^^^^
      0000
```

Divisjon med \(16\) er derfor bare:

```text
1011010000 >> 4
```

som gir

```text
101101
```

Montgomery-algoritmen **velger altså \(q\) nettopp for å tvinge de nederste bitene til null**.

Dette er en veldig hardware-vennlig idé.

---

# 9. Hele konseptet i ett bilde

Hvis vi vil beregne mange ting modulo \(n\):

$$
a\cdot b\cdot c\cdot d\pmod n,
$$

gjør Montgomery:

```text
NORMAL SPACE

a       b       c       d
│       │       │       │
▼       ▼       ▼       ▼
×r mod n
│
▼
────────────────────────────
     MONTGOMERY SPACE

ā * b̄
  │
  ▼
REDC
  │
  ▼
āb̄ * c̄
  │
  ▼
REDC
  │
  ▼
...
────────────────────────────
            │
            ▼
       final REDC
            │
            ▼

NORMAL SPACE
```

Det koster altså noe å **gå inn og ut** av Montgomery space, men hvis RSA eller en annen algoritme skal gjøre hundrevis/tusenvis av modulære multiplikasjoner, sparer man mye underveis. Artikkelen fremhever nettopp dette poenget. ([CP-Algorithms][1])

---

## Det jeg ville fokusert på først

Ikke bekymre deg for C++-implementasjonen eller "Fast inverse trick" nederst på siden ennå. De er implementasjonsoptimaliseringer. Først ville jeg sørget for at disse fire tingene sitter:

1. Hvorfor velger vi \(r=2^m\)?
2. Hva betyr \(\bar{x}=xr\bmod n\)?
3. Hvorfor får vi en ekstra \(r\) når vi multipliserer to Montgomery-tall?
4. Hvordan velger REDC \(q\) slik at de nederste \(m\) bitene blir null?

Når **punkt 4** gir intuitiv mening, faller veldig mye av resten på plass.

Vi kan gjerne ta et **fullstendig lite eksempel med binærtall**, for eksempel \(n=13,\ r=16,\ x=7,\ y=11\), og gjennomføre Montgomery multiplication helt for hånd. Det tror jeg vil være den mest nyttige neste delen før vi ser på hvordan dette kan implementeres med registre, addere og shifts i VHDL.

[1]: https://cp-algorithms.com/algebra/montgomery_multiplication.html "Montgomery Multiplication - Algorithms for Competitive Programming"


# Eksempel:

Ja. La oss bruke det samme eksemplet:

$$
\boxed{x=7,\quad y=11,\quad n=13,\quad r=16=2^4}
$$

Målet er å beregne

$$
7\cdot11\bmod13.
$$

Vanlig regning gir \(77\bmod13=12\), så vi vet at svaret skal bli **12**. Nå gjør vi hele operasjonen med Montgomery multiplication.

### 1. Finn konstantene \(r^{-1}\) og \(n'\)

CP-algorithms bruker relasjonen

$$
rr^{-1}+nn'=1.
$$

Vi har \(r=16\) og \(n=13\), så vi trenger

$$
16r^{-1}+13n'=1.
$$

Extended Euclidean algorithm gir:

$$
16=1\cdot13+3
$$

$$
13=4\cdot3+1
$$

Dermed

$$
1=13-4(16-13)=5\cdot13-4\cdot16.
$$

Altså:

$$
\boxed{r^{-1}=-4}
$$

og

$$
\boxed{n'=5}.
$$

Merk at \(r^{-1}=-4\) her er Bézout-koeffisienten. Modulo 13 er dette det samme som \(9\), siden \(-4\equiv9\pmod{13}\).

Vi kan kontrollere:

$$
16(-4)+13(5)=-64+65=1.
$$

---

### 2. Konverter \(x=7\) til Montgomery space

Montgomery-representasjonen er

$$
\bar{x}=xr\bmod n.
$$

Dermed:

$$
\bar 7=7\cdot16\bmod13.
$$

$$
112\bmod13=8.
$$

Så:

$$
\boxed{\bar 7=8}.
$$

Binært:

```text
7  = 0111
        ↓ × r mod 13
8  = 1000
```

Tallet `1000` representerer altså nå 7 i Montgomery space.

---

### 3. Konverter \(y=11\)

Samme prosess:

$$
\bar{11}=11\cdot16\bmod13.
$$

$$
176\bmod13=7.
$$

Dermed:

$$
\boxed{\bar{11}=7}.
$$

Så vi har:

$$
7\rightarrow8
$$

$$
11\rightarrow7.
$$

---

### 4. Multipliser Montgomery-representasjonene

Nå gjør vi vanlig multiplikasjon:

$$
T=\bar7\cdot\bar{11}
$$

$$
T=8\cdot7=\boxed{56}.
$$

Binært:

$$
56=00111000_2.
$$

Men dette er ikke ferdig. Vi har:

$$
(xr)(yr)=xyr^2.
$$

Vi ønsker bare \(xyr\). Derfor må Montgomery reduction, REDC, fjerne én faktor \(r\).

---

### 5. Beregn \(q\)

Formelen fra artikkelen er:

$$
q=(T\bmod r)n'\bmod r.
$$

Vi har

$$
T=56,\quad r=16,\quad n'=5.
$$

Først:

$$
56\bmod16=8.
$$

Så:

$$
q=8\cdot5\bmod16
$$

$$
=40\bmod16
$$

$$
\boxed{q=8}.
$$

Dette er spesielt interessant binært. Fordi \(r=16=2^4\), betyr `mod 16` bare **behold de fire nederste bitene**:

```text
T = 56

0011 1000
     ^^^^
     1000 = 8
```

Ingen divider er nødvendig.

---

### 6. Beregn \(a\)

REDC sier nå:

$$
a=\frac{T-qn}{r}.
$$

Sett inn:

$$
a=\frac{56-8\cdot13}{16}
$$

$$
=\frac{56-104}{16}
$$

$$
=\frac{-48}{16}
$$

$$
\boxed{a=-3}.
$$

Siden \(a<0\), legger algoritmen til \(n\):

$$
a=-3+13=10.
$$

Dermed:

$$
\boxed{a=10}.
$$

---

### 7. Hva i all verden er 10?

Vi startet med

$$
7\cdot11=77\equiv12\pmod{13}.
$$

Så hvorfor fikk vi **10**?

Fordi vi **fortsatt er i Montgomery space**.

Resultatet skal være Montgomery-representasjonen av 12:

$$
\bar{12}=12\cdot16\bmod13.
$$

Siden

$$
192\bmod13=10,
$$

får vi:

$$
\boxed{\bar{12}=10}.
$$

Perfekt.

Vi har altså gjort:

$$
\boxed{\bar7\cdot\bar{11}\xrightarrow{\text{REDC}}\bar{12}}
$$

eller numerisk:

$$
\boxed{8\cdot7\xrightarrow{\text{REDC}}10}.
$$

---

### 8. Konverter tilbake til vanlig representasjon

Til slutt ønsker vi faktisk `12`, ikke Montgomery-representasjonen `10`.

For å gå ut av Montgomery space bruker vi REDC én gang til:

$$
\operatorname{REDC}(10).
$$

Beregn igjen:

$$
q=(10\bmod16)\cdot5\bmod16.
$$

$$
q=10\cdot5\bmod16
$$

$$
=50\bmod16=2.
$$

Deretter:

$$
a=\frac{10-2\cdot13}{16}
$$

$$
=\frac{-16}{16}
$$

$$
=-1.
$$

Negativt, så legg til \(n=13\):

$$
-1+13=\boxed{12}.
$$

Og dermed:

$$
\boxed{7\cdot11\bmod13=12}.
$$

## Hele regnestykket

Det kan oppsummeres slik:

```text
              Normal space
              7        11
              │         │
            ×16       ×16
            mod13     mod13
              │         │
              ▼         ▼
              8         7
               \       /
                \     /
                 8 × 7
                   │
                   ▼
                  56
                   │
                 REDC
                   │
                   ▼
                  10       ← Montgomery-representasjon av 12
                   │
                 REDC
                   │
                   ▼
                  12
                   │
                   ▼
              Normal space
```

Det mest interessante fra et **hardware/VHDL-perspektiv** er steg 5–6. Vi hadde

$$
q=(T\bmod16)\cdot5\bmod16.
$$

`mod 16` betyr bare at vi beholder **4 LSB**. Deretter konstruerer vi

$$
T-qn.
$$

Montgomery-algoritmen garanterer at dette er delelig med \(16\). I vårt tilfelle:

$$
56-8(13)=-48.
$$

Og fordi \(16=2^4\):

$$
\frac{-48}{16}
$$

tilsvarer i binær hardware i prinsippet et **4-bit høyreskift** (med riktig håndtering av signed arithmetic).

Det er kjernen i hele trikset: **velg \(q\) slik at divisjonen du til slutt må gjøre alltid er divisjon med \(2^m\)**. Da blir en kostbar generell modulo/divisjon erstattet av bit selection og shifting.

Neste naturlige steg er egentlig å ta akkurat `REDC`-delen og tegne hvordan den kan bygges som **datapath med multiplikatorer, adder/subtraktor, mux og registre**. Det gjør koblingen til VHDL mye tydeligere.


# Matematisk bevis

... (Henrik)
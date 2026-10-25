# Laplace Image of the Heat–Hold–Cool Boundary History

## The boundary history

Trapezoidal "heat–hold–cool" program with peak level $M$ and knots $0 < t_A \le t_B < t_C$:

$$
f(t) =
\begin{cases}
\dfrac{M\,t}{t_A}, & 0 \le t \le t_A \quad \text{(heat)}\\[2ex]
M, & t_A \le t \le t_B \quad \text{(hold)}\\[2ex]
\dfrac{M\,(t_C - t)}{t_C - t_B}, & t_B \le t \le t_C \quad \text{(cool)}\\[2ex]
0, & t \ge t_C
\end{cases}
$$

Goal: the Laplace image

$$
F(s) = \mathcal{L}\{f\}(s) = \int_0^\infty e^{-st} f(t)\,dt .
$$

## Step 1: Identify the slopes and their changes

The slope of $f$ on each interval:

$$
f'(t) = \begin{cases}
m_1 = \dfrac{M}{t_A}, & 0 < t < t_A\\[1.5ex]
m_2 = 0, & t_A < t < t_B\\[1ex]
m_3 = -\dfrac{M}{t_C - t_B}, & t_B < t < t_C\\[1.5ex]
m_4 = 0, & t > t_C
\end{cases}
$$

The slope *changes* at the four knots $\tau \in \{0,\, t_A,\, t_B,\, t_C\}$:

$$
\Delta_0 = m_1 - 0 = \frac{M}{t_A}, \qquad
\Delta_{t_A} = m_2 - m_1 = -\frac{M}{t_A},
$$

$$
\Delta_{t_B} = m_3 - m_2 = -\frac{M}{t_C - t_B}, \qquad
\Delta_{t_C} = m_4 - m_3 = +\frac{M}{t_C - t_B}.
$$

## Step 2: Write $f$ as a sum of shifted ramps

Define the ramp $(t - \tau)_+ = \max(t - \tau,\, 0)$: zero before $\tau$, growing with slope $1$ after. A continuous piecewise-linear function with $f(0) = 0$ is exactly

$$
f(t) = \sum_k \Delta_{\tau_k}\,(t - \tau_k)_+ ,
$$

because each ramp switches on slope $\Delta_{\tau_k}$ at its knot, and continuity is automatic (ramps are continuous). Explicitly:

$$
f(t) = \frac{M}{t_A}\,(t)_+ \;-\; \frac{M}{t_A}\,(t - t_A)_+ \;-\; \frac{M}{t_C - t_B}\,(t - t_B)_+ \;+\; \frac{M}{t_C - t_B}\,(t - t_C)_+ .
$$

**Verification on each interval:**

- $0 \le t \le t_A$: only the first ramp is active: $f = \frac{M}{t_A}t$ ✓ (heating)
- $t_A \le t \le t_B$: first two active: $\frac{M}{t_A}t - \frac{M}{t_A}(t - t_A) = M$ ✓ (hold)
- $t_B \le t \le t_C$: three active: $M - \frac{M}{t_C - t_B}(t - t_B)$, linear from $M$ down to $0$ ✓ (cooling)
- $t \ge t_C$: all four active; the fourth adds $+\frac{M}{t_C - t_B}(t - t_C)$, exactly cancelling the ongoing decrease: $f \equiv 0$ ✓

The last check is the important one: the slope changes sum to zero,

$$
\sum_k \Delta_{\tau_k} = 0,
$$

which is what makes the schedule return to a constant (here zero) instead of drifting.

## Step 3: Transform each ramp

Two standard ingredients.

**(a) The basic ramp.** By integration by parts (for $\operatorname{Re} s > 0$):

$$
\mathcal{L}\{t\}(s) = \int_0^\infty t\, e^{-st}\,dt
= \left[-\frac{t\,e^{-st}}{s}\right]_0^\infty + \frac{1}{s}\int_0^\infty e^{-st}\,dt
= 0 + \frac{1}{s}\cdot\frac{1}{s} = \frac{1}{s^2}.
$$

**(b) The shift (delay) rule.** Substituting $t' = t - \tau$:

$$
\mathcal{L}\{g(t-\tau)\,\mathbb{1}_{t>\tau}\}(s)
= \int_\tau^\infty e^{-st}\, g(t-\tau)\,dt
= e^{-s\tau} \int_0^\infty e^{-st'} g(t')\,dt'
= e^{-s\tau}\, G(s).
$$

Combining (a) and (b):

$$
\mathcal{L}\{(t - \tau)_+\}(s) = \frac{e^{-s\tau}}{s^2}.
$$

## Step 4: Assemble by linearity

The Laplace transform is linear, so the ramp sum transforms term by term:

$$
F(s) = \frac{1}{s^2}\left[\frac{M}{t_A} - \frac{M}{t_A}e^{-s t_A} - \frac{M}{t_C - t_B}e^{-s t_B} + \frac{M}{t_C - t_B}e^{-s t_C}\right].
$$

Grouping the terms sharing a denominator:

$$
\boxed{\;F(s) = \frac{M}{s^2}\left[\frac{1 - e^{-s t_A}}{t_A} \;-\; \frac{e^{-s t_B} - e^{-s t_C}}{t_C - t_B}\right]\;}
$$

## Step 5: Rewrite in the $\varphi$-form

Introduce the entire function

$$
\varphi(z) = \frac{1 - e^{-z}}{z}, \qquad \varphi(0) = 1.
$$

Factor each group to expose $\varphi$:

$$
\frac{1 - e^{-s t_A}}{s^2\, t_A} = \frac{1}{s}\cdot\frac{1 - e^{-s t_A}}{s\, t_A} = \frac{\varphi(s\, t_A)}{s},
$$

and for the cooling pair, factor out the delay $e^{-s t_B}$:

$$
\frac{e^{-s t_B} - e^{-s t_C}}{s^2 (t_C - t_B)}
= e^{-s t_B}\cdot \frac{1 - e^{-s (t_C - t_B)}}{s^2 (t_C - t_B)}
= \frac{e^{-s t_B}\,\varphi\big(s(t_C - t_B)\big)}{s},
$$

giving

$$
F(s) = \frac{M}{s}\Big[\varphi(s\, t_A) - e^{-s t_B}\,\varphi\big(s(t_C - t_B)\big)\Big].
$$

Since $\varphi$ is entire and both terms equal $1$ at $s = 0$, the bracket vanishes there and cancels the $1/s$ — confirming that $F$ is **entire** (no poles, no branch points), as expected for a compactly supported history.

## Properties and sanity checks

$$
F(0) = \frac{M\,(t_B + t_C - t_A)}{2} \qquad \text{(area under the trapezoid)},
$$

$$
F(s) \sim \frac{M}{t_A\, s^2} \quad \text{as } |s| \to \infty,
$$

the $1/s^2$ decay reflecting $f(0) = 0$ but $f'(0^+) = M/t_A \neq 0$.

**Triangular limit** ($t_A = t_B$, hold vanishes):

$$
F(s) = \frac{M}{s}\Big[\varphi(s\, t_A) - e^{-s t_A}\,\varphi\big(s\,(t_C - t_A)\big)\Big].
$$

**Numerical evaluation near $s = 0$:** compute $\varphi$ stably as

$$
\varphi(z) = -\frac{\operatorname{expm1}(-z)}{z}
$$

to avoid catastrophic cancellation in $1 - e^{-z}$ for $|z| \ll 1$.

## Remarks on the method

1. **Analytic continuation.** The derivation used $\operatorname{Re} s > 0$ (where the individual ramp integrals converge), but the final assembled expression is entire, so it extends to all $s$ — which is why it can be evaluated anywhere on a complex inversion contour.

2. **Distributional shortcut.** Equivalently, differentiate $f$ twice in the distributional sense to get pure impulses,
$$
f''(t) = \sum_k \Delta_{\tau_k}\,\delta(t - \tau_k),
$$
transform using $\delta(t - \tau) \mapsto e^{-s\tau}$, and divide by $s^2$ via $\mathcal{L}\{f''\} = s^2 F(s) - s f(0) - f'(0^-)$ with zero initial terms. Same four coefficients, same result — the ramp decomposition is that argument made elementary.

3. **General ramp–soak schedules.** The formula generalizes verbatim to any continuous piecewise-linear program:
$$
F(s) = \frac{1}{s^2}\sum_k \Delta_{\tau_k}\, e^{-s\tau_k},
$$
entire whenever the schedule ends at the constant **zero** level ($\sum_k \Delta_{\tau_k} = 0$ and zero final value), and with a genuine simple pole $f_\infty/s$ at the origin if it ends at a nonzero soak level $f_\infty$.

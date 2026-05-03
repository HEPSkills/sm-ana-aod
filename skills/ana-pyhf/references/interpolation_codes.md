# Piecewise Linear Interpolation (Interpolation Codes)

Source: https://pyhf.readthedocs.io/en/v0.7.6/examples/notebooks/learn/InterpolationCodes.html

## Overview

Correlated modifiers (`normsys`, `histosys`) interpolate between nominal and ±1σ variations using an interpolating function. pyhf implements several **interpolation codes**; all are based on computing the delta (change from nominal).

## Interpolation Code 0: Piecewise Linear

The interpolated yield is:

```
η_s(α) = σ_sb⁰ + Σ_p I_lin(α_p; σ_sb⁰, σ_psb⁺, σ_psb⁻)
```

Where:
- α ≥ 0: `I_lin = α × (σ⁺ − σ⁰)`
- α < 0: `I_lin = α × (σ⁰ − σ⁻)`

```python
def interpolate_deltas(down, nom, up, alpha):
    delta_up   = up  - nom
    delta_down = nom - down
    return delta_up * alpha if alpha > 0 else delta_down * alpha
```

## Key Concepts

- All interpolation schemes share a common structure: compute deltas, then apply an interpolating function
- Code 0 is **piecewise linear** — slope changes at α = 0
- Higher codes (1, 2, 4, 5, 6) use polynomial/exponential smoothing for continuity at α = 0
- The same framework applies to single bins, multi-bin histograms, and batched (3D tensor) computations

## Applications

1. **Single bin**: interpolate total event count at arbitrary α
2. **Multi-bin**: bin-by-bin interpolation returning an array
3. **Batched (3D tensor)**: shape `(n_bins, n_alpha_points, ...)` for efficient vectorized evaluation

## How to Apply in Practice

pyhf chooses the interpolation code internally based on modifier type configuration. Users do not typically set the code manually — the JSON spec drives it. The interpolation code affects smoothness of the likelihood surface near α = 0.

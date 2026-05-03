# Tensorizing Interpolators

Source: https://pyhf.readthedocs.io/en/v0.7.6/examples/notebooks/learn/TensorizingInterpolations.html

## Overview

Tensorizing interpolations converts nested-loop interpolation into vectorized tensor operations, enabling GPU acceleration and ~100–340× speedups.

## The Problem (Naive Approach)

Nested loops over: histogram sets → alpha values → bins → apply interpolation per element. This is slow and not GPU-friendly.

## Linear Interpolation Tensorization

**Naive**:
```python
for alpha in alphaset:
    delta = alpha * (up - nom) if alpha > 0 else alpha * (nom - down)
    result = nom + delta
```

**Tensorized** (step-by-step):
1. Replace `if/else` with `np.where(alphaset > 0, delta_up, delta_down)`
2. Vectorize over bins with array broadcasting
3. Use `np.einsum('i,j->ij', alphaset, variations)` to compute all alpha×bin deltas at once
4. Final: pure tensor operations, no explicit loops

## Non-Linear (Exponential) Interpolation

```python
# Multiplicative ratio-based:
ratio_up   = up   / nom
ratio_down = down / nom
# Interpolated: nom * ratio^alpha
result = nom * np.where(alphaset > 0, ratio_up**alphaset, ratio_down**(-alphaset))
```

## Tensor Dimensions

```
(s, h, a, b)  — systematics × histograms × alpha values × bins
```

All interpolated yields across all variations are computed in a single operation.

## Performance

| Method | Time per run | Speedup |
|---|---|---|
| Naive linear | ~160 ms | 1× |
| Tensorized linear | ~0.47 ms | ~340× |
| Naive non-linear | ~150 ms | 1× |
| Tensorized non-linear | ~1.49 ms | ~100× |

## Key Pattern

```python
# Core: Einstein summation replaces alpha loop
alphas_times_deltas = np.einsum('i,j->ij', alphaset, variations)
# → shape (n_alphas, n_bins)
```

## Backend Note

The tensorized approach works identically with `pyhf.tensorlib` — swap `np` for `pyhf.tensorlib` to run on PyTorch/TensorFlow/JAX backends for GPU acceleration.

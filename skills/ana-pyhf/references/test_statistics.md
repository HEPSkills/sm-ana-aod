# Empirical Test Statistics

Source: https://pyhf.readthedocs.io/en/v0.7.6/examples/notebooks/learn/TestStatistics.html

## Overview

Demonstrates computing test statistics from pseudo-experiments to validate asymptotic approximations. Uses a single-bin model: signal=10, background=100, bkg_uncertainty=10%.

## Test Statistic Definitions

### Unbounded POI (μ ∈ [−10, 10])

| Statistic | Formula | Use |
|---|---|---|
| `t_μ` | `(μ − μ̂)² / σ²` | general deviation from test value |
| `q_μ` | `t_μ` if `μ̂ < μ`, else 0 | upper limits (one-sided) |

### Bounded POI (μ ≥ 0)

| Statistic | Formula | Use |
|---|---|---|
| `t̃_μ` | `t_μ` if `μ̂ ≥ 0`; `t_μ − t_0` otherwise | upper limits with physical boundary |
| `q̃_μ` | `t̃_μ` if `μ̂ < μ`, else 0 | standard CLs upper limits |
| `q_0` | `t_0` if `μ̂ ≥ 0`, else 0 | discovery (test μ=0) |

## Python API

```python
import pyhf

init_pars    = model.config.suggested_init()
par_bounds   = model.config.suggested_bounds()
fixed_params = model.config.suggested_fixed()

tmu       = pyhf.infer.test_statistics.tmu(
    test_poi, data, model, init_pars, par_bounds, fixed_params)
tmu_tilde = pyhf.infer.test_statistics.tmu_tilde(
    test_poi, data, model, init_pars, par_bounds, fixed_params)
qmu       = pyhf.infer.test_statistics.qmu(
    test_poi, data, model, init_pars, par_bounds, fixed_params)
qmu_tilde = pyhf.infer.test_statistics.qmu_tilde(
    test_poi, data, model, init_pars, par_bounds, fixed_params)
```

## When to Use Which

- `test_stat="qtilde"` (q̃_μ): standard upper limits with μ ≥ 0 constraint — default for exclusion
- `test_stat="q"` (q_μ): upper limits when μ can be negative (unbounded)
- `test_stat="q0"`: discovery test (how significant is μ > 0)
- Use `calctype="toybased"` to validate that empirical distributions match the asymptotic chi-squared approximation

## Validation Result

300 pseudo-experiments confirmed that toy-based test statistic distributions match the asymptotic chi-squared / half-chi-squared predictions for all four variants.

# Two-Bin Counting Experiment with Background Uncertainty

Source: https://pyhf.readthedocs.io/en/v0.7.6/examples/notebooks/hello-world.html

## Overview

The simplest pyhf model: two-bin channel with uncorrelated per-bin background uncertainties (one `shapesys` parameter per bin).

## Python Code

```python
import pyhf

model = pyhf.simplemodels.uncorrelated_background(
    signal=[12.0, 11.0],
    bkg=[50.0, 52.0],
    bkg_uncertainty=[3.0, 7.0],
)

data = [51, 48] + model.config.auxdata
test_mu = 1.0

# Basic CLs (observed + median expected)
CLs_obs, CLs_exp = pyhf.infer.hypotest(
    test_mu, data, model,
    test_stat="qtilde",
    return_expected=True,
)
# CLs_obs ≈ 0.0525,  CLs_exp (median) ≈ 0.0645

# Individual tail probabilities
CLs_obs, (p_sb, p_b) = pyhf.infer.hypotest(
    test_mu, data, model,
    test_stat="qtilde",
    return_tail_probs=True,
)
# p_sb (CL_{s+b}) ≈ 0.0233,  p_b (CL_b) ≈ 0.4442
# CLs = p_sb / p_b

# Full ±2σ expected band
CLs_obs, CLs_exp_band = pyhf.infer.hypotest(
    test_mu, data, model,
    test_stat="qtilde",
    return_expected_set=True,
)
# CLs_exp_band ≈ [0.0026, 0.0138, 0.0645, 0.2353, 0.5730]  (−2σ…+2σ)
```

## Key Points

- `pyhf.simplemodels.uncorrelated_background` builds a single-channel model with one `normfactor` (μ) and one Poisson-constrained `shapesys` per bin
- `model.config.auxdata` provides constraint term data — must be appended to observations
- `test_stat="qtilde"` is the standard one-sided test statistic for upper limits
- `return_expected=True` → single median expected CLs
- `return_expected_set=True` → list of 5 values: [−2σ, −1σ, median, +1σ, +2σ]
- `return_tail_probs=True` → `(p_{s+b}, p_b)` tuple; CLs = p_{s+b} / p_b

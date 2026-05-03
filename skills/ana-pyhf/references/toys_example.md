# Running Monte Carlo Simulations (Toys)

Source: https://pyhf.readthedocs.io/en/v0.7.6/examples/notebooks/toys.html

## Overview

Toy MC (pseudo-experiments) is an alternative to the asymptotic approximation (Cowan et al. arXiv:1007.1727). Use `calctype="toybased"` when low statistics or non-standard conditions make asymptotic formulas unreliable.

## Basic Model

```python
import pyhf
import numpy as np

model = pyhf.simplemodels.uncorrelated_background(
    signal=[6], bkg=[9], bkg_uncertainty=[3]
)
```

## Manual Toy Generation

```python
n_samples = 10_000

# PDFs at specific hypotheses
pars_bkg = model.config.suggested_init(); pars_bkg[model.config.poi_index] = 0.0
pars_sig = model.config.suggested_init(); pars_sig[model.config.poi_index] = 1.0

pdf_bkg = model.make_pdf(pyhf.tensorlib.astensor(pars_bkg))
pdf_sig = model.make_pdf(pyhf.tensorlib.astensor(pars_sig))

mc_bkg = pdf_bkg.sample((n_samples,))   # shape: (n_samples, n_aux+1)
mc_sig = pdf_sig.sample((n_samples,))

# Compute test statistic for each toy
init_pars   = model.config.suggested_init()
par_bounds  = model.config.suggested_bounds()
fixed_params = model.config.suggested_fixed()

qtilde_bkg = pyhf.tensorlib.astensor([
    pyhf.infer.test_statistics.qmu_tilde(1.0, mc, model, init_pars, par_bounds, fixed_params)
    for mc in mc_bkg
])
qtilde_sig = pyhf.tensorlib.astensor([
    pyhf.infer.test_statistics.qmu_tilde(1.0, mc, model, init_pars, par_bounds, fixed_params)
    for mc in mc_sig
])
```

## Calculator API (Recommended)

```python
# qtilde (q̃_μ) — μ ≥ 0
toy_calc_qtilde = pyhf.infer.utils.create_calculator(
    "toybased",
    model.expected_data(pars_sig),
    model,
    ntoys=n_samples,
    test_stat="qtilde",
)
dist_sig, dist_bkg = toy_calc_qtilde.distributions(1.0)
# dist_sig.samples — test stat values under s+b hypothesis
# dist_bkg.samples — test stat values under b-only hypothesis
# dist_*.p_value(obs_stat) — compute p-value

# q_μ — allows μ < 0 (need relaxed bounds)
qmu_bounds = model.config.suggested_bounds()
qmu_bounds[model.config.poi_index] = (-10, 10)

toy_calc_qmu = pyhf.infer.utils.create_calculator(
    "toybased",
    model.expected_data(model.config.suggested_init()),
    model,
    par_bounds=qmu_bounds,
    ntoys=n_samples,
    test_stat="q",
)
dist_sig_q, dist_bkg_q = toy_calc_qmu.distributions(1.0)
```

## High-level Interface with Toys

```python
CLs_obs, CLs_exp = pyhf.infer.hypotest(
    1.0, observations, model,
    test_stat="qtilde",
    return_expected_set=True,
    calctype="toybased",
    ntoys=5_000,
    track_progress=True,
)
```

## Key Points

- `calctype="toybased"` replaces the asymptotic formula with sampled distributions
- `ntoys=5000`–`10000` is typical; more toys = more accurate p-values
- `track_progress=True` shows a progress bar
- For `test_stat="q"` (two-sided), expand `poi_index` bounds to include negative μ
- `dist.samples` is a 1D tensor of test statistic values per toy
- `dist.p_value(q_obs)` returns the fraction of toys with stat ≥ q_obs
- Test statistics: `q` (two-sided), `qtilde` (one-sided, μ≥0), `q0` (discovery)

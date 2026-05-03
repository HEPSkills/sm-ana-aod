# Multi-bin Poisson Example

Source: https://pyhf.readthedocs.io/en/v0.7.6/examples/notebooks/multiBinPois.html

## Overview

Demonstrates multi-bin statistical modeling, fitting, upper limit calculation, and 2D mass-plane exclusion contours.

## Model Setup

```python
import pyhf
from pyhf.simplemodels import uncorrelated_background

source = {
    "binning": [2, -0.5, 1.5],
    "bindata": {
        "data":   [120.0, 145.0],
        "bkg":    [100.0, 150.0],
        "bkgerr": [15.0,  20.0],
        "sig":    [30.0,  45.0],
    },
}

model = uncorrelated_background(
    signal=source["bindata"]["sig"],
    bkg=source["bindata"]["bkg"],
    bkg_uncertainty=source["bindata"]["bkgerr"],
)
data = source["bindata"]["data"] + model.config.auxdata
```

## Fitting

```python
init_pars  = model.config.suggested_init()
par_bounds = model.config.suggested_bounds()

bestfit_pars = pyhf.infer.mle.fit(data, model, init_pars, par_bounds)
bestfit_cts  = model.expected_data(bestfit_pars, include_auxdata=False)
```

## Upper Limits

```python
import numpy as np
from pyhf.contrib.viz import brazil
import matplotlib.pyplot as plt

poi_values = np.linspace(0.1, 5, 50)
obs_limit, exp_limits, (poi_tests, tests) = pyhf.infer.intervals.upper_limits.upper_limit(
    data, model, poi_values, level=0.05, return_results=True
)
# obs_limit ≈ 2.38,  exp_limits ≈ [1.08, 1.42, 1.97, 2.73, 3.85]

fig, ax = plt.subplots()
brazil.plot_results(poi_tests, tests, test_size=0.05, ax=ax)
```

## 2D Mass Plane Scan

```python
def CLs(m1, m2):
    signal_counts = signal(m1, m2)   # user-defined signal model
    pdf = uncorrelated_background(signal_counts, bkg, bkgerr)
    cls_obs, cls_exp_set = pyhf.infer.hypotest(
        1.0, data, pdf, test_stat="qtilde", return_expected_set=True
    )
    return cls_obs, cls_exp_set, True

# Evaluate on a grid of 15×15 mass points (100–1000 GeV each axis)
# Then plot 2D contours at CLs = 0.05
```

## Key Points

- `model.expected_data(pars, include_auxdata=False)` returns only the main-channel bin counts
- Brazil band plot: 5 expected quantiles (−2σ…+2σ) plus observed
- 2D exclusion: scan CLs over a mass grid, then draw contour at CLs = 0.05
- 225 mass-point grid evaluated in the example

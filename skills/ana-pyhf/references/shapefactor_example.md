# ShapeFactor Example

Source: https://pyhf.readthedocs.io/en/v0.7.6/examples/notebooks/ShapeFactor.html

## Overview

`shapefactor` is a free (unconstrained), bin-wise multiplicative modifier used for data-driven background shape estimation. Multiple samples sharing the same `shapefactor` name are **coupled** — the same per-bin γ parameters scale all of them simultaneously across channels.

## JSON Workspace Structure

```json
{
  "channels": [
    {
      "name": "signal",
      "samples": [
        {
          "name": "signal",
          "data": [20.0, 20.0],
          "modifiers": [{"name": "mu", "type": "normfactor", "data": null}]
        },
        {
          "name": "bkg1",
          "data": [100.0, 70.0],
          "modifiers": [{"name": "coupled_shapefactor", "type": "shapefactor", "data": null}]
        }
      ]
    },
    {
      "name": "control",
      "samples": [
        {
          "name": "background",
          "data": [100.0, 100.0],
          "modifiers": [{"name": "coupled_shapefactor", "type": "shapefactor", "data": null}]
        }
      ]
    }
  ]
}
```

Both `bkg1` (signal channel) and `background` (control channel) share `"coupled_shapefactor"` — their shapes are tied by the same per-bin parameters.

## Python Code

```python
import pyhf, numpy as np
import matplotlib.pyplot as plt
from pyhf.contrib.viz import brazil

spec = {
    "channels": [
        {"name": "signal", "samples": [
            {"name": "signal",     "data": [20.0, 20.0],
             "modifiers": [{"name": "mu",                  "type": "normfactor",  "data": None}]},
            {"name": "bkg1",       "data": [100.0, 70.0],
             "modifiers": [{"name": "coupled_shapefactor", "type": "shapefactor", "data": None}]},
        ]},
        {"name": "control", "samples": [
            {"name": "background", "data": [100.0, 100.0],
             "modifiers": [{"name": "coupled_shapefactor", "type": "shapefactor", "data": None}]},
        ]},
    ]
}

pdf  = pyhf.Model(spec)
data = [200.0, 300.0, 220.0, 230.0]   # control then signal channel bins

# Unconditional MLE fit — 3 parameters: [mu, gamma_bin0, gamma_bin1]
unconpars = pyhf.infer.mle.fit(data, pdf)
# Result ≈ [1.0, 2.0, 3.0]

# Upper limit (Brazil band)
poi_values = np.linspace(0, 5, 61)
obs_limit, exp_limits, (poi_tests, tests) = pyhf.infer.intervals.upper_limits.upper_limit(
    data, pdf, poi_values, level=0.05, return_results=True
)
# obs_limit ≈ 2.195
# exp_limits ≈ [0.741, 0.995, 1.385, 1.929, 2.594]  (−2σ, −1σ, median, +1σ, +2σ)

fig, ax = plt.subplots(figsize=(10, 7))
brazil.plot_results(poi_tests, tests, test_size=0.05, ax=ax)
```

## Key Points

- `shapefactor` has `data: null` — no up/down templates needed
- Parameter count = number of bins in the channel(s) that share the name
- Coupling across channels: the same γ_b multiplies corresponding bins in all channels that reference this modifier
- `pdf.config.suggested_init()` returns `[1.0, 1.0, 1.0]` (one per parameter)

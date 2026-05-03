# Multibin Coupled HistoSys Example

Source: https://pyhf.readthedocs.io/en/v0.7.6/examples/notebooks/multichannel-coupled-histo.html

## Overview

Two-channel model where background samples across both channels share a coupled `histosys` modifier — a single α parameter controls correlated shape variation in both channels simultaneously.

## Model Structure

- **signal channel**: signal sample (`normfactor` μ) + bkg1 + bkg2 (both with `coupled_histo` histosys)
- **control channel**: single background with the same `coupled_histo` histosys

The `coupled_histo` modifier shares `lo_data`/`hi_data` templates across all samples that reference it by name.

## JSON Workspace Pattern

```json
{
  "channels": [
    {
      "name": "signal",
      "samples": [
        {"name": "signal", "data": [...],
         "modifiers": [{"name": "mu", "type": "normfactor", "data": null}]},
        {"name": "bkg1",   "data": [...],
         "modifiers": [{"name": "coupled_histo", "type": "histosys",
                         "data": {"lo_data": [...], "hi_data": [...]}}]},
        {"name": "bkg2",   "data": [...],
         "modifiers": [{"name": "coupled_histo", "type": "histosys",
                         "data": {"lo_data": [...], "hi_data": [...]}}]}
      ]
    },
    {
      "name": "control",
      "samples": [
        {"name": "background", "data": [...],
         "modifiers": [{"name": "coupled_histo", "type": "histosys",
                         "data": {"lo_data": [...], "hi_data": [...]}}]}
      ]
    }
  ]
}
```

## Python Code

```python
import json, pyhf
import numpy as np
from pyhf.contrib.viz import brazil
import matplotlib.pyplot as plt

spec = json.load(open("2bin_2channel_coupledhisto.json"))
pdf  = pyhf.Model(spec)

data = ws_data + pdf.config.auxdata   # observed + auxiliary

init_pars  = pdf.config.suggested_init()
par_bounds = pdf.config.suggested_bounds()

# Unconstrained MLE
unconpars = pyhf.infer.mle.fit(data, pdf, init_pars, par_bounds)
# Result ≈ [-0.303, 0.636]   (alpha_histo, mu)

# Background-only fit (POI fixed to 0)
conpars = pyhf.infer.mle.fixed_poi_fit(0.0, data, pdf, init_pars, par_bounds)
# Result ≈ [0.291, 0.0]

# CLs scan over 61 POI values
poi_values = np.linspace(0, 5, 61)
obs_limit, exp_limits, (poi_tests, tests) = pyhf.infer.intervals.upper_limits.upper_limit(
    data, pdf, poi_values, level=0.05, return_results=True
)
# obs_limit ≈ 1.545
# exp_limits ≈ [0.338, ..., 1.945]  (−2σ…+2σ)

fig, ax = plt.subplots()
brazil.plot_results(poi_tests, tests, test_size=0.05, ax=ax)
```

## Key Points

- `histosys` uses **absolute** `lo_data`/`hi_data` bin arrays (not relative to nominal)
- Coupling is by name: same modifier name → same α parameter across all samples/channels
- `fixed_poi_fit(poi_val, ...)` profiles over all nuisance parameters with POI fixed
- Unconstrained α < 0 means data prefers the "low" template shape

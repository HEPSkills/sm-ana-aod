---
name: ana-pyhf
description: Statistical analysis with pyhf — HistFactory-based likelihood models, hypothesis testing, CLs upper limits, pull plots, toy MC, workspace serialization/patching, and combinations for HEP analyses.
---

# pyhf Statistical Analysis

## Introduction

`pyhf` is a pure-Python implementation of the HistFactory statistical framework used in HEP analyses. It encodes the likelihood as:

> p(n, a | θ) = ∏ Poisson(main channel bins) × ∏ Poisson(auxiliary constraint terms)

where θ = (μ, χ) combines the parameter of interest (signal strength μ) and nuisance parameters χ constrained by auxiliary data.

Key design goals:
- Declarative JSON-based model format (replaces ROOT/XML, schema-validated via JSON Schema draft-06)
- Backend-agnostic tensor math: supports numpy, pytorch, tensorflow, jax
- Long-term preservation and reinterpretation via HEPData / INSPIRE

Core objects:

| Object | Role |
|---|---|
| `pyhf.pdf.Model` | Likelihood function; holds parameter config and PDF evaluation |
| `pyhf.Workspace` | Container for the full JSON HistFactory spec (channels, samples, modifiers, measurements) |
| `pyhf.PatchSet` | Collection of signal patches to overlay on a background-only workspace |

Key parameter accessors on `model.config`:

| Accessor | Returns |
|---|---|
| `parameters` | list of all parameter names |
| `par_order` | internal ordering used by the tensor |
| `poi_index` | index of the parameter of interest |
| `par_slice(k)` | slice into the parameter vector for parameter `k` |
| `param_set(k).constrained` | whether `k` is constrained by auxiliary data |
| `param_set(k).width()` | constraint width (used for pull normalisation) |
| `suggested_init()` | default starting values |
| `suggested_bounds()` | parameter bounds |
| `auxdata` | auxiliary data values encoding the constraint terms |

Backends and optimisers are set globally:

```python
pyhf.set_backend("numpy", "scipy")   # default
pyhf.set_backend("numpy", "minuit")  # required for return_uncertainties=True
```

---

## Likelihood Specification (JSON HistFactory)

A **workspace** JSON contains three top-level keys:

### channels

Each channel is an analysis region with named samples. Each sample has:
- `data`: array of nominal event rates per bin
- `modifiers`: list of `{name, type, data}` modifier objects

### measurements

Defines the POI and per-parameter config (`inits`, `bounds`, `fixed`, `auxdata`, `sigmas`).

### observations

Observed bin counts per channel (auxiliary data is derived automatically).

### Modifier Types

| Type | Key | Description | Constraint | Data |
|---|---|---|---|---|
| `normfactor` | unconstrained normalisation | free multiplicative μ per sample (common POI) | none | `null` |
| `normsys` | normalisation uncertainty | interpolates between `hi`/`lo` scale factors, κ(0)=1 | Gaussian | `{hi, lo}` floats |
| `histosys` | correlated shape | interpolates between `hi_data`/`lo_data` absolute bin arrays | Gaussian | `{hi_data, lo_data}` |
| `shapesys` | uncorrelated shape | bin-wise γ from relative uncertainties; bins with zero nominal/uncertainty fixed to 1 | Poisson | array of absolute uncertainties |
| `staterror` | MC stat uncertainty | bin-wise γ_cb, σ_cb = √(Σδ²)/Σν⁰ from MC sample yields | Gaussian | array of absolute uncertainties |
| `lumi` | luminosity | global scale from lumi uncertainty in measurement config | Gaussian | `null` |
| `shapefactor` | data-driven shape | free bin-wise multiplicative parameters (e.g. multijet) | none | `null` |

**Parameter sharing**: modifiers with the same `name` share the same parameter set — enabling correlated shape+norm variation from a single parameter.

### Interpolation

Correlated modifiers (`normsys`, `histosys`) use interpolating functions evaluated at α = ±1 (up/down variations). Several interpolation codes exist (see `references/interpolation_codes.md`).

---

## Common Use and Applications

### 1. Basic Model and Hypothesis Test

```python
import pyhf, numpy as np

model = pyhf.simplemodels.uncorrelated_background(
    signal=[5.0, 10.0],
    bkg=[50.0, 60.0],
    bkg_uncertainty=[5.0, 12.0],
)

observations = [53.0, 65.0] + model.config.auxdata

bestfit_pars = pyhf.infer.mle.fit(data=observations, pdf=model)

CLs_obs, CLs_exp = pyhf.infer.hypotest(
    1.0, observations, model,
    test_stat="qtilde",
    return_expected_set=True,
)
```

### 2. Workspace (JSON HistFactory)

```python
import json, pyhf

with open("2-bin_1-channel.json") as f:
    spec = json.load(f)

ws    = pyhf.Workspace(spec)
model = ws.model()
data  = ws.data(model)
data_noaux = ws.data(model, include_auxdata=False)

ws.get_measurement()
ws.get_measurement(measurement_name="Measurement")
ws.get_measurement(measurement_index=0)
```

### 3. Serialization and Patching

```python
import json, pyhf

pyhf.contrib.utils.download(
    "https://doi.org/10.17182/hepdata.90607.v3/r3",
    "1Lbb-likelihoods",
)

spec     = json.load(open("1Lbb-likelihoods/BkgOnly.json"))
patchset = pyhf.PatchSet(json.load(open("1Lbb-likelihoods/patchset.json")))

pyhf.utils.digest(spec)
patchset.verify(spec)

patch = patchset["C1N2_Wh_hbb_900_250"]   # by name
patch = patchset[(900, 250)]               # by parameter coordinates

ws = pyhf.Workspace(patch.apply(spec))                     # method 1
ws = pyhf.Workspace(patchset.apply(spec, (900, 250)))      # method 2
model = pyhf.Workspace(spec).model(patches=[patch])        # method 3

patchset.labels      # parameter-space axes, e.g. ["m1", "m2"]
patchset.patches
patchset.references
```

### 4. Pull Plots

`minuit` is required to obtain per-parameter uncertainties.

```python
pyhf.set_backend("numpy", "minuit")

result = pyhf.infer.mle.fit(data, model, return_uncertainties=True)
bestfit, errors = result.T

pulls = pyhf.tensorlib.concatenate([
    (bestfit[model.config.par_slice(k)] - model.config.param_set(k).suggested_init)
    / model.config.param_set(k).width()
    for k in model.config.par_order
    if model.config.param_set(k).constrained
])
```

For background-only fits pass `poi_name=None` to `ws.model()`.

### 5. Toy MC

Use `calctype="toybased"` when asymptotic approximations fail (low-statistics regions).

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

Default is `calctype="asymptotics"`.

### 6. Workspace Combinations

Channel and modifier names must be unique before combining.

```python
other_ws = ws.rename(
    channels={"singlechannel": "othersinglechannel"},
    modifiers={"uncorr_bkguncrt": "otheruncorr_bkguncrt"},
    measurements={"Measurement": "OtherMeasurement"},
)

combined       = pyhf.Workspace.combine(ws, other_ws)
combined_model = combined.model()
combined_data  = combined.data(combined_model)

pyhf.infer.hypotest(1.0, combined_data, combined_model, test_stat="qtilde")
```

### 7. Upper Limits and Model-Independent Tables

```python
import numpy as np, scipy.stats, pyhf

pyhf.set_backend("numpy", "minuit")

poi_values = np.linspace(0.1, 5, 50)
obs_limit, exp_limits, results = pyhf.infer.intervals.upper_limits.upper_limit(
    observations, model, poi_values, level=0.05, return_results=True
)

pars_bonly, corr_bonly = pyhf.infer.mle.fixed_poi_fit(
    0.0, data, model,
    return_uncertainties=True,
    return_correlations=True,
)
bestfit_b, uncrt_b = pars_bonly.T

npars       = len(bestfit_b)
model_batch = ws.model(batch_size=npars)
pars_batch  = np.tile(bestfit_b, (npars, 1))

up_yields = model_batch.expected_actualdata(pars_batch + np.diag(uncrt_b))
dn_yields = model_batch.expected_actualdata(pars_batch - np.diag(uncrt_b))
variations = (up_yields - dn_yields) / 2
error_sq   = np.einsum("il,ik,kl->l", variations, corr_bonly, variations)

_, (_, CLb) = pyhf.infer.hypotest(obs_limit, data, model, return_tail_probs=True)
p0   = pyhf.infer.hypotest(0.0, data, model, test_stat="q0")
p0_Z = scipy.stats.norm.isf(p0)
```

Visible cross-section: `obs_limit / luminosity_ifb` [fb].

---

## References

- `references/pyhf_api.json` — full Python API quick-reference
- `references/shapefactor_example.md` — ShapeFactor example notebook
- `references/hello_world_example.md` — Two-bin counting experiment example
- `references/multibin_pois_example.md` — Multi-bin Poisson example
- `references/multichannel_histo_example.md` — Multibin Coupled HistoSys example
- `references/toys_example.md` — Running Monte Carlo simulations (toys)
- `references/interpolation_codes.md` — Piecewise Linear Interpolation
- `references/tensorizing_interpolations.md` — Tensorizing Interpolators
- `references/test_statistics.md` — Empirical Test Statistics
- `references/using_calculators.md` — Using Calculators
- `references/statistical_analysis.md` — Binned HEP Statistical Analysis in Python

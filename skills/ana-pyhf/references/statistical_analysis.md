# Binned HEP Statistical Analysis in Python

Source: https://pyhf.readthedocs.io/en/v0.7.6/examples/notebooks/binderexample/StatisticalAnalysis.html

## Overview

End-to-end pyhf workflow covering model import, exploration, fitting, upper limits, and visualization. Demonstrates reading XML+ROOT HistFactory workspaces with `pyhf.readxml`.

## Workflow Steps

### 1. Import from XML/ROOT

```python
import pyhf.readxml

# Convert legacy XML+ROOT HistFactory to pyhf JSON
spec = pyhf.readxml.parse("config/example.xml", "path/to/root/files/")
ws = pyhf.Workspace(spec)
```

### 2. Model Exploration

```python
model = ws.model()
data  = ws.data(model)

print(model.config.channels)         # list of channel names
print(model.config.samples)          # list of sample names
print(model.config.parameters)       # all parameter names
print(model.config.par_order)        # parameter ordering
print(model.config.suggested_init()) # initial values
```

### 3. Fitting

```python
import pyhf

pyhf.set_backend("numpy", "minuit")

bestfit, errors = pyhf.infer.mle.fit(
    data, model, return_uncertainties=True
).T
```

### 4. Upper Limits

```python
import numpy as np
from pyhf.contrib.viz import brazil
import matplotlib.pyplot as plt

poi_values = np.linspace(0.1, 5, 50)
obs_limit, exp_limits, (poi_tests, tests) = pyhf.infer.intervals.upper_limits.upper_limit(
    data, model, poi_values, level=0.05, return_results=True
)

fig, ax = plt.subplots(figsize=(10, 7))
brazil.plot_results(poi_tests, tests, test_size=0.05, ax=ax)
ax.set_xlabel(r"$\mu$")
ax.set_ylabel(r"$\mathrm{CL}_s$")
```

### 5. Discovery (p0)

```python
p0 = pyhf.infer.hypotest(0.0, data, model, test_stat="q0")
import scipy.stats
Z = scipy.stats.norm.isf(p0)
print(f"p0 = {p0:.4f},  Z = {Z:.2f} sigma")
```

## Key Points

- `pyhf.readxml` converts legacy ROOT/XML workspaces to JSON without ROOT dependency
- Containerized workflows (yadage) support reproducible analysis pipelines
- `pyhf.contrib.viz.brazil.plot_results` generates publication-quality Brazil band plots
- Full pipeline: XML → JSON workspace → model → fit → limits → plot

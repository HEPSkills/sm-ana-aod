# How to Collect Results — Accumulators (Coffea)

Source: https://coffea-hep.readthedocs.io/en/latest/user_guide/accumulators.html

## Modern Approach: Plain Dictionaries

Modern coffea (2023+) uses plain Python dicts returned from `process()`. No need for `_accumulator`, `@property accumulator`, or `.identity()` methods. The framework automatically merges dicts and histogram objects across chunks.

- **Virtual/Eager modes**: nest results under the dataset name
- **Dask mode**: return flat dictionaries

---

## Histogram Creation and Filling

Use the `hist` library directly:

```python
import hist

# Standard (eager) mode
h = hist.Hist(
    hist.axis.StrCategory([], name="region", growth=True),
    hist.axis.Regular(100, 50, 150, name="mass", label="m [GeV]"),
)
h.fill(region="signal", mass=dimuon_mass, weight=events.genWeight)

# Dask mode
import hist.dask
h = hist.dask.Hist(...)
```

Axes with `growth=True` grow dynamically. The `hist` library handles awkward arrays directly — no numpy conversion needed.

---

## Tracking Multiple Results

```python
def process(self, events):
    output = {
        "h_mass": hist.Hist(...),
        "h_pt": hist.Hist(...),
        "n_events": ak.sum(ak.ones_like(events.event)),
        "sumw": float(ak.sum(events.genWeight)),
        "cutflow": {"all": len(events), "selected": 0},
    }
    # fill histograms ...
    return output
```

All types merge automatically across chunks.

---

## Weights Class

Track multiple weight sources:

```python
from coffea.analysis_tools import Weights

weights = Weights(len(events))
weights.add("genWeight", events.genWeight)
weights.add("puWeight", pu_weight)
weights.add("muonSF", muon_sf, muon_sf_up, muon_sf_dn)

total_weight = weights.weight()          # central value
varied_weight = weights.weight("muonSF")  # with variation
```

---

## Postprocessing

```python
def postprocess(self, accumulator):
    # runs after all chunks merge
    # compute derived quantities, averages, ratios
    pass
```

---

## Specialized Accumulator Classes

For legacy or specific merging behaviors:

| Class | Merging Behavior | Typical Use |
|---|---|---|
| `column_accumulator` | Concatenates arrays | Collect selected event IDs |
| `list_accumulator` | Appends lists | Metadata about interesting events |
| `set_accumulator` | Union of sets | Unique run numbers |
| `defaultdict_accumulator` | Auto-init counter | Cutflow counts |
| `value_accumulator` | Custom type + init | Arbitrary float sums |

```python
from coffea.processor import column_accumulator, set_accumulator, defaultdict_accumulator

# Concatenate arrays
col = column_accumulator(ak.to_numpy(selected_pts))

# Unique run numbers
runs = set_accumulator(set(ak.to_numpy(events.run)))

# Cutflow
cutflow = defaultdict_accumulator(int)
cutflow["all"] += len(events)
cutflow["selected"] += ak.sum(mask)
```

---

## Serialization

```python
from coffea.util import save, load

save(result, "out.coffea")
result = load("out.coffea")
```

Both histograms and dicts are picklable.

---

## Best Practices

- Always return the complete dict structure even when chunks are empty
- Test with `IterativeExecutor` first to validate output
- For large arrays exceeding 100 MB, write directly to disk rather than using `column_accumulator`

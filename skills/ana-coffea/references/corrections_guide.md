# How to Apply Corrections (Coffea)

Source: https://coffea-hep.readthedocs.io/en/latest/user_guide/corrections.html

## Core Integration with correctionlib

Coffea integrates with `correctionlib` for applying scale factors and systematic variations. Load corrections in `__init__` — coffea knows how to serialize/distribute the correction set with the Processor onto a cluster:

```python
import correctionlib

class MyProcessor(processor.ProcessorABC):
    def __init__(self):
        self._corrections = correctionlib.CorrectionSet.from_file("corrections.json.gz")

    def process(self, events):
        # evaluate scale factor: output shape matches input shape
        sf = self._corrections["muon_ID"].evaluate(
            events.metadata["year"],
            ak.flatten(abs(events.Muon.eta)),
            ak.flatten(events.Muon.pt),
            "sf",         # variation label: "sf", "systup", "systdown"
        )
        sf_up = self._corrections["muon_ID"].evaluate(..., "systup")
        sf_dn = self._corrections["muon_ID"].evaluate(..., "systdown")
```

---

## Per-Object Scale Factors

- Pass object kinematics (eta, pt) as awkward arrays; output matches input shape
- Variation labels: `"nominal"`, `"syst_up"`, `"syst_down"` (correction-specific)
- Cache helper arrays (e.g., `abs_eta = abs(events.Muon.eta)`) to avoid redundant calculation

---

## Handling Systematics

Store alternative weight variations in output dict to build envelopes for downstream steps:

```python
output = {
    "h_mass_nominal": hist.Hist(...),
    "h_mass_muon_sf_up": hist.Hist(...),
    "h_mass_muon_sf_dn": hist.Hist(...),
}
output["h_mass_nominal"].fill(mass=mass, weight=nominal_weight)
output["h_mass_muon_sf_up"].fill(mass=mass, weight=sf_up_weight)
```

Return systematic variations so they merge correctly across chunks.

---

## Multiple Corrections

When applying multiple corrections: multiply per-object corrections before reducing across the event dimension:

```python
# per-muon SF → product over muons in event
event_sf = ak.prod(per_muon_sf, axis=1)
total_weight = event_sf * pu_weight * xsec_weight
```

---

## Global Factors

Cross-section, luminosity, and generator weights are applied separately. Store in fileset metadata for consistent bookkeeping:

```python
xsec = events.metadata.get("xsec", 1.0)
lumi = events.metadata.get("lumi", 1.0)
genw = events.genWeight
global_weight = xsec * lumi * genw / sumw
```

---

## Using the Weights Class

```python
from coffea.analysis_tools import Weights

weights = Weights(len(events))
weights.add("genWeight", events.genWeight)
weights.add("puWeight", pu_weight)
weights.add("muonSF", muon_sf, muon_sf_up, muon_sf_dn)

nominal = weights.weight()              # combined central weight
varied  = weights.weight("muonSF")     # with muonSF variation
```

---

## Best Practices

- Load corrections once in `__init__`, not in `process()`
- Document correction file versions in metadata for reproducibility
- Use the `Weights` class for complex multi-correction scenarios
- Store systematic variations in output dict for downstream envelope building

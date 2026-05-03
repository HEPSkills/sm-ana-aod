# How to Work with NanoEvents (Coffea)

Source: https://coffea-hep.readthedocs.io/en/latest/user_guide/nanoevents.html

## Loading Events

```python
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema

events = NanoEventsFactory.from_root(
    {"nano_dy.root": "Events"},
    schemaclass=NanoAODSchema,
    entry_stop=10_000,  # limit for testing
).events()
```

Accepts ROOT or Parquet files and converts them into Pythonic objects with Awkward Array behaviors.

---

## Supported Schemas

| Schema | Format |
|---|---|
| `NanoAODSchema` | Standard CMS NanoAOD |
| `PFNanoAODSchema` | PF NanoAOD |
| `BaseSchema` | Generic flat/jagged ROOT |
| `PHYSLITESchema` | ATLAS PHYSLITE |
| `DelphesSchema` | Delphes fast simulation |

---

## Exploring Structure

```python
events.fields                  # top-level collections
events.Muon.fields             # attributes within a collection
events.Muon.pt.type            # Awkward Array type signature
```

---

## Columnar Selection

Selections are lazy until materialized. Boolean masks combine vectorized operations:

```python
tight_muons = events.Muon[
    (events.Muon.tightId)
    & (events.Muon.pt > 25)
    & (abs(events.Muon.eta) < 2.4)
]
```

Awkward structure preserves variable per-event lengths.

---

## Vector Behaviors & Lorentz Vectors

NanoAODSchema automatically associates physics vector operations:

```python
dimuon = lead + trail        # 4-vector addition
mass = dimuon.mass           # invariant mass computed automatically
pt   = dimuon.pt
eta  = dimuon.eta
phi  = dimuon.phi
```

Available behaviors from `vector` library: `.mass`, `.pt`, `.eta`, `.phi`, `.deltaR()`, `.nearest()`.

---

## Cross-References

NanoAOD cross-reference fields (e.g., `Jet.genJetIdx`) are resolved automatically:

```python
gen_jets = events.Jet.matched_gen   # follows cross-reference
```

---

## Metadata Access in Processors

```python
def process(self, events):
    dataset = events.metadata["dataset"]
    year    = events.metadata.get("year")
    is_mc   = events.metadata.get("is_mc", False)
```

---

## Data Conversion

```python
import awkward as ak

flat_mass = ak.to_numpy(ak.flatten(mass, axis=None))
df = ak.to_dataframe({"mass": mass, "pt": pt})
```

---

## Performance Guidelines

- Maintain vectorized operations — avoid explicit Python loops over events
- If iteration unavoidable: wrap hot sections with `@numba.njit` to compile while preserving parallelism
- Use `entry_stop=N` in `NanoEventsFactory.from_root()` to limit event counts during development

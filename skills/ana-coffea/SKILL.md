---
name: ana-coffea
description: Columnar HEP analysis with coffea — NanoEvents, ProcessorABC, accumulators, PackedSelection, Weights, corrections via correctionlib/lookup_tools/btag_tools/jetmet_tools, scaling with distributed executors (Dask, Parsl, TaskVine), dataset discovery via Rucio, ML inference integration, and full API reference for particle physics analyses.
---

# Coffea Analysis Framework

## What is Coffea?

Coffea is a columnar analysis framework that merges Awkward Array's data model with a lightweight execution layer, enabling HEP analyses to scale from personal computers to distributed clusters without code modifications.

Key design goals:
- **Columnar paradigm**: operates on columns spanning chunks of rows using array programming primitives (NumPy + Awkward Array)
- **No code rewriting**: the same processor works locally and on all cluster backends
- **Backend-agnostic execution**: swap executor from `IterativeExecutor` → `DaskExecutor` with one argument change
- **Built-in metrics**: captures runtime data including bytes read and columns accessed

---

## Core Workflow

Three-step pattern for all coffea analyses:

1. **Implement Processor**: create a `coffea.processor.ProcessorABC` subclass with `process()` and `postprocess()` methods
2. **Test Locally**: use `coffea.processor.Runner` with `IterativeExecutor` or `FuturesExecutor`
3. **Scale Out**: swap executor to `DaskExecutor`, `ParslExecutor`, or `TaskVineExecutor` — no processor changes needed

```python
from coffea import processor
from coffea.nanoevents import NanoAODSchema

class MyProcessor(processor.ProcessorABC):
    def process(self, events):
        return {"cutflow": {"all": len(events)}}

    def postprocess(self, accumulator):
        pass

runner = processor.Runner(
    executor=processor.IterativeExecutor(),
    schema=NanoAODSchema,
)
result = runner(fileset, "Events", processor_instance=MyProcessor())
```

---

## Datasets (Fileset Format)

Three supported fileset patterns — see `references/datasets_guide.md` for full details:

```python
# Format 1 (recommended): explicit file-to-tree mapping
fileset = {
    "DYJets": {
        "files": {
            "/store/mc/.../nano_dy.root": "Events",
            "/store/mc/.../nano_dy_2.root": "Events",
        },
        "metadata": {"year": 2018, "is_mc": True, "xsec": 6225.4},
    },
}

# Format 2: uniform tree name per dataset
fileset = {
    "DYJets": {
        "treename": "Events",
        "files": ["/store/mc/.../nano_dy.root"],
        "metadata": {"year": 2018},
    },
}

# Format 3: global tree name via Runner argument
result = runner(fileset, "Events", processor_instance=my_processor)
```

- Top-level keys → dataset identifiers accessible via `events.metadata['dataset']`
- XRootD URLs supported: `root://cmsxrootd.fnal.gov//store/mc/...`
- Serialize to JSON for version-controlled reproducibility
- Rucio discovery: `coffea.dataset_tools.rucio_utils.get_dataset_files_replicas()`
- Limit for testing: `NanoEventsFactory.from_root(..., entry_stop=N)` or `maxchunks=N` in Runner

---

## NanoEvents

NanoEvents wraps flat nTuple structures (ROOT TTree / Parquet) into Pythonic Awkward Array objects with physics behaviors, cross-references, and lazy loading.

```python
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema

events = NanoEventsFactory.from_root(
    {"nano_dy.root": "Events"},
    schemaclass=NanoAODSchema,
    metadata={"dataset": "DYJets"},
    entry_stop=10_000,
).events()

# Explore structure
events.fields                    # top-level collections
events.Muon.fields               # collection attributes
events.Muon.pt.type              # Awkward type signature

# Columnar selection (lazy until materialized)
tight_muons = events.Muon[
    (events.Muon.tightId)
    & (events.Muon.pt > 25)
    & (abs(events.Muon.eta) < 2.4)
]

# Lorentz vector operations (via vector behaviors)
dimuon = lead + trail
mass = dimuon.mass               # invariant mass
pt   = dimuon.pt
```

Available schemas:

| Schema | Format |
|---|---|
| `NanoAODSchema` | Standard CMS NanoAOD |
| `PFNanoAODSchema` | PF NanoAOD (double-jagged PF candidates) |
| `BaseSchema` | Generic flat/jagged ROOT (verbatim branches) |
| `TreeMakerSchema` | CMS TreeMaker format |
| `PHYSLITESchema` | ATLAS DAOD_PHYSLITE |
| `DelphesSchema` | Delphes fast simulation |

NanoAODSchema auto-resolves cross-references (e.g. `events.Jet.matched_gen`). See `references/nanoevents_guide.md` and `references/example_nanoevents.md` for full details.

---

## Accumulators

Modern coffea (2023+) uses plain Python dicts + `hist.Hist` objects — no special accumulator wrapper classes needed. The framework merges automatically across chunks.

```python
import hist

def process(self, events):
    h = hist.Hist(
        hist.axis.StrCategory([], name="region", growth=True),
        hist.axis.Regular(100, 50, 150, name="mass", label="m_{ll} [GeV]"),
    )
    h.fill(region="signal", mass=dimuon_mass, weight=total_weight)
    return {
        "h_mass": h,
        "n_events": len(events),
        "sumw": float(ak.sum(events.genWeight)),
        "cutflow": {"all": len(events), "selected": int(ak.sum(mask))},
    }
```

- `hist.dask.Hist` for Dask mode
- Serialize: `coffea.util.save(result, "out.coffea")` / `coffea.util.load("out.coffea")`
- Avoid returning large arrays (>100 MB) in accumulators — write to disk instead

Specialized accumulator classes (legacy/specific merging):

| Class | Behavior |
|---|---|
| `column_accumulator` | Concatenates arrays |
| `list_accumulator` | Appends lists |
| `set_accumulator` | Union of sets |
| `defaultdict_accumulator` | Auto-init counters |
| `value_accumulator` | Custom type + init |

See `references/accumulators_guide.md` for full patterns.

---

## Analysis Tools (`coffea.analysis_tools`)

### PackedSelection

Memory- and CPU-efficient storage of multiple boolean masks with arbitrary combination:

```python
from coffea.analysis_tools import PackedSelection

sel = PackedSelection()
sel.add("tightMuon",   (events.Muon.pt > 25) & (abs(events.Muon.eta) < 2.4))
sel.add("dimuon",      ak.num(events.Muon) >= 2)
sel.add("oppSign",     ak.sum(events.Muon.charge, axis=1) == 0)

mask = sel.all("tightMuon", "dimuon", "oppSign")    # AND of named cuts
any_mask = sel.any("tightMuon", "dimuon")            # OR

# Cutflow and N-1 plots built-in
cutflow = sel.cutflow("tightMuon", "dimuon", "oppSign")
```

See `references/example_packedselection.md` for full cutflow / N-1 examples.

### Weights

Container for event weights and systematic variations:

```python
from coffea.analysis_tools import Weights

weights = Weights(len(events))
weights.add("genWeight", events.genWeight)
weights.add("puWeight",  pu_weight)
weights.add("muonSF",    muon_sf, muon_sf_up, muon_sf_dn)  # central + up/down

total        = weights.weight()            # combined central weight
with_muonSF  = weights.weight("muonSF")   # weight with muonSF variation
```

Also: `NminusOne`, `Cutflow` classes in `coffea.analysis_tools`.

See `references/example_analysis_tools.md` for full `Weights` + cutflow demo.

---

## Corrections

### correctionlib (preferred)

Load once in `__init__`, coffea distributes it with the Processor:

```python
import correctionlib

class MyProcessor(processor.ProcessorABC):
    def __init__(self):
        self._corr = correctionlib.CorrectionSet.from_file("corrections.json.gz")

    def process(self, events):
        sf    = self._corr["muon_ID"].evaluate(year, abs_eta, pt, "sf")
        sf_up = self._corr["muon_ID"].evaluate(year, abs_eta, pt, "systup")
        sf_dn = self._corr["muon_ID"].evaluate(year, abs_eta, pt, "systdown")
```

### coffea.jetmet_tools (JEC/JER)

CMS jet energy corrections and resolution smearing. Available until full transition to correctionlib.

### coffea.btag_tools

```python
from coffea.btag_tools import BTagScaleFactor

btag_sf = BTagScaleFactor("DeepCSV_102XSF_V1.btag.csv.gz", BTagScaleFactor.RESHAPE)
sf = btag_sf.eval("central", events.Jet.hadronFlavour,
                  abs(events.Jet.eta), events.Jet.pt)
```

### coffea.lookup_tools (legacy)

Read ROOT TH1/TH2/TGraph correction files into evaluator objects.

### Object Systematics

```python
# UpDownSystematic: varies one field
# UpDownMultiSystematic: varies multiple fields simultaneously
```

See `references/corrections_guide.md` and `references/example_corrections.md` for full patterns.
See `references/example_systematics.md` for object-level systematic variations.

---

## Executors

All executors share the same `Runner` interface — only the `executor=` argument changes:

| Executor | Use Case |
|---|---|
| `IterativeExecutor()` | Sequential debugging (default) |
| `FuturesExecutor(workers=N)` | Multi-core on one machine |
| `DaskExecutor(client=client)` | Dask Distributed cluster |
| `ParslExecutor(config=cfg)` | HPC / batch (Parsl) |
| `TaskVineExecutor(port=N)` | Opportunistic workers (TaskVine) |

```python
# Dask cluster example
from dask.distributed import Client
client = Client("tcp://scheduler:8786")

runner = processor.Runner(
    executor=processor.DaskExecutor(client=client),
    schema=NanoAODSchema,
    savemetrics=True,       # collect bytes read, columns touched
    chunksize=100_000,      # events per chunk
    maxchunks=10,           # limit for testing
)
result, metrics = runner(fileset, "Events", processor_instance=MyProcessor())
```

Use `processor.SimpleCheckpointer` for job persistence across restarts.

See `references/executors_guide.md` and `references/example_processing.md` for detailed setup.

---

## Dataset Discovery

```python
from coffea.dataset_tools import rucio_utils
from coffea.dataset_tools.dataset_query import print_dataset_query

# Query Rucio for files and replicas
outlist, outtree = rucio_utils.query_dataset(
    "/DYJetsToLL_M-50.../NANOAODSIM"
)
outfiles, outsites, sites_counts = rucio_utils.get_dataset_files_replicas(
    dataset="/DYJetsToLL_M-50.../NANOAODSIM"
)
site = max(sites_counts, key=sites_counts.get)  # select site with most replicas

# High-level: DataDiscoveryCLI class
```

`coffea.dataset_tools` API: `preprocess`, `apply_to_dataset`, `apply_to_fileset`, `max_chunks`, `max_files`, `slice_chunks`, `filter_files`, `get_failed_steps_for_fileset`.

See `references/example_dataset_discovery.md` for full Rucio + preprocessing workflow.
See `references/example_filespec.md` for file specification patterns.

---

## ML Inference (`coffea.ml_tools`)

Coffea provides wrappers for running ML model inference inside Dask-mode processors:

- Converts and pads awkward arrays to ML tool containers
- Supports PyTorch (GNN example: ParticleNet-like jet variable calculation)
- Required only in Dask / dask-awkward mode

See `references/example_mltools.md` for PyTorch GNN inference example.

---

## Lumi Tools (`coffea.lumi_tools`)

```python
from coffea.lumi_tools import LumiMask, LumiData

# Apply golden JSON lumi mask to data
lumimask = LumiMask("Cert_Run2018D.json")
good_lumi = lumimask(events.run, events.luminosityBlock)
```

---

## API Reference

Top-level coffea modules:

| Module | Key Classes / Functions |
|---|---|
| `coffea.analysis_tools` | `Weights`, `PackedSelection`, `NminusOne`, `Cutflow`, `WeightStatistics` |
| `coffea.btag_tools` | `BTagScaleFactor` |
| `coffea.dataset_tools` | `preprocess`, `apply_to_fileset`, `ROOTFileSpec`, `DatasetSpec`, rucio_utils |
| `coffea.jetmet_tools` | JEC/JER correction tools |
| `coffea.lookup_tools` | Legacy ROOT histogram evaluator |
| `coffea.lumi_tools` | `LumiMask`, `LumiData` |
| `coffea.ml_tools` | ML inference wrappers (Dask mode) |
| `coffea.nanoevents` | `NanoEventsFactory`, schema classes |
| `coffea.nanoevents.methods` | `base`, `candidate`, `nanoaod`, `vector` behaviors |
| `coffea.processor` | `ProcessorABC`, `Runner`, all executor classes |
| `coffea.util` | `save`, `load` |

See `references/api_reference.md` for the full class/function listing.

---

## References

### User Guides
- `references/datasets_guide.md` — How to prepare datasets (fileset formats, Rucio, metadata, best practices)
- `references/nanoevents_guide.md` — How to work with NanoEvents (branch access, schemas, cross-refs, vector behaviors)
- `references/accumulators_guide.md` — How to collect results (hist.Hist, dict accumulators, Weights, serialization)
- `references/corrections_guide.md` — How to apply corrections (correctionlib, btag_tools, jetmet_tools, systematics)
- `references/executors_guide.md` — How to scale with executors (all executor types, Runner config, checkpointing)

### Example Notebooks
- `references/example_nanoevents.md` — Reading data with NanoEvents (schemas, delayed access, vector ops)
- `references/example_corrections.md` — Applying corrections (correctionlib, lookup_tools, btag_tools)
- `references/example_analysis_tools.md` — Analysis tools (Weights, PackedSelection, cutflows, histograms)
- `references/example_packedselection.md` — PackedSelection (cutflow, N-1 plots, region definitions)
- `references/example_systematics.md` — Object systematics (UpDownSystematic, UpDownMultiSystematic)
- `references/example_processing.md` — Processing and scaling (full ProcessorABC + Runner + executor demo)
- `references/example_advanced_numba.md` — Advanced Numba (JIT-compiled custom kernels)
- `references/example_mltools.md` — ML tools (PyTorch GNN inference in Dask mode)
- `references/example_dataset_discovery.md` — Dataset discovery (Rucio queries, DataDiscoveryCLI, preprocessing)
- `references/example_filespec.md` — File specification patterns (ROOTFileSpec, ParquetFileSpec, CoffeaROOTFileSpec)

### API
- `references/api_reference.md` — Full coffea Python API reference (all modules, classes, functions)

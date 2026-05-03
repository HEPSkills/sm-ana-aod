# How to Prepare Datasets (Coffea)

Source: https://coffea-hep.readthedocs.io/en/latest/user_guide/datasets.html

## Fileset Formats

Three supported patterns:

### Format 1: File-to-Tree Mapping (Recommended)

```python
fileset = {
    "DYJets": {
        "files": {
            "/store/mc/.../nano_dy.root": "Events",
            "/store/mc/.../nano_dy_2.root": "Events",
        },
        "metadata": {"year": 2018, "is_mc": True},
    },
}
```

- Top-level keys → dataset identifiers, accessible via `events.metadata['dataset']`
- Each file explicitly declares its tree name (allows mixed tree names within a dataset)
- Metadata merges into chunk metadata dicts available during processing

### Format 2: Uniform Tree Names Per Dataset

```python
fileset = {
    "DYJets": {
        "treename": "Events",
        "files": ["/store/mc/.../nano_dy.root", "/store/mc/.../nano_dy_2.root"],
        "metadata": {"year": 2018, "is_mc": True},
    },
}
```

### Format 3: Global Tree Name (via Runner)

```python
result = runner(fileset, processor_instance=my_processor, treename="Events")
```

---

## Remote and Local File Access

Coffea delegates file access to uproot, which accepts:
- Local filesystem paths
- XRootD URLs: `root://cmsxrootd.fnal.gov//store/mc/...`
- Glob patterns for pattern matching

Mixed storage backends within a single fileset are supported.

---

## Programmatic File Discovery

### Rucio Integration

```python
from coffea.dataset_tools.rucio_utils import get_dataset_files_replicas

outfiles, outsites, sites_counts = get_dataset_files_replicas(
    dataset="/DYJetsToLL_M-50.../NANOAODSIM",
)

# Select optimal site by replica count
site = max(sites_counts, key=sites_counts.get)
```

Returns file lists, available sites per file, and replica statistics for intelligent site selection.

---

## Metadata Handling

Metadata travels with each processing chunk:

```python
def process(self, events):
    dataset = events.metadata["dataset"]       # automatic
    xsec = events.metadata.get("cross_section", 1.0)
    year = events.metadata.get("year")
```

Common metadata uses:
- Cross-section values for event weighting
- Year/era tags for detector configuration
- MC vs. data flags
- Analysis-specific parameters

---

## Persistence and Sharing

Filesets serialize to JSON:

```python
import json
with open("fileset.json", "w") as fout:
    json.dump(fileset, fout, indent=2)
```

Store under version control as input documentation for reproducibility.

---

## Development Optimization

Reduce filesets for testing:

```python
mini_fileset = {
    dataset: {
        "files": {list(info["files"].items())[0][0]: list(info["files"].items())[0][1]},
        "metadata": info.get("metadata", {}),
    }
    for dataset, info in fileset.items()
}
```

Use `NanoEventsFactory.from_root(..., entry_stop=N)` to limit event counts during schema validation.

---

## Best Practices

- Preserve event counts and generator weight sums in metadata
- Merge upstream if handling numerous small files (reduces scheduler overhead)
- Store JSON filesets under version control
- Validate schemas locally before deploying large production jobs

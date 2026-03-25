---
name: sm-ana-aod
description: Perform Standard Model searches and analysis using ATLAS Open Data. Use this skill when the user wants to analyze fundamental particles and forces, investigate Standard Model processes, or perform event selection and plotting using the ATLAS Open Data format and datasets.
---

# Standard Model Analysis with ATLAS Open Data (sm-ana-aod)

This skill provides a modular, production-ready Standard Operating Procedure for ATLAS Open Data analysis.

## Design Philosophy
- **Modern & Modular**: Separate data loading, signal region selection, and plotting into reusable modules.
- **Config-Driven**: Use YAML files to define cuts, samples, and plotting parameters.
- **Iterative & Visual**: Output plots at each major step for validation.
- **Extensible**: Easy to add new functions or workflows.

## Project Structure
```text
analysis_project_directory/
├── config/
│   ├── samples.yaml      		# DID definitions, colors, labels
│   └── cuts.yaml         		# Cutflow definitions
├── scripts/
│   ├── analysis_data_loader.py # Data loading and caching (XRootD/HTTPS)
│   ├── processor.py      		# Core analysis loop (uproot/awkward)
│   ├── selection.py      		# Physics selection functions
│   └── plotter.py        		# Modern plotting (mplhep based)
└── main.py               		# Entry point
```

## SOP

1.  Environment Setup
2.  Data Access
3.  Signal Region Definition
4.  Run Analysis
5.  Review Output

### Environment Setup

1. **Attach to tmux session**: `tmux -S ${TMPDIR}/openclaw-tmux-sockets/openclaw.sock attach -t sm-ana-aod`
2. **Navigate to analysis project directory**
3. **Install dependencies**:
   1. XRootD:
      - macOS: `brew install xrootd`
      - **Debian 11+/Ubuntu 22.04+**: `sudo apt install xrootd-client xrootd-server python3-xrootd`

   2. Python packages
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate
   pip install xrootd atlasopenmagic uproot awkward vector matplotlib mplhep pyyaml tqdm
   ```
   3. Initialize from Python:
   ```python
   import sys
   from atlasopenmagic import install_from_environment
   install_from_environment()
   ```

### Data Access

1. 💡 **Analyze User's intent and physics**
   - What is(are) the signal process(es) of interest
   - What are the main backgrounds
   - What are the key variables to discriminate signal from background and plotting
   - Ask User for review

2. 🌐 **ATLAS Open Data release**
   List and select (if not selected by User): `python3 -c 'import atlasopenmagic as atom; atom.available_releases()'`

3. 🏷️ **Skimming**
   List and select (if not selected by User): `python3 -c 'import atlasopenmagic as atom; atom.set_release("2025e-13tev-beta"); print(atom.available_skims())'`

4. 📌 **DIDs** for signal and backgrounds
   - For each process, search for DIDs if not provided by User
   - Example of searching $V+$jets: `python3 -c 'import atlasopenmagic as atom, json; atom.set_release("2025e-13tev-beta"); datasets = {did: atom.get_metadata(did) for did in atom.available_datasets()}; dataset = {k: {"physics_short": v.get("physics_short"), "description": v.get("description")} for k, v in datasets.items() if any(x in (v.get("physics_short") or "") for x in ["Zee", "Zmumu", "Ztautau" ,"Znunu", "Wenu", "Wmunu", "Wtaunu"])}; print(json.dumps(dataset, indent=0))'`

5. 🧮 **Key variables** to discriminate signal from background and plotting
   List and select (if not provided by User): `python3 -c 'import uproot; import atlasopenmagic as atom; atom.set_release("2025e-13tev-beta"); samples = atom.build_dataset({"test": {"dids": ["301204"]}}, skim="2bjets"); url = samples["test"]["list"][0]; f = uproot.open(url); print(f["analysis"].keys())'`

6. ☁️  **Data Loader**
   Write file `analysis_data_loader.py`, template:

```python
# analysis_data_loader.py

print("\033[92m[Analysis Data Loader] Loading ATLAS Open Data release\033[0m")

import atlasopenmagic as atom
atom.available_releases()
atom.set_release('2025e-13tev-beta')

# Select the skim to use for the analysis
skim = "2bjets"

defs = {
    r'Data':{'dids':['data']},
    r'Signal':  {'dids': [...],'color': "red" },
    r'Background ...': {'dids': [...],'color':'orange'},
    ...
}

# Get URLs
samples = atom.build_dataset(defs, skim=skim, protocol='https', cache=False)

# Define what variables are important to our analysis
variables = [...]

```

### Signal Region Definition

**Define Config**: Edit `config/cuts.yaml` to specify your selection (e.g., $E_T^{miss} > 150$ GeV, $n_{b-jets} == 2$).

### Run Analysis

- Download/Cache remote ROOT files via XRootD/HTTPS.
- Apply the modular selection logic.
- Save intermediate state for plotting.

## Resources

- [ATLAS Open Data](https://opendata.atlas.cern/)
- [mplhep Documentation](https://mplhep.readthedocs.io/en/latest/) (Preferred for HEP styling)

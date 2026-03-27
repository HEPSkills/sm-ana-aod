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
analysisProjectDir/
├── config/
│   ├── samples.yaml      		# DID definitions, colors, labels
│   └── cuts.yaml         		# Cutflow definitions
├── scripts/
│   ├── data_loader.py # Data loading and caching (XRootD/HTTPS)
│   ├── processor.py      		# Core analysis loop (uproot/awkward)
│   ├── selection.py      		# Physics selection functions
│   └── plotter.py        		# ATLAS Style
└── main.py               		# Entry point
```

## Workflow

1.  Environment Setup
2.  Data Access
3.  Signal Region Definition
5.  Run Analysis
6.  Review Output

### Environment Setup

1. 🔎 **Navigate to analysis project directory**
2. 🛠️ **Install dependencies**:
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
   Write file `data_loader.py`, template:

```python
# data_loader.py

print("\033[92m[Data Loader] Loading ATLAS Open Data release\033[0m")

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

Write file `selection.py` and define alls functions for

- weight

- high-level physics observables/objects (for example invariant mass)
- Selection functions (for cutflow)

Example template:

```python
# selection.py

import awkward as ak
import numpy as np
import vector

MeV = 0.001
GeV = 1.0
lumi = 36.1 # fb-1 for all the data that's been released, 2015 and 2016 together

def calc_weight(events):
    return (
        ((lumi*1000. #*1000 to go from fb-1 to pb-1
        * events['xsec']
        * events['mcWeight']
        * events['ScaleFactor_PILEUP']
        * events['ScaleFactor_FTAG']
        * events['ScaleFactor_JVT']
        * events['filteff']
        * events['kfac'])
        / (events['sum_of_weights']))
    )
    
vector.register_awkward()
def calc_mbb(data):
    # Count jets above pT threshold
    bjet = data['btag_ID']
    btag_jet_pt = data['jet_pt'][bjet]
    btag_jet_eta = data['jet_eta'][bjet]
    btag_jet_phi = data['jet_phi'][bjet]


    correct = (data['jet_pt'][bjet]<100)
    abhundred = (data['jet_pt'][bjet]>=100)

    # For jets without a matching lepton, the PtReco correction increases
    # the energy of jets with pT ∼ 20 GeV by 12% and the energy of those
    # with pT > 100 GeV by 1%, while a larger correction is observed
    # for jets matched to a lepton, due to the missing neutrino energy.
    btag_jet_e = ((data['jet_e'][bjet]*((1+((((-11./80.)*data['jet_pt'][bjet]+14.76))/100.)) ))*correct + data['jet_e'][bjet]*1.01*abhundred)
    p = ak.zip({"pt": btag_jet_pt, "eta": btag_jet_eta, "phi": btag_jet_phi, "E": btag_jet_e}, with_name="Momentum4D")
    invariant_mass = (p[:, 0] + p[:, 1]).M # .M calculates the invariant mass
    return invariant_mass

def select_jets(data, central_pt_cut=20.0, central_eta_cut=2.5, forward_pt_cut=30.0, forward_eta_cut=4.5):
    # Count jets above pT threshold
    jet_pt = data['jet_pt']
    jet_eta = abs(data['jet_eta'])
    jet_jvt = data['jet_jvt']

    cjet = ((jet_jvt == 1) & (data['jet_pt'] > central_pt_cut) & (abs(data['jet_eta']) < central_eta_cut))
    fjet = ((jet_jvt == 1) & (data['jet_pt'] > forward_pt_cut * GeV) & (abs(data['jet_eta']) >= 2.5) & (abs(data['jet_eta']) < forward_eta_cut))
    bjet = ((cjet) & (data['btag_ID']))
    bjet45 = ((cjet) & (data['btag_ID']) & (data['jet_pt'] > 45 * GeV))

    njet = ((ak.sum(((cjet) | (fjet)), 1) == 2) | (ak.sum(((cjet) | (fjet)), 1) == 3))

    nbjet = ak.sum(bjet,1) == 2
    nbjet45 = ak.sum(bjet45,1) == 1

    return (njet & nbjet & nbjet45)

def select_zero_leptons(data):
    lep_pt = data['lep_pt']
    lep_eta = abs(data['lep_eta'])
    lep_type = data['lep_type']
    lep_d0sig = data['lep_d0sig']
    lep_z0 = data['lep_z0']
    lep_iso = data['lep_isLooseIso']

    select_electrons = ((lep_type==11) & (lep_pt > 7 * GeV) & (lep_eta < 2.47) & (lep_d0sig < 5) & (lep_z0 < 0.5) & (lep_iso == 1) & (data['lep_isLooseID'] == 1))
    select_muons = ((lep_type==13) & (lep_pt > 7 * GeV) & (lep_eta < 2.7) & (lep_d0sig < 3) & (lep_z0 < 0.5) & (lep_iso == 1) & (data['lep_isLooseID'] == 1))

    nel = ak.sum(select_electrons,1)
    nmu = ak.sum(select_muons,1)
    nlep = nel + nmu

    return ((nel == 0) & (nmu == 0))

...
```

### Run Analysis

Execute the full chain: Data loading $\to$ Selection $\to$ Weighting $\to$ Plotting.

see `{baseDir}/references/hbb_analysis.py`

## Resources

- [ATLAS Open Data Release Notes](https://opendata.atlas.cern/release/2020/notes/analysis/Hbb.html)
- [uproot/awkward-array Tutorial](https://uproot.readthedocs.io/)
- [mplhep Styling Guide](https://mplhep.readthedocs.io/en/latest/styles.html)

---
name: ana-create-data-loader
description: Create a data loader for the analysis. This involves selecting the appropriate ATLAS Open Data release, skimming the data to focus on relevant events, and identifying key variables for the analysis.
---

# Online Data Access

1. 💡 **Analyze User's intent and physics**
   - What is the signal process (or processes) of interest?
   - What are the main backgrounds
   - What are the key variables to discriminate signal from background and plotting

2. 🌐 **Select ATLAS Open Data release**
   - Skip this step if User has already selected a release
   - List and select: `python3 -c 'import atlasopenmagic as atom; atom.available_releases()'`

3. 🏷️ **Select Skimming**
   - Skip this step if User has already selected a skim
   - List and select: `python3 -c 'import atlasopenmagic as atom; atom.set_release("2025e-13tev-beta"); print(atom.available_skims())'`

4. 📌 Search **DIDs** for signal and backgrounds
   - Skip this step if User has already provided DIDs for signal and backgrounds
   - Example of searching $V+$jets: `python3 -c 'import atlasopenmagic as atom, json; atom.set_release("2025e-13tev-beta"); datasets = {did: atom.get_metadata(did) for did in atom.available_datasets()}; dataset = {k: {"physics_short": v.get("physics_short"), "description": v.get("description")} for k, v in datasets.items() if any(x in (v.get("physics_short") or "") for x in ["Zee", "Zmumu", "Ztautau", "Znunu", "Wenu", "Wmunu", "Wtaunu"])}; print(json.dumps(dataset, indent=0))'`

5. 🧮 **Select variables** for signal/background discrimination and plotting
   - Skip this step if User has already provided variables list
   - List and select: `python3 -c 'import uproot; import atlasopenmagic as atom; atom.set_release("2025e-13tev-beta"); samples = atom.build_dataset({"test": {"dids": ["301204"]}}, skim="2bjets"); url = samples["test"]["list"][0]; f = uproot.open(url); print(f["analysis"].keys())'`

6. Create Data Loader

Write data loading module to file `data_loader.py`, template:

```python
# data_loader.py

print("\033[92m[Data Loader] Loading ATLAS Open Data release\033[0m")

import atlasopenmagic as atom
atom.available_releases()
atom.set_release(...)

# Select the skim to use for the analysis
skim = ...

defs = {
    r'Data': {'dids': ['data']},
    r'Signal': {'dids': [...], 'color': "red" },
    r'Background ...': {'dids': [...], 'color': 'orange'},
    ...
}

# Get URLs with cache=False
samples = atom.build_dataset(defs, skim=skim, protocol='https', cache=False)

# Define what variables are important to our analysis
variables = [...]

```

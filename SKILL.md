---
name: sm-ana-aod
description: Perform Standard Model searches and analysis using ATLAS Open Data. Use this skill when the user wants to analyze fundamental particles and forces, investigate Standard Model processes, or perform event selection and plotting using the ATLAS Open Data format and datasets.
---

# Standard Model Analysis with ATLAS Open Data (sm-ana-aod)

This skill provides a modular, production-ready Standard Operating Procedure for ATLAS Open Data analysis.

## Key Requirments

- **Code Centralization:** Save every analysis **scripts** and **outputs** in the /home/agent/analysis/, NOT in ${baseDir}
- **Log to file**: When running scripts/commands, use `tee` to save the log to loacal file.

**Code Style**

- **Modern & Modular**: Separate data loading, signal region selection, and plotting into reusable modules.
- **Config-Driven**: Use YAML files to define cuts, samples, and plotting parameters.
- **Iterative & Visual**: Output plots at each major step for validation.
- **Extensible**: Easy to add new functions or workflows.

## Project Structure
```text
home/agent/analysis/
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

### 1. Environment Setup

1. 🔎 **Navigate to analysis project directory**
2. 🛠️ **Install dependencies**:
   1. XRootD:
      - macOS: `brew install xrootd`
      - **Debian 11+/Ubuntu 22.04+**: `sudo apt install build-essential xrootd-client xrootd-server python3-xrootd`

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

   Notes:

- Use venv with **python3.12**

### 2. Online Data Access

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

### 3. Signal Region Definition

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

### 4. Data Visualization

1. **Data Preparation**: Download the online data to local cache directory (use .tmp to prevent corrupted files)

   Example:

```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import uproot
import awkward as ak
import vector
import time
import os
import requests
from tqdm import tqdm

from data_loader import *
from selection import *

weight_variables = ['xsec', 'mcWeight', 'ScaleFactor_PILEUP', 'ScaleFactor_FTAG', 'ScaleFactor_JVT', 'filteff', 'kfac', 'sum_of_weights']

fraction = 1
# Define empty dictionary to hold awkward arrays
all_data = {}

# Ensure cache directory exists
os.makedirs('./cache', exist_ok=True)

# Loop over samples
for s in samples:
    # Print which sample is being processed
    print('Processing '+s+' samples')

    # Define empty list to hold data for each sample
    frames = []

    # Loop over each file
    for val in samples[s]['list'][0:2]:

        url = val # file name / URL to open
        filename = url.split('/')[-1]
        local_path = f'./cache/{filename}'
        temp_path = f'./cache/{filename}.tmp'

        # Download logic
        if not os.path.exists(local_path):
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                with open(temp_path, 'wb') as f:
                    with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"  Downloading: {filename}", leave=False) as pbar:
                        for chunk in r.iter_content(chunk_size=8*1024*1024):
                            f.write(chunk)
                            pbar.update(len(chunk))
                os.replace(temp_path, local_path)

        # start the clock
        start = time.time()
        
        # Open local cached file instead of the URL
        tree = uproot.open(local_path + ":analysis")

        sample_data = []
```

2. **Event Selection**

3. **High-level physics observable/object calculation**

4. **"Money" Plots**

   Follow this plotting style:

```python
# Variable to plot.
# Set to either "mass" (for invariant mass of two b-jets) or
# "met" for the missing transverse energy
variable_to_plot = 'mass'
# x-axis range of the plot
if variable_to_plot == "met":
    step_size = 25* GeV
    xmin = 150 * GeV
    xmax = 500 * GeV
else:
    step_size = 20* GeV
    xmin = 20 * GeV
    xmax = 500 * GeV


bin_edges = np.arange(start=xmin, # The interval includes this value
                    stop=xmax+step_size, # The interval doesn't include this value
                    step=step_size ) # Spacing between values
bin_centres = np.arange(start=xmin+step_size/2, # The interval includes this value
                        stop=xmax+step_size/2, # The interval doesn't include this value
                        step=step_size ) # Spacing between values

bin_left = np.arange(start=xmin, # The interval includes this value
                        stop=xmax+step_size, # The interval doesn't include this value
                        step=step_size ) # Spacing between values

data_x,_ = np.histogram(np.clip(ak.to_numpy(all_data['Data'][variable_to_plot]),bin_edges[0],bin_edges[-2]),
                        bins=bin_edges ) # histogram the data
data_x_errors = np.sqrt( data_x ) # statistical error on the data

signal_x = np.clip(ak.to_numpy(all_data['Signal'][variable_to_plot]),bin_edges[0],bin_edges[-2]) # histogram the signal
signal_weights = ak.to_numpy(all_data['Signal'].totalWeight) # get the weights of the signal events
signal_color = samples['Signal']['color'] # get the colour for the signal bar

mc_x = [] # define list to hold the Monte Carlo histogram entries
mc_weights = [] # define list to hold the Monte Carlo weights
mc_colors = [] # define list to hold the colors of the Monte Carlo bars
mc_labels = [] # define list to hold the legend labels of the Monte Carlo bars

for s in samples: # loop over samples
    if s not in ['Data', 'Signal']: # if not data nor signal
        # if 'V' in s or 'bar' in s:
        #     print(f'skip {s}')
        #     break
        mc_x.append( np.clip(ak.to_numpy(all_data[s][variable_to_plot]),bin_edges[0],bin_edges[-2]) ) # append to the list of Monte Carlo histogram entries
        mc_weights.append( ak.to_numpy(all_data[s].totalWeight) ) # append to the list of Monte Carlo weights
        mc_colors.append( samples[s]['color'] ) # append to the list of Monte Carlo bar colors
        mc_labels.append( s ) # append to the list of Monte Carlo legend labels

# *************
# Main plot
# *************
fig = plt.gcf()
fig.set_size_inches(18.5, 10.5)

# Create a 2-row grid layout
fig, (main_axes, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(8, 6),
                               gridspec_kw={'height_ratios': [3, 1]})
fig.set_size_inches(13.5, 13.5)
#main_axes = plt.gca() # get current axes

# plot the data points
main_axes.errorbar(x=bin_centres, y=data_x, yerr=data_x_errors,
                   fmt='ko', # 'k' means black and 'o' is for circles
                   markersize=4, # Adjust the size of the circles
                   label='Data')

# # plot the Monte Carlo bars
mc_heights = main_axes.hist(mc_x, bins=bin_edges,
                            weights=mc_weights, stacked=True,
                            color=mc_colors,
                            label=mc_labels )

mc_x_tot = mc_heights[0][-1] # stacked background MC y-axis value

# calculate MC statistical uncertainty: sqrt(sum w^2)
mc_x_err = np.sqrt(np.histogram(np.hstack(mc_x), bins=bin_edges, weights=np.hstack(mc_weights)**2)[0])

# plot the signal bar
signal_heights = main_axes.hist(signal_x, bins=bin_edges, bottom=mc_x_tot,
                    weights=signal_weights, color=signal_color,
                    label=r'Signal ($m_H$ = 125 GeV)')

signal_x_tot = signal_heights[0]# stacked background MC y-axis value

# plot the statistical uncertainty
main_axes.bar(bin_centres, # x
                2*mc_x_err, # heights
                alpha=0.5, # half transparency
                bottom=mc_x_tot-mc_x_err, color='none',
                hatch="////", width=step_size, label='Stat. Unc.' )

# plot the signal bar
main_axes.hist(signal_x, bins=bin_edges, #bottom=mc_x_tot,
                weights=signal_weights*(10 if variable_to_plot == "met" else 5), color=signal_color, histtype='step', linewidth=1.5,
                label=r'Signal ($m_H$ = 125 GeV) x %i'%(10 if variable_to_plot == "met" else 5))

if variable_to_plot == "met":
    ax2.tick_params(axis='y', labelsize=20)
    main_axes.set_xticks(list(np.arange(0, 550, step=25)), list(np.arange(0, 550, step=25)))  # Set text labels and properties.
    ax2.set_xticks(list(np.arange(0, 550, step=25)), list(np.arange(0, 550, step=25)),fontsize=20)  # Set text labels and properties.
else:
    main_axes.set_xticks(list(np.arange(0, 520, step=20)), list(np.arange(0, 520, step=20)))  # Set text labels and properties.
    ax2.set_xticks(list(np.arange(0, 520, step=20)), list(np.arange(0, 520, step=20)),fontsize=16)  # Set text labels and properties.
    ax2.tick_params(axis='y', labelsize=20)
main_axes.tick_params(axis='y', labelsize=20)

# set the x-limit of the main axes
main_axes.set_xlim( left=xmin, right=xmax )

# separation of x axis minor ticks
main_axes.xaxis.set_minor_locator( AutoMinorLocator() )

# set the axis tick parameters for the main axes
main_axes.tick_params(which='both', # ticks on both x and y axes
                        direction='in', # Put ticks inside and outside the axes
                        top=True, # draw ticks on the top axis
                        right=True ) # draw ticks on right axis


# write y-axis label for main axes
main_axes.set_ylabel('Events / '+str(step_size)+' GeV',
                        y=1, horizontalalignment='right',fontsize=40)



# add minor ticks on y-axis for main axes
main_axes.yaxis.set_minor_locator( AutoMinorLocator() )

if variable_to_plot == "met":
    xtit = r'$E_{T}^{miss}$ [GeV]'
    main_axes.set_yscale('log')
    # set y-axis limits for main axes
    main_axes.set_ylim( bottom=0.4, top=350000)#np.amax(data_x)*1.6 )
else:
    xtit = r'$m_{bb}$ [GeV]'
    #main_axes.set_yscale('log')
    main_axes.set_ylim( bottom=0.1, top=1120)#np.amax(data_x)*1.6 )
    ax2.set_ylim( bottom=0.45, top=4.5)#np.amax(data_x)*1.6 )
# draw the legend
main_axes.legend( frameon=False, fontsize=20 ); # no box around the legend

# Calculate the ratio where counts2 is not zero
this_data_x = data_x.astype('float64')
ratio = np.divide(this_data_x , (mc_x_tot + signal_x_tot), out=np.zeros_like(this_data_x), where=(mc_x_tot != 0))


# Calculate uncertainty in the ratio using propagation of uncertainty
ratio_uncertainty = ratio * np.sqrt((data_x_errors/this_data_x)**2 + (mc_x_err/(mc_x_tot + signal_x_tot))**2)


ratio_uncertainty[ratio_uncertainty < 0] = 0      # Replace negative numbers with 0
ratio_uncertainty[np.isnan(ratio_uncertainty)] = 0  # Replace NaN with 0

# Plot the ratio with markers in the bottom subplot
mid_bins = 0.5 * (bin_edges[:-1] + bin_edges[1:])  # Midpoints of bins for plotting
bin_widths = np.diff(bin_edges) / 2  # Half bin width for each midpoint

# To get the edges right need to add an additional point to the right of the axis limits
mc_x_err = np.append(mc_x_err,mc_x_err[-1])
mc_x_tot = np.append(mc_x_tot,mc_x_tot[-1])

uncertainty = 0.1
# Add a shaded area representing the error around ratio = 1
ax2.fill_between(bin_left, 1 - mc_x_err/mc_x_tot, 1 + mc_x_err/mc_x_tot,
                 hatch="////",color='gray', alpha=0.5, label='Error Band', step = 'pre')

ax2.errorbar(mid_bins, ratio, xerr=bin_widths ,yerr=ratio_uncertainty,fmt="o", color='black')
ax2.set_xlabel(xtit ,fontsize=40,loc='right')
ax2.set_ylabel('Data/Pred.',fontsize=20)
ax2.set_ylim( bottom=0.4, top=1.6)#np.amax(data_x)*1.6 )
ax2.grid(True)  # Enable gridlines for the bottom subplot

# add minor ticks on y-axis for main axes
ax2.yaxis.set_minor_locator( AutoMinorLocator() )

# Adjust layout
plt.tight_layout()

plt.savefig('mbb.png')
print("Plot saved as mbb.png")
```

   Notes:

- Often we draw ratio plots
- Main panel: complete list of curves of:
  - Stacked MC backgrounds
  - MC signals
  - Observed Data
  - Statistical Uncertainty of MC background
- Ratio panel:
  - Data / Pred.

### 5. Fitting

- Select the parameter of interests
- Select/Construct the fit function
- Fit the Parameter of Interest to maximize the likelihood of statistical model with the observed data.
- Do plotting

## Resources

- [ATLAS Open Data Release Notes](https://opendata.atlas.cern/release/2020/notes/analysis/Hbb.html)
- [uproot/awkward-array Tutorial](https://uproot.readthedocs.io/)
- [mplhep Styling Guide](https://mplhep.readthedocs.io/en/latest/styles.html)

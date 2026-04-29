---
name: ana-create-event-selector
description: Create event selection module for the signal region definition.
---

# Signal Region Definition

Write complete event selection module to file `event_selector.py` and define functions for
- Physics observables/objects calculation (for example invariant mass etc.)
- Selection function for each cut in the cutflow
- Weight calculation

Template:

```python
# event_selector.py

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

## References

Read cuts from these files

```
references/hbb_selections.json
references/hmumu_selections.json
references/hyy_selections.json
references/hzz4l_selections.json
references/ttbar_selections.json
references/wz3l_selections.json
references/z_mumu_selections.json
```

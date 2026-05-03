Object systematics — coffea 2026.4.1.dev3+gbfc8fd2cf.d20260501 documentation
[Skip to main content](#main-content)
Back to top
Ctrl+K
* [Getting Started](../getting_started/index.html)
* [User Guide](../user_guide/index.html)
* [Coffea by Example](../examples.html)
* [API Reference Guide](../api_reference.html)
* [Contributing to coffea](../contributing.html)
Search
Ctrl+K
Search
Ctrl+K
* [Getting Started](../getting_started/index.html)
* [User Guide](../user_guide/index.html)
* [Coffea by Example](../examples.html)
* [API Reference Guide](../api_reference.html)
* [Contributing to coffea](../contributing.html)
Collapse Sidebar
Expand Sidebar
Section Navigation
* [Reading data with coffea NanoEvents](nanoevents.html)
* [Applying corrections to columnar data](applying_corrections.html)
* [Analysis tools](analysis_tools.html)
* [Packed Selection](packedselection.html)
* Object systematics
* [Processing and Scaling](processing.html)
* [Jit compilation with Numba](advanced_numba.html)
* [Running inference tools](mltools.html)
* [Dataset discovery tools](dataset_discovery.html)
* [Dataset specification with FileSpec classes](filespec.html)
* [Coffea by Example](../examples.html)
* Object systematics
# Object systematics[#](#object-systematics)
This is a rendered copy of [systematics.ipynb](https://github.com/scikit-hep/coffea/blob/master/binder/systematics.ipynb). You can optionally run it interactively on [binder at this link](https://mybinder.org/v2/gh/coffeateam/coffea/master?filepath=binder%2Fsystematics.ipynb)
This notebook presents how to add systematics to objects in coffea.
Coffea currently implements two types of object systematics. `UpDownSystematic` which varies one field on the object it is applied on and `UpDownMultiSystematic` which varies multiple fields on the object it is applied on.
Check the snippets below for example usage.
```
import awkward
import numpy as np
from coffea import nanoevents
def get_array(array):
return array.compute() if nanoevents_mode == "dask" else array
nanoevents_mode = "virtual"
access_log = []
events = nanoevents.NanoEventsFactory.from_root({"coffea/tests/samples/nano_dy.root": "Events"}, mode=nanoevents_mode, access_log=access_log).events()
muons = events.Muon
jets = events.Jet
met = events.MET
```
```
/home/iason/Dropbox/work/pyhep_dev/coffea/src/coffea/nanoevents/schemas/nanoaod.py:264: RuntimeWarning: Missing cross-reference index for LowPtElectron_electronIdx => Electron
warnings.warn(
/home/iason/Dropbox/work/pyhep_dev/coffea/src/coffea/nanoevents/schemas/nanoaod.py:264: RuntimeWarning: Missing cross-reference index for LowPtElectron_genPartIdx => GenPart
warnings.warn(
/home/iason/Dropbox/work/pyhep_dev/coffea/src/coffea/nanoevents/schemas/nanoaod.py:264: RuntimeWarning: Missing cross-reference index for LowPtElectron_photonIdx => Photon
warnings.warn(
/home/iason/Dropbox/work/pyhep_dev/coffea/src/coffea/nanoevents/schemas/nanoaod.py:264: RuntimeWarning: Missing cross-reference index for FatJet_genJetAK8Idx => GenJetAK8
warnings.warn(
```
```
def some_event_weight(ones):
return (1.0 + np.array([0.05, -0.05], dtype=np.float32)) * ones[:, None]
events.add_systematic("RenFactScale", "UpDownSystematic", "weight", some_event_weight)
events.add_systematic("XSectionUncertainty", "UpDownSystematic", "weight", some_event_weight)
def muon_pt_scale(pt):
return (1.0 + np.array([0.05, -0.05], dtype=np.float32)) * pt[:, None]
def muon_pt_resolution(pt):
return np.random.normal(pt[:, None], np.array([0.02, 0.01], dtype=np.float32))
def muon_eff_weight(ones):
return (1.0 + np.array([0.05, -0.05], dtype=np.float32)) * ones[:, None]
def muon_pt_phi_systematic(ptphi):
pt_var = (1.0 + np.array([0.05, -0.05], dtype=np.float32)) * ptphi.pt[:, None]
phi_var = (1.0 + np.array([0.1, -0.1], dtype=np.float32)) * ptphi.phi[:, None]
return awkward.zip({"pt": pt_var, "phi": phi_var}, depth_limit=1)
muons.add_systematic("PtScale", "UpDownSystematic", "pt", muon_pt_scale)
muons.add_systematic("PtResolution", "UpDownSystematic", "pt", muon_pt_resolution)
muons.add_systematic("EfficiencySF", "UpDownSystematic", "weight", muon_eff_weight)
muons.add_systematic("PtPhiSystematic", "UpDownMultiSystematic", ("pt", "phi"), muon_pt_phi_systematic)
def jet_pt_scale(pt):
return (1.0 + np.array([0.10, -0.10], dtype=np.float32)) * pt[:, None]
def jet_pt_resolution(pt):
return np.random.normal(pt[:, None], np.array([0.20, 0.10], dtype=np.float32))
def jet_pt_phi_systematic(ptphi):
pt_var = (1.0 + np.array([0.10, -0.10], dtype=np.float32)) * ptphi.pt[:, None]
phi_var = (1.0 + np.array([0.2, -0.2], dtype=np.float32)) * ptphi.phi[:, None]
return awkward.zip({"pt": pt_var, "phi": phi_var}, depth_limit=1)
jets.add_systematic("PtScale", "UpDownSystematic", "pt", jet_pt_scale)
jets.add_systematic("PtResolution", "UpDownSystematic", "pt", jet_pt_resolution)
jets.add_systematic("PtPhiSystematic", "UpDownMultiSystematic", ("pt", "phi"), jet_pt_phi_systematic)
def met_pt_scale(pt):
return (1.0 + np.array([0.03, -0.03], dtype=np.float32)) * pt[:, None]
def met_pt_phi_systematic(ptphi):
pt_var = (1.0 + np.array([0.03, -0.03], dtype=np.float32)) * ptphi.pt[:, None]
phi_var = (1.0 + np.array([0.05, -0.05], dtype=np.float32)) * ptphi.phi[:, None]
return awkward.zip({"pt": pt_var, "phi": phi_var}, depth_limit=1)
met.add_systematic("PtScale", "UpDownMultiSystematic", "pt", met_pt_scale)
met.add_systematic("PtPhiSystematic", "UpDownMultiSystematic", ("pt", "phi"), met_pt_phi_systematic)
```
```
renfact_up = events.systematics.RenFactScale.up.weight_RenFactScale
get_array(renfact_up)
```
```
[1.05,
1.05,
1.05,
1.05,
1.05,
1.05,
1.05,
1.05,
1.05,
1.05,
...,
1.05,
1.05,
1.05,
1.05,
1.05,
1.05,
1.05,
1.05,
1.05]
------
backend: cpu
nbytes: 320 B
type: 40 * float64
```
```
muon_pt = awkward.flatten(muons.pt)
get_array(muon_pt)
```
```
[76.8,
20.1,
31,
50.6,
14.3,
16.7,
13.9,
46.5,
40.7,
51.4,
39.6,
38.9,
33.7,
17.1,
14.5,
4.36,
10.1,
17.9]
------
backend: cpu
nbytes: 72 B
type: 18 * float32[parameters={"__doc__": "pt", "typename": "float[]"}]
```
```
muon_PtScale_up = awkward.flatten(muons.systematics.PtScale.up)
get_array(muon_PtScale_up)
```
```
[{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...}]
------------------------------------------------------------------
backend: cpu
nbytes: 3.1 kB
type: 18 * Muon[
dxy: float32[parameters={"__doc__": "dxy (with sign) wrt first PV, in cm", "typename": "float[]"}],
dxyErr: float32[parameters={"__doc__": "dxy uncertainty, in cm", "typename": "float[]"}],
dz: float32[parameters={"__doc__": "dz (with sign) wrt first PV, in cm", "typename": "float[]"}],
dzErr: float32[parameters={"__doc__": "dz uncertainty, in cm", "typename": "float[]"}],
eta: float32[parameters={"__doc__": "eta", "typename": "float[]"}],
ip3d: float32[parameters={"__doc__": "3D impact parameter wrt first PV, in cm", "typename": "float[]"}],
jetPtRelv2: float32[parameters={"__doc__": "Relative momentum of the lepton with respect to the closest jet after subtracting the lepton", "typename": "float[]"}],
jetRelIso: float32[parameters={"__doc__": "Relative isolation in matched jet (1/ptRatio-1, pfRelIso04_all if no matched jet)", "typename": "float[]"}],
mass: float32[parameters={"__doc__": "mass", "typename": "float[]"}],
miniPFRelIso_all: float32[parameters={"__doc__": "mini PF relative isolation, total (with scaled rho*EA PU corrections)", "typename": "float[]"}],
...
parameters={"__doc__": "slimmedMuons after basic selection (pt > 3 && (passed('CutBasedIdLoose') || passed('SoftCutBasedId') || passed('SoftMvaId') || passed('CutBasedIdGlobalHighPt') || passed('CutBasedIdTrkHighPt')))", "collection_name": "Muon", "variation": "PtScale-pt-up"}]
```
```
muon_PtScale_up_pt = awkward.flatten(muons.systematics.PtScale.up.pt)
get_array(muon_PtScale_up_pt)
```
```
[80.6,
21.1,
32.6,
53.2,
15,
17.6,
14.6,
48.8,
42.7,
54,
41.6,
40.8,
35.4,
17.9,
15.3,
4.58,
10.6,
18.8]
------
backend: cpu
nbytes: 72 B
type: 18 * float32
```
```
muons_PtPhiSystematic_up = awkward.flatten(muons.systematics.PtPhiSystematic.up)
get_array(muons_PtPhiSystematic_up)
```
```
[{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...},
{dxy: ??, dxyErr: ??, dz: ??, dzErr: ??, eta: ??, ip3d: ??, ...}]
------------------------------------------------------------------
backend: cpu
nbytes: 3.1 kB
type: 18 * Muon[
dxy: float32[parameters={"__doc__": "dxy (with sign) wrt first PV, in cm", "typename": "float[]"}],
dxyErr: float32[parameters={"__doc__": "dxy uncertainty, in cm", "typename": "float[]"}],
dz: float32[parameters={"__doc__": "dz (with sign) wrt first PV, in cm", "typename": "float[]"}],
dzErr: float32[parameters={"__doc__": "dz uncertainty, in cm", "typename": "float[]"}],
eta: float32[parameters={"__doc__": "eta", "typename": "float[]"}],
ip3d: float32[parameters={"__doc__": "3D impact parameter wrt first PV, in cm", "typename": "float[]"}],
jetPtRelv2: float32[parameters={"__doc__": "Relative momentum of the lepton with respect to the closest jet after subtracting the lepton", "typename": "float[]"}],
jetRelIso: float32[parameters={"__doc__": "Relative isolation in matched jet (1/ptRatio-1, pfRelIso04_all if no matched jet)", "typename": "float[]"}],
mass: float32[parameters={"__doc__": "mass", "typename": "float[]"}],
miniPFRelIso_all: float32[parameters={"__doc__": "mini PF relative isolation, total (with scaled rho*EA PU corrections)", "typename": "float[]"}],
...
parameters={"__doc__": "slimmedMuons after basic selection (pt > 3 && (passed('CutBasedIdLoose') || passed('SoftCutBasedId') || passed('SoftMvaId') || passed('CutBasedIdGlobalHighPt') || passed('CutBasedIdTrkHighPt')))", "collection_name": "Muon", "variation": "PtPhiSystematic-('pt', 'phi')-up"}]
```
```
muons_PtPhiSystematic_up_pt = awkward.flatten(muons.systematics.PtPhiSystematic.up.pt)
get_array(muons_PtPhiSystematic_up_pt)
```
```
[80.6,
21.1,
32.6,
53.2,
15,
17.6,
14.6,
48.8,
42.7,
54,
41.6,
40.8,
35.4,
17.9,
15.3,
4.58,
10.6,
18.8]
------
backend: cpu
nbytes: 72 B
type: 18 * float32
```
```
muons_PtPhiSystematic_up_phi = awkward.flatten(muons.systematics.PtPhiSystematic.up.phi)
get_array(muons_PtPhiSystematic_up_phi)
```
```
[1.8,
-3.16,
-1.54,
0.522,
-2.9,
-3.34,
-1.08,
-2.14,
1.66,
3.17,
-0.407,
-0.385,
3.26,
0.532,
-2.88,
-0.784,
-2.41,
3.19]
--------
backend: cpu
nbytes: 72 B
type: 18 * float32
```
```
jets_pt = awkward.flatten(jets.pt)
get_array(jets_pt)
```
```
[80.8,
45.6,
29.6,
17.6,
15.2,
106,
38.9,
26,
19.9,
18.2,
...,
22.1,
56.9,
53.6,
24.7,
21.6,
20.2,
15.2,
18.8,
18.3]
------
backend: cpu
nbytes: 752 B
type: 188 * float32[parameters={"__doc__": "pt", "typename": "float[]"}]
```
```
jets_PtScale_up = awkward.flatten(jets.systematics.PtScale.up)
get_array(jets_PtScale_up)
```
```
[{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
...,
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...}]
----------------------------------------------------------------------------
backend: cpu
nbytes: unknown
type: 188 * Jet[
area: float32[parameters={"__doc__": "jet catchment area, for JECs", "typename": "float[]"}],
btagCMVA: float32[parameters={"__doc__": "CMVA V2 btag discriminator", "typename": "float[]"}],
btagCSVV2: float32[parameters={"__doc__": " pfCombinedInclusiveSecondaryVertexV2 b-tag discriminator (aka CSVV2)", "typename": "float[]"}],
btagDeepB: float32[parameters={"__doc__": "DeepCSV b+bb tag discriminator", "typename": "float[]"}],
btagDeepC: float32[parameters={"__doc__": "DeepCSV charm btag discriminator", "typename": "float[]"}],
btagDeepFlavB: float32[parameters={"__doc__": "DeepFlavour b+bb+lepb tag discriminator", "typename": "float[]"}],
btagDeepFlavC: float32[parameters={"__doc__": "DeepFlavour charm tag discriminator", "typename": "float[]"}],
chEmEF: float32[parameters={"__doc__": "charged Electromagnetic Energy Fraction", "typename": "float[]"}],
chHEF: float32[parameters={"__doc__": "charged Hadron Energy Fraction", "typename": "float[]"}],
eta: float32[parameters={"__doc__": "eta", "typename": "float[]"}],
...
parameters={"__doc__": "slimmedJets, i.e. ak4 PFJets CHS with JECs applied, after basic selection (pt > 15)", "collection_name": "Jet", "variation": "PtScale-pt-up"}]
```
```
jets_PtScale_up_pt = awkward.flatten(jets.systematics.PtScale.up.pt)
get_array(jets_PtScale_up_pt)
```
```
[88.8,
50.2,
32.6,
19.3,
16.8,
116,
42.8,
28.5,
21.9,
20,
...,
24.3,
62.6,
59,
27.2,
23.8,
22.2,
16.7,
20.7,
20.1]
------
backend: cpu
nbytes: 752 B
type: 188 * float32
```
```
jets_PtPhiSystematic_up = awkward.flatten(jets.systematics.PtPhiSystematic.up)
get_array(jets_PtPhiSystematic_up)
```
```
[{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
...,
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...},
{area: ??, btagCMVA: ??, btagCSVV2: ??, btagDeepB: ??, btagDeepC: ??, ...}]
----------------------------------------------------------------------------
backend: cpu
nbytes: unknown
type: 188 * Jet[
area: float32[parameters={"__doc__": "jet catchment area, for JECs", "typename": "float[]"}],
btagCMVA: float32[parameters={"__doc__": "CMVA V2 btag discriminator", "typename": "float[]"}],
btagCSVV2: float32[parameters={"__doc__": " pfCombinedInclusiveSecondaryVertexV2 b-tag discriminator (aka CSVV2)", "typename": "float[]"}],
btagDeepB: float32[parameters={"__doc__": "DeepCSV b+bb tag discriminator", "typename": "float[]"}],
btagDeepC: float32[parameters={"__doc__": "DeepCSV charm btag discriminator", "typename": "float[]"}],
btagDeepFlavB: float32[parameters={"__doc__": "DeepFlavour b+bb+lepb tag discriminator", "typename": "float[]"}],
btagDeepFlavC: float32[parameters={"__doc__": "DeepFlavour charm tag discriminator", "typename": "float[]"}],
chEmEF: float32[parameters={"__doc__": "charged Electromagnetic Energy Fraction", "typename": "float[]"}],
chHEF: float32[parameters={"__doc__": "charged Hadron Energy Fraction", "typename": "float[]"}],
eta: float32[parameters={"__doc__": "eta", "typename": "float[]"}],
...
parameters={"__doc__": "slimmedJets, i.e. ak4 PFJets CHS with JECs applied, after basic selection (pt > 15)", "collection_name": "Jet", "variation": "PtPhiSystematic-('pt', 'phi')-up"}]
```
```
jets_PtPhiSystematic_up_pt = awkward.flatten(jets.systematics.PtPhiSystematic.up.pt)
get_array(jets_PtPhiSystematic_up_pt)
```
```
[88.8,
50.2,
32.6,
19.3,
16.8,
116,
42.8,
28.5,
21.9,
20,
...,
24.3,
62.6,
59,
27.2,
23.8,
22.2,
16.7,
20.7,
20.1]
------
backend: cpu
nbytes: 752 B
type: 188 * float32
```
```
jets_PtPhiSystematic_up_phi = awkward.flatten(jets.systematics.PtPhiSystematic.up.phi)
get_array(jets_PtPhiSystematic_up_phi)
```
```
[-1.09,
1.98,
-3.43,
-2.77,
2.58,
-0.778,
-3.49,
2.69,
3.45,
2.13,
...,
2.54,
0.0636,
-3.63,
0.638,
0.462,
-3.23,
1.89,
3.14,
2.85]
--------
backend: cpu
nbytes: 752 B
type: 188 * float32
```
```
met_pt = met.pt
get_array(met_pt)
```
```
[25.9,
40.5,
38.7,
9.41,
10.9,
14.1,
4.82,
50.9,
39.7,
61.8,
...,
23.8,
45.1,
16.8,
13.1,
4.5,
82.1,
24.8,
24.2,
42.5]
------
backend: cpu
nbytes: 160 B
type: 40 * float32[parameters={"__doc__": "pt", "typename": "float"}]
```
```
met_PtScale_up = met.systematics.PtScale.up
get_array(met_PtScale_up)
```
```
[{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
...,
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...}]
----------------------------------------------------------------------
backend: cpu
nbytes: 1.8 kB
type: 40 * MissingET[
MetUnclustEnUpDeltaX: float32[parameters={"__doc__": "Delta (METx_mod-METx) Unclustered Energy Up", "typename": "float"}],
MetUnclustEnUpDeltaY: float32[parameters={"__doc__": "Delta (METy_mod-METy) Unclustered Energy Up", "typename": "float"}],
covXX: float32[parameters={"__doc__": "xx element of met covariance matrix", "typename": "float"}],
covXY: float32[parameters={"__doc__": "xy element of met covariance matrix", "typename": "float"}],
covYY: float32[parameters={"__doc__": "yy element of met covariance matrix", "typename": "float"}],
phi: float32[parameters={"__doc__": "phi", "typename": "float"}],
pt: float32,
significance: float32[parameters={"__doc__": "MET significance", "typename": "float"}],
sumEt: float32[parameters={"__doc__": "scalar sum of Et", "typename": "float"}],
fiducialGenPhi: float32[parameters={"__doc__": "phi", "typename": "float"}],
...
parameters={"collection_name": "MET", "variation": "PtScale-pt-up"}]
```
```
met_PtScale_up_pt = met.systematics.PtScale.up.pt
get_array(met_PtScale_up_pt)
```
```
[26.7,
41.7,
39.9,
9.69,
11.2,
14.5,
4.96,
52.4,
40.9,
63.6,
...,
24.5,
46.5,
17.3,
13.5,
4.63,
84.5,
25.6,
24.9,
43.8]
------
backend: cpu
nbytes: 160 B
type: 40 * float32
```
```
met_PtPhiSystematic_up = met.systematics.PtPhiSystematic.up
get_array(met_PtPhiSystematic_up)
```
```
[{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
...,
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...},
{MetUnclustEnUpDeltaX: ??, MetUnclustEnUpDeltaY: ??, covXX: ??, ...}]
----------------------------------------------------------------------
backend: cpu
nbytes: 1.8 kB
type: 40 * MissingET[
MetUnclustEnUpDeltaX: float32[parameters={"__doc__": "Delta (METx_mod-METx) Unclustered Energy Up", "typename": "float"}],
MetUnclustEnUpDeltaY: float32[parameters={"__doc__": "Delta (METy_mod-METy) Unclustered Energy Up", "typename": "float"}],
covXX: float32[parameters={"__doc__": "xx element of met covariance matrix", "typename": "float"}],
covXY: float32[parameters={"__doc__": "xy element of met covariance matrix", "typename": "float"}],
covYY: float32[parameters={"__doc__": "yy element of met covariance matrix", "typename": "float"}],
phi: float32,
pt: float32,
significance: float32[parameters={"__doc__": "MET significance", "typename": "float"}],
sumEt: float32[parameters={"__doc__": "scalar sum of Et", "typename": "float"}],
fiducialGenPhi: float32[parameters={"__doc__": "phi", "typename": "float"}],
...
parameters={"collection_name": "MET", "variation": "PtPhiSystematic-('pt', 'phi')-up"}]
```
```
met_PtPhiSystematic_up_pt = met.systematics.PtPhiSystematic.up.pt
get_array(met_PtPhiSystematic_up_pt)
```
```
[26.7,
41.7,
39.9,
9.69,
11.2,
14.5,
4.96,
52.4,
40.9,
63.6,
...,
24.5,
46.5,
17.3,
13.5,
4.63,
84.5,
25.6,
24.9,
43.8]
------
backend: cpu
nbytes: 160 B
type: 40 * float32
```
```
met_PtPhiSystematic_up_phi = met.systematics.PtPhiSystematic.up.phi
get_array(met_PtPhiSystematic_up_phi)
```
```
[1.75,
2.05,
-2.47,
3.01,
0.818,
-3.16,
-0.339,
-0.0646,
0.0881,
1.37,
...,
-0.541,
0.421,
0.818,
-1.82,
-2.36,
1.62,
-2.47,
-2.54,
-0.687]
---------
backend: cpu
nbytes: 160 B
type: 40 * float32
```
```
# TODO: Make it so that syst_muons.Y > X returns boolean values
# for all variations over Y.
# Requires some tracking of (pieces of) "what".
```
[previous
Packed Selection](packedselection.html)
[next
Processing and Scaling](processing.html)
[Show Source](../_sources/notebooks/systematics.ipynb.txt)
© Copyright 2025, Fermi National Accelerator Laboratory.
Created using [Sphinx](https://www.sphinx-doc.org/) 7.4.7.
Built with the [PyData Sphinx Theme](https://pydata-sphinx-theme.readthedocs.io/en/stable/index.html) 0.17.1.

2.3s · markdown via readability

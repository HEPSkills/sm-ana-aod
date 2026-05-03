Processing and Scaling — coffea 2026.4.1.dev3+gbfc8fd2cf.d20260501 documentation
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
* [Object systematics](systematics.html)
* Processing and Scaling
* [Jit compilation with Numba](advanced_numba.html)
* [Running inference tools](mltools.html)
* [Dataset discovery tools](dataset_discovery.html)
* [Dataset specification with FileSpec classes](filespec.html)
* [Coffea by Example](../examples.html)
* Processing and Scaling
# Processing and Scaling[#](#processing-and-scaling)
This is a rendered copy of [processing.ipynb](https://github.com/scikit-hep/coffea/blob/master/binder/processing.ipynb). You can optionally run it interactively on [binder at this link](https://mybinder.org/v2/gh/coffeateam/coffea/master?filepath=binder%2Fprocessing.ipynb)
Coffea relies mainly on [uproot](https://github.com/scikit-hep/uproot) to provide access to ROOT files for analysis.
As a usual analysis will involve processing tens to thousands of files, totalling gigabytes to terabytes of data, there is a certain amount of work to be done to build a parallelized framework to process the data in a reasonable amount of time.
Since the beginning a `coffea.processor` module was provided to encapsulate the core functionality of the analysis, which could be run locally or distributed via a number of Executors. This allowed users to worry just about the actual analysis code and not about how to implement efficient parallelization, assuming that the parallization is a trivial map-reduce operation (e.g. filling histograms and adding them together). This API ceased to exist for some time but we brought it back.
In coffa 202x (CalVer), you also have the option of deeper integration with `dask` (via `dask_awkward` and `uproot.dask`), and whether an analysis is to be executed on local or distributed resources, a TaskGraph encapsulating the analysis is created in this case. We will demonstrate how to use callable code to build these TGs.
We’ll always be showcasing both ways of using coffea to write and execute your analyis
Let’s start by writing a simple processor class that reads some CMS open data and plots a dimuon mass spectrum.
We’ll start by copying the [ProcessorABC](https://coffea-hep.readthedocs.io/en/latest/api/coffea.processor.ProcessorABC.html#coffea.processor.ProcessorABC) skeleton and filling in some details:
* Remove `flag`, as we won’t use it
* Adding a new histogram for $m\_{\mu \mu}$
* Building a [Candidate](https://coffea-hep.readthedocs.io/en/latest/api/coffea.nanoevents.methods.candidate.PtEtaPhiMCandidate.html#coffea.nanoevents.methods.candidate.PtEtaPhiMCandidate) record for muons, since we will read it with `BaseSchema` interpretation (the files used here could be read with `NanoAODSchema` but we want to show how to build vector objects from other TTree formats)
* Calculating the dimuon invariant mass
## File access[#](#file-access)
In the examples below, we will be using local copies of the files for speed but I have also left the eospublic xrtood urls for them in comments
## Coffea Processors[#](#coffea-processors)
```
import awkward as ak
import dask_awkward as dak
from coffea import processor
from coffea.nanoevents.methods import candidate
import hist
import hist.dask
import dask
class MyProcessor(processor.ProcessorABC):
def __init__(self, mode="virtual"):
assert mode in ["eager", "virtual", "dask"]
self._mode = mode
def process(self, events):
dataset = events.metadata["dataset"]
muons = ak.zip(
{
"pt": events.Muon_pt,
"eta": events.Muon_eta,
"phi": events.Muon_phi,
"mass": events.Muon_mass,
"charge": events.Muon_charge,
},
with_name="PtEtaPhiMCandidate",
behavior=candidate.behavior,
)
if self._mode == "dask":
hist_class = hist.dask.Hist
else:
hist_class = hist.Hist
h_mass = hist_class.new.StrCat(["opposite", "same"], name="sign").Log(1000, 0.2, 200.0, name="mass", label=r"$m_{\mu\mu}$ [GeV]").Int64()
cut = (ak.num(muons) == 2) & (ak.sum(muons.charge, axis=1) == 0)
# add first and second muon in every event together
dimuon = muons[cut][:, 0] + muons[cut][:, 1]
h_mass.fill(sign="opposite", mass=dimuon.mass)
cut = (ak.num(muons) == 2) & (ak.sum(muons.charge, axis=1) != 0)
dimuon = muons[cut][:, 0] + muons[cut][:, 1]
h_mass.fill(sign="same", mass=dimuon.mass)
if self._mode == "dask":
return {
"entries": ak.num(events, axis=0),
"mass": h_mass,
}
else:
return {
dataset: {
"entries": len(events),
"mass": h_mass,
}
}
def postprocess(self, accumulator):
pass
```
If we were to just use bare uproot to execute this processor, we could do that with the following example, which:
* Opens a CMS open data file
* Creates a NanoEvents object using `BaseSchema` (roughly equivalent to the output of reading with plain `uproot`)
* Creates a `MyProcessor` instance
* Runs the `process()` function, which returns our accumulators
```
from coffea.nanoevents import NanoEventsFactory, BaseSchema
import matplotlib.pyplot as plt
```
```
# filename = "root://eospublic.cern.ch//eos/root-eos/cms_opendata_2012_nanoaod/Run2012B_DoubleMuParked.root"
filename = "/Users/iason/work/pyhep_dev/uscms-idap-training/coffea/Run2012B_DoubleMuParked.root"
access_log = []
events = NanoEventsFactory.from_root(
{filename: "Events"},
entry_stop=500_000,
metadata={"dataset": "DoubleMuon"},
schemaclass=BaseSchema,
mode="virtual",
access_log=access_log,
).events()
p = MyProcessor("virtual")
```
```
%%time
out = p.process(events)
out
```
```
CPU times: user 178 ms, sys: 31.6 ms, total: 210 ms
Wall time: 280 ms
```
```
{'DoubleMuon': {'entries': 500000,
'mass': Hist(
StrCategory(['opposite', 'same'], name='sign'),
Regular(1000, 0.2, 200, transform=log, name='mass', label='$m_{\\mu\\mu}$ [GeV]'),
storage=Int64()) # Sum: 245435.0 (245753.0 with flow)}}
```
```
set(access_log)
```
```
{'Muon_charge', 'Muon_eta', 'Muon_mass', 'Muon_phi', 'Muon_pt'}
```
```
fig, ax = plt.subplots()
out["DoubleMuon"]["mass"].plot1d(ax=ax)
ax.set_xscale("log")
ax.legend(title="Dimuon charge")
plt.show()
```
```
# filename = "root://eospublic.cern.ch//eos/root-eos/cms_opendata_2012_nanoaod/Run2012B_DoubleMuParked.root"
filename = "/Users/iason/work/pyhep_dev/uscms-idap-training/coffea/Run2012B_DoubleMuParked.root"
events = NanoEventsFactory.from_root(
{filename: {"object_path": "Events", "steps": [[0, 500_000]]}},
metadata={"dataset": "DoubleMuon"},
schemaclass=BaseSchema,
mode="dask",
).events()
p = MyProcessor("dask")
taskgraph = p.process(events)
taskgraph
```
```
{'entries': dask.awkward,
'mass': Hist(
StrCategory(['opposite', 'same'], name='sign'),
Regular(1000, 0.2, 200, transform=log, name='mass', label='$m_{\\mu\\mu}$ [GeV]'),
storage=Int64()) # (has staged fills)}
```
```
dask.visualize(taskgraph, rankdir="LR", optimize_graph=False)
```
```
dask.visualize(taskgraph, rankdir="LR", optimize_graph=True)
```
```
%%time
(out,) = dask.compute(taskgraph)
out
```
```
CPU times: user 263 ms, sys: 38.9 ms, total: 302 ms
Wall time: 321 ms
```
```
{'entries': 500000,
'mass': Hist(
StrCategory(['opposite', 'same'], name='sign'),
Regular(1000, 0.2, 200, transform=log, name='mass', label='$m_{\\mu\\mu}$ [GeV]'),
storage=Int64()) # Sum: 245435.0 (245753.0 with flow)}
```
```
dak.necessary_columns(taskgraph)
```
```
{'from-uproot-ece94f13a30832ab46c00668ff6af4a8': frozenset({'Muon_charge',
'Muon_eta',
'Muon_mass',
'Muon_phi',
'Muon_pt'})}
```
```
fig, ax = plt.subplots()
out["mass"].plot1d(ax=ax)
ax.set_xscale("log")
ax.legend(title="Dimuon charge")
plt.show()
```
## Filesets[#](#filesets)
We’ll need to construct a fileset to run over
```
initial_fileset = {
"DoubleMuon": {
"files": {
"/Users/iason/work/pyhep_dev/uscms-idap-training/coffea/Run2012B_DoubleMuParked.root": "Events",
# "root://eospublic.cern.ch//eos/root-eos/cms_opendata_2012_nanoaod/Run2012B_DoubleMuParked.root": "Events",
},
"metadata": {
"is_mc": False,
},
},
"ZZ to 4mu": {
"files": {
"/Users/iason/work/pyhep_dev/uscms-idap-training/coffea/ZZTo4mu.root": "Events",
# "root://eospublic.cern.ch//eos/root-eos/cms_opendata_2012_nanoaod/ZZTo4mu.root": "Events",
},
"metadata": {
"is_mc": True,
},
},
}
```
## Processing with Virtual mode[#](#processing-with-virtual-mode)
Preprocessing is hidden inside this interface
```
%%time
iterative_run = processor.Runner(
executor=processor.IterativeExecutor(compression=None),
schema=BaseSchema,
maxchunks=3,
savemetrics=True,
)
out, metrics = iterative_run(
initial_fileset,
processor_instance=MyProcessor("virtual"),
)
```
```
Processing 100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 6/6 [ 0:00:00 < 0:00:00 | 11.6 chunk/s ]
```
```
CPU times: user 439 ms, sys: 78.1 ms, total: 517 ms
Wall time: 569 ms
```
```
out
```
```
{'DoubleMuon': {'entries': 300090,
'mass': Hist(
StrCategory(['opposite', 'same'], name='sign'),
Regular(1000, 0.2, 200, transform=log, name='mass', label='$m_{\\mu\\mu}$ [GeV]'),
storage=Int64()) # Sum: 146806.0 (147001.0 with flow)},
'ZZ to 4mu': {'entries': 299814,
'mass': Hist(
StrCategory(['opposite', 'same'], name='sign'),
Regular(1000, 0.2, 200, transform=log, name='mass', label='$m_{\\mu\\mu}$ [GeV]'),
storage=Int64()) # Sum: 57211.0 (57331.0 with flow)}}
```
```
fig, ax = plt.subplots()
out["DoubleMuon"]["mass"].plot1d(ax=ax)
ax.set_xscale("log")
ax.legend(title="Dimuon charge")
plt.show()
```
Now, if we want to use more than a single core on our machine, we simply change `IterativeExecutor` for `FuturesExecutor`, which uses the python `concurrent.futures` standard library. We can then set the most interesting argument to the `FuturesExecutor`: the number of cores to use.
```
%%time
futures_run = processor.Runner(
executor=processor.FuturesExecutor(workers=4, compression=None),
schema=BaseSchema,
savemetrics=True,
)
out, metrics = futures_run(initial_fileset, processor_instance=MyProcessor("virtual"))
```
```
Processing 100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 308/308 [ 0:00:07 < 0:00:00 | 48.6 chunk/s ]
Merging (local) 0% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1/308 [ 0:00:07 < -:--:-- | ? merges/s ]
```
```
CPU times: user 1.38 s, sys: 159 ms, total: 1.54 s
Wall time: 7.54 s
```
```
out
```
```
{'DoubleMuon': {'entries': 29308627,
'mass': Hist(
StrCategory(['opposite', 'same'], name='sign'),
Regular(1000, 0.2, 200, transform=log, name='mass', label='$m_{\\mu\\mu}$ [GeV]'),
storage=Int64()) # Sum: 14378856.0 (14397111.0 with flow)},
'ZZ to 4mu': {'entries': 1499064,
'mass': Hist(
StrCategory(['opposite', 'same'], name='sign'),
Regular(1000, 0.2, 200, transform=log, name='mass', label='$m_{\\mu\\mu}$ [GeV]'),
storage=Int64()) # Sum: 288707.0 (289326.0 with flow)}}
```
```
fig, ax = plt.subplots()
out["DoubleMuon"]["mass"].plot1d(ax=ax)
ax.set_xscale("log")
ax.legend(title="Dimuon charge")
plt.show()
```
In an analysis facility, all you need to do do scale your analysis, is connect to the facility’s dask cluster
```
from dask.distributed import Client
# here we connect to the cluster of our analysis facility.
# if you are on coffea-casa for example, that should be something like
# client = Client("tls://localhost:8786")
# locally we can make our own cluster though
from dask.distributed import LocalCluster
cluster = LocalCluster(threads_per_worker=1)
client = Client(cluster)
client
```
### Client
Client-40302046-b51d-11f0-82f3-aae91076e0c2
**Connection method:** Cluster object
**Cluster type:** distributed.LocalCluster
**Dashboard:** <http://127.0.0.1:8787/status>
### Cluster Info
### LocalCluster
4821f588
**Dashboard:** <http://127.0.0.1:8787/status>
**Workers:** 14
**Total threads:** 14
**Total memory:** 36.00 GiB
**Status:** running
**Using processes:** True
### Scheduler Info
### Scheduler
Scheduler-5624041c-9ad4-43d0-81c0-ce9adac70d58
**Comm:** tcp://127.0.0.1:56079
**Workers:** 14
**Dashboard:** <http://127.0.0.1:8787/status>
**Total threads:** 14
**Started:** Just now
**Total memory:** 36.00 GiB
### Workers
#### Worker: 0
**Comm:** tcp://127.0.0.1:56113
**Total threads:** 1
**Dashboard:** <http://127.0.0.1:56114/status>
**Memory:** 2.57 GiB
**Nanny:** tcp://127.0.0.1:56082
**Local directory:** /var/folders/2c/94kt72fs0\_q\_9nzr2y5jphb00000gn/T/dask-scratch-space/worker-tku6bjgv
#### Worker: 1
**Comm:** tcp://127.0.0.1:56110
**Total threads:** 1
**Dashboard:** <http://127.0.0.1:56111/status>
**Memory:** 2.57 GiB
**Nanny:** tcp://127.0.0.1:56084
**Local directory:** /var/folders/2c/94kt72fs0\_q\_9nzr2y5jphb00000gn/T/dask-scratch-space/worker-7rskj1y2
#### Worker: 2
**Comm:** tcp://127.0.0.1:56116
**Total threads:** 1
**Dashboard:** <http://127.0.0.1:56117/status>
**Memory:** 2.57 GiB
**Nanny:** tcp://127.0.0.1:56086
**Local directory:** /var/folders/2c/94kt72fs0\_q\_9nzr2y5jphb00000gn/T/dask-scratch-space/worker-inmnzm0i
#### Worker: 3
**Comm:** tcp://127.0.0.1:56124
**Total threads:** 1
**Dashboard:** <http://127.0.0.1:56125/status>
**Memory:** 2.57 GiB
**Nanny:** tcp://127.0.0.1:56088
**Local directory:** /var/folders/2c/94kt72fs0\_q\_9nzr2y5jphb00000gn/T/dask-scratch-space/worker-si0ii2ks
#### Worker: 4
**Comm:** tcp://127.0.0.1:56128
**Total threads:** 1
**Dashboard:** <http://127.0.0.1:56129/status>
**Memory:** 2.57 GiB
**Nanny:** tcp://127.0.0.1:56090
**Local directory:** /var/folders/2c/94kt72fs0\_q\_9nzr2y5jphb00000gn/T/dask-scratch-space/worker-lki3yuxs
#### Worker: 5
**Comm:** tcp://127.0.0.1:56119
**Total threads:** 1
**Dashboard:** <http://127.0.0.1:56120/status>
**Memory:** 2.57 GiB
**Nanny:** tcp://127.0.0.1:56092
**Local directory:** /var/folders/2c/94kt72fs0\_q\_9nzr2y5jphb00000gn/T/dask-scratch-space/worker-tj\_akctt
#### Worker: 6
**Comm:** tcp://127.0.0.1:56131
**Total threads:** 1
**Dashboard:** <http://127.0.0.1:56132/status>
**Memory:** 2.57 GiB
**Nanny:** tcp://127.0.0.1:56094
**Local directory:** /var/folders/2c/94kt72fs0\_q\_9nzr2y5jphb00000gn/T/dask-scratch-space/worker-nbh\_9dhd
#### Worker: 7
**Comm:** tcp://127.0.0.1:56134
**Total threads:** 1
**Dashboard:** <http://127.0.0.1:56135/status>
**Memory:** 2.57 GiB
**Nanny:** tcp://127.0.0.1:56096
**Local directory:** /var/folders/2c/94kt72fs0\_q\_9nzr2y5jphb00000gn/T/dask-scratch-space/worker-hja2ri7k
#### Worker: 8
**Comm:** tcp://127.0.0.1:56138
**Total threads:** 1
**Dashboard:** <http://127.0.0.1:56141/status>
**Memory:** 2.57 GiB
**Nanny:** tcp://127.0.0.1:56098
**Local directory:** /var/folders/2c/94kt72fs0\_q\_9nzr2y5jphb00000gn/T/dask-scratch-space/worker-oosdwo6a
#### Worker: 9
**Comm:** tcp://127.0.0.1:56149
**Total threads:** 1
**Dashboard:** <http://127.0.0.1:56151/status>
**Memory:** 2.57 GiB
**Nanny:** tcp://127.0.0.1:56100
**Local directory:** /var/folders/2c/94kt72fs0\_q\_9nzr2y5jphb00000gn/T/dask-scratch-space/worker-sxl5w0rr
#### Worker: 10
**Comm:** tcp://127.0.0.1:56144
**Total threads:** 1
**Dashboard:** <http://127.0.0.1:56145/status>
**Memory:** 2.57 GiB
**Nanny:** tcp://127.0.0.1:56102
**Local directory:** /var/folders/2c/94kt72fs0\_q\_9nzr2y5jphb00000gn/T/dask-scratch-space/worker-k6qo6zft
#### Worker: 11
**Comm:** tcp://127.0.0.1:56143
**Total threads:** 1
**Dashboard:** <http://127.0.0.1:56146/status>
**Memory:** 2.57 GiB
**Nanny:** tcp://127.0.0.1:56104
**Local directory:** /var/folders/2c/94kt72fs0\_q\_9nzr2y5jphb00000gn/T/dask-scratch-space/worker-e8bf4qh1
#### Worker: 12
**Comm:** tcp://127.0.0.1:56137
**Total threads:** 1
**Dashboard:** <http://127.0.0.1:56139/status>
**Memory:** 2.57 GiB
**Nanny:** tcp://127.0.0.1:56106
**Local directory:** /var/folders/2c/94kt72fs0\_q\_9nzr2y5jphb00000gn/T/dask-scratch-space/worker-vn88bsqk
#### Worker: 13
**Comm:** tcp://127.0.0.1:56150
**Total threads:** 1
**Dashboard:** <http://127.0.0.1:56153/status>
**Memory:** 2.57 GiB
**Nanny:** tcp://127.0.0.1:56108
**Local directory:** /var/folders/2c/94kt72fs0\_q\_9nzr2y5jphb00000gn/T/dask-scratch-space/worker-\_am04ody
```
%%time
dask_run = processor.Runner(
executor=processor.DaskExecutor(client=client, compression=None),
schema=BaseSchema,
chunksize=100_000,
skipbadfiles=True,
savemetrics=True,
)
out, metrics = dask_run(initial_fileset, processor_instance=MyProcessor("virtual"))
```
```
Processing 100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 326/326 [ 0:00:03 < 0:00:00 | 89.5 chunk/s ]
```
```
CPU times: user 740 ms, sys: 166 ms, total: 905 ms
Wall time: 3.84 s
```
```
out
```
```
{'DoubleMuon': {'entries': 29308627,
'mass': Hist(
StrCategory(['opposite', 'same'], name='sign'),
Regular(1000, 0.2, 200, transform=log, name='mass', label='$m_{\\mu\\mu}$ [GeV]'),
storage=Int64()) # Sum: 14378856.0 (14397111.0 with flow)},
'ZZ to 4mu': {'entries': 1499064,
'mass': Hist(
StrCategory(['opposite', 'same'], name='sign'),
Regular(1000, 0.2, 200, transform=log, name='mass', label='$m_{\\mu\\mu}$ [GeV]'),
storage=Int64()) # Sum: 288707.0 (289326.0 with flow)}}
```
```
fig, ax = plt.subplots()
out["DoubleMuon"]["mass"].plot1d(ax=ax)
ax.set_xscale("log")
ax.legend(title="Dimuon charge")
plt.show()
```
## Processing with Dask mode[#](#processing-with-dask-mode)
### Preprocessing[#](#preprocessing)
There are dataset discovery tools inside of coffea to help construct such datasets. Those will not be demonstrated here. For now, we’ll take the above `initial_fileset` and preprocess it.
```
from coffea.dataset_tools import apply_to_fileset, max_chunks, max_files, preprocess
```
```
preprocessed_available, preprocessed_total = preprocess(
initial_fileset,
step_size=100_000,
align_clusters=False,
skip_bad_files=True,
recalculate_steps=False,
files_per_batch=1,
file_exceptions=(OSError,),
save_form=False,
uproot_options={},
step_size_safety_factor=0.5,
)
```
### Preprocessed fileset[#](#preprocessed-fileset)
Lets have a look at the contents of the preprocessed\_available part of the fileset
```
preprocessed_available
```
```
{'DoubleMuon': {'files': {'/Users/iason/work/pyhep_dev/uscms-idap-training/coffea/Run2012B_DoubleMuParked.root': {'object_path': 'Events',
'steps': [[0, 100030],
[100030, 200060],
[200060, 300090],
[300090, 400120],
[400120, 500150],
[500150, 600180],
[600180, 700210],
[700210, 800240],
[800240, 900270],
[900270, 1000300],
[1000300, 1100330],
[1100330, 1200360],
[1200360, 1300390],
[1300390, 1400420],
[1400420, 1500450],
[1500450, 1600480],
[1600480, 1700510],
[1700510, 1800540],
[1800540, 1900570],
[1900570, 2000600],
[2000600, 2100630],
[2100630, 2200660],
[2200660, 2300690],
[2300690, 2400720],
[2400720, 2500750],
[2500750, 2600780],
[2600780, 2700810],
[2700810, 2800840],
[2800840, 2900870],
[2900870, 3000900],
[3000900, 3100930],
[3100930, 3200960],
[3200960, 3300990],
[3300990, 3401020],
[3401020, 3501050],
[3501050, 3601080],
[3601080, 3701110],
[3701110, 3801140],
[3801140, 3901170],
[3901170, 4001200],
[4001200, 4101230],
[4101230, 4201260],
[4201260, 4301290],
[4301290, 4401320],
[4401320, 4501350],
[4501350, 4601380],
[4601380, 4701410],
[4701410, 4801440],
[4801440, 4901470],
[4901470, 5001500],
[5001500, 5101530],
[5101530, 5201560],
[5201560, 5301590],
[5301590, 5401620],
[5401620, 5501650],
[5501650, 5601680],
[5601680, 5701710],
[5701710, 5801740],
[5801740, 5901770],
[5901770, 6001800],
[6001800, 6101830],
[6101830, 6201860],
[6201860, 6301890],
[6301890, 6401920],
[6401920, 6501950],
[6501950, 6601980],
[6601980, 6702010],
[6702010, 6802040],
[6802040, 6902070],
[6902070, 7002100],
[7002100, 7102130],
[7102130, 7202160],
[7202160, 7302190],
[7302190, 7402220],
[7402220, 7502250],
[7502250, 7602280],
[7602280, 7702310],
[7702310, 7802340],
[7802340, 7902370],
[7902370, 8002400],
[8002400, 8102430],
[8102430, 8202460],
[8202460, 8302490],
[8302490, 8402520],
[8402520, 8502550],
[8502550, 8602580],
[8602580, 8702610],
[8702610, 8802640],
[8802640, 8902670],
[8902670, 9002700],
[9002700, 9102730],
[9102730, 9202760],
[9202760, 9302790],
[9302790, 9402820],
[9402820, 9502850],
[9502850, 9602880],
[9602880, 9702910],
[9702910, 9802940],
[9802940, 9902970],
[9902970, 10003000],
[10003000, 10103030],
[10103030, 10203060],
[10203060, 10303090],
[10303090, 10403120],
[10403120, 10503150],
[10503150, 10603180],
[10603180, 10703210],
[10703210, 10803240],
[10803240, 10903270],
[10903270, 11003300],
[11003300, 11103330],
[11103330, 11203360],
[11203360, 11303390],
[11303390, 11403420],
[11403420, 11503450],
[11503450, 11603480],
[11603480, 11703510],
[11703510, 11803540],
[11803540, 11903570],
[11903570, 12003600],
[12003600, 12103630],
[12103630, 12203660],
[12203660, 12303690],
[12303690, 12403720],
[12403720, 12503750],
[12503750, 12603780],
[12603780, 12703810],
[12703810, 12803840],
[12803840, 12903870],
[12903870, 13003900],
[13003900, 13103930],
[13103930, 13203960],
[13203960, 13303990],
[13303990, 13404020],
[13404020, 13504050],
[13504050, 13604080],
[13604080, 13704110],
[13704110, 13804140],
[13804140, 13904170],
[13904170, 14004200],
[14004200, 14104230],
[14104230, 14204260],
[14204260, 14304290],
[14304290, 14404320],
[14404320, 14504350],
[14504350, 14604380],
[14604380, 14704410],
[14704410, 14804440],
[14804440, 14904470],
[14904470, 15004500],
[15004500, 15104530],
[15104530, 15204560],
[15204560, 15304590],
[15304590, 15404620],
[15404620, 15504650],
[15504650, 15604680],
[15604680, 15704710],
[15704710, 15804740],
[15804740, 15904770],
[15904770, 16004800],
[16004800, 16104830],
[16104830, 16204860],
[16204860, 16304890],
[16304890, 16404920],
[16404920, 16504950],
[16504950, 16604980],
[16604980, 16705010],
[16705010, 16805040],
[16805040, 16905070],
[16905070, 17005100],
[17005100, 17105130],
[17105130, 17205160],
[17205160, 17305190],
[17305190, 17405220],
[17405220, 17505250],
[17505250, 17605280],
[17605280, 17705310],
[17705310, 17805340],
[17805340, 17905370],
[17905370, 18005400],
[18005400, 18105430],
[18105430, 18205460],
[18205460, 18305490],
[18305490, 18405520],
[18405520, 18505550],
[18505550, 18605580],
[18605580, 18705610],
[18705610, 18805640],
[18805640, 18905670],
[18905670, 19005700],
[19005700, 19105730],
[19105730, 19205760],
[19205760, 19305790],
[19305790, 19405820],
[19405820, 19505850],
[19505850, 19605880],
[19605880, 19705910],
[19705910, 19805940],
[19805940, 19905970],
[19905970, 20006000],
[20006000, 20106030],
[20106030, 20206060],
[20206060, 20306090],
[20306090, 20406120],
[20406120, 20506150],
[20506150, 20606180],
[20606180, 20706210],
[20706210, 20806240],
[20806240, 20906270],
[20906270, 21006300],
[21006300, 21106330],
[21106330, 21206360],
[21206360, 21306390],
[21306390, 21406420],
[21406420, 21506450],
[21506450, 21606480],
[21606480, 21706510],
[21706510, 21806540],
[21806540, 21906570],
[21906570, 22006600],
[22006600, 22106630],
[22106630, 22206660],
[22206660, 22306690],
[22306690, 22406720],
[22406720, 22506750],
[22506750, 22606780],
[22606780, 22706810],
[22706810, 22806840],
[22806840, 22906870],
[22906870, 23006900],
[23006900, 23106930],
[23106930, 23206960],
[23206960, 23306990],
[23306990, 23407020],
[23407020, 23507050],
[23507050, 23607080],
[23607080, 23707110],
[23707110, 23807140],
[23807140, 23907170],
[23907170, 24007200],
[24007200, 24107230],
[24107230, 24207260],
[24207260, 24307290],
[24307290, 24407320],
[24407320, 24507350],
[24507350, 24607380],
[24607380, 24707410],
[24707410, 24807440],
[24807440, 24907470],
[24907470, 25007500],
[25007500, 25107530],
[25107530, 25207560],
[25207560, 25307590],
[25307590, 25407620],
[25407620, 25507650],
[25507650, 25607680],
[25607680, 25707710],
[25707710, 25807740],
[25807740, 25907770],
[25907770, 26007800],
[26007800, 26107830],
[26107830, 26207860],
[26207860, 26307890],
[26307890, 26407920],
[26407920, 26507950],
[26507950, 26607980],
[26607980, 26708010],
[26708010, 26808040],
[26808040, 26908070],
[26908070, 27008100],
[27008100, 27108130],
[27108130, 27208160],
[27208160, 27308190],
[27308190, 27408220],
[27408220, 27508250],
[27508250, 27608280],
[27608280, 27708310],
[27708310, 27808340],
[27808340, 27908370],
[27908370, 28008400],
[28008400, 28108430],
[28108430, 28208460],
[28208460, 28308490],
[28308490, 28408520],
[28408520, 28508550],
[28508550, 28608580],
[28608580, 28708610],
[28708610, 28808640],
[28808640, 28908670],
[28908670, 29008700],
[29008700, 29108730],
[29108730, 29208760],
[29208760, 29308627]],
'num_entries': 29308627,
'uuid': '7a4da368-cfd1-11e8-9717-97650d81beef'}},
'metadata': {'is_mc': False},
'form': None},
'ZZ to 4mu': {'files': {'/Users/iason/work/pyhep_dev/uscms-idap-training/coffea/ZZTo4mu.root': {'object_path': 'Events',
'steps': [[0, 99938],
[99938, 199876],
[199876, 299814],
[299814, 399752],
[399752, 499690],
[499690, 599628],
[599628, 699566],
[699566, 799504],
[799504, 899442],
[899442, 999380],
[999380, 1099318],
[1099318, 1199256],
[1199256, 1299194],
[1299194, 1399132],
[1399132, 1499064]],
'num_entries': 1499064,
'uuid': '9fb6f85c-cfd1-11e8-9717-97650d81beef'}},
'metadata': {'is_mc': True},
'form': None}}
```
### Saving a preprocessed fileset[#](#saving-a-preprocessed-fileset)
We can use the gzip, pickle, and json modules/libraries to both save and reload datasets directly. We’ll do this short example below
```
import gzip
import json
output_file = "example_fileset"
with gzip.open(f"{output_file}_available.json.gz", "wt") as file:
json.dump(preprocessed_available, file, indent=2)
print(f"Saved available fileset chunks to {output_file}_available.json.gz")
with gzip.open(f"{output_file}_all.json.gz", "wt") as file:
json.dump(preprocessed_total, file, indent=2)
print(f"Saved complete fileset chunks to {output_file}_all.json.gz")
```
```
Saved available fileset chunks to example_fileset_available.json.gz
Saved complete fileset chunks to example_fileset_all.json.gz
```
We could then reload these filesets and quickly pick up where we left off. Often we’ll want to preprocess again “soon” before analyzing data because this will let us catch which files are accessible now and which are not. The saved filesets may be useful for tracking, and we may have enough stability to reuse it for some period of time.
```
with gzip.open(f"{output_file}_available.json.gz", "rt") as file:
reloaded_available = json.load(file)
with gzip.open(f"{output_file}_all.json.gz", "rt") as file:
reloaded_all = json.load(file)
```
### Slicing chunks and files[#](#slicing-chunks-and-files)
Given this preprocessed fileset, we can test our processor on just a few chunks of a handful of files. To do this, we use the max\_files and max\_chunks functions from the dataset tools
```
test_preprocessed_files = max_files(preprocessed_available, 1)
test_preprocessed = max_chunks(test_preprocessed_files, 3)
```
```
test_preprocessed
```
```
{'DoubleMuon': {'files': {'/Users/iason/work/pyhep_dev/uscms-idap-training/coffea/Run2012B_DoubleMuParked.root': {'object_path': 'Events',
'steps': [[0, 100030], [100030, 200060], [200060, 300090]],
'num_entries': 29308627,
'uuid': '7a4da368-cfd1-11e8-9717-97650d81beef'}},
'metadata': {'is_mc': False},
'form': None},
'ZZ to 4mu': {'files': {'/Users/iason/work/pyhep_dev/uscms-idap-training/coffea/ZZTo4mu.root': {'object_path': 'Events',
'steps': [[0, 99938], [99938, 199876], [199876, 299814]],
'num_entries': 1499064,
'uuid': '9fb6f85c-cfd1-11e8-9717-97650d81beef'}},
'metadata': {'is_mc': True},
'form': None}}
```
```
small_tg, small_rep = apply_to_fileset(
data_manipulation=MyProcessor("dask"),
fileset=test_preprocessed,
schemaclass=BaseSchema,
uproot_options={"allow_read_errors_with_report": (OSError, ValueError)},
)
```
```
dask.visualize(small_tg, optimize_graph=True)
```
```
%%time
small_computed, small_rep_computed = dask.compute(small_tg, small_rep)
```
```
CPU times: user 121 ms, sys: 14.5 ms, total: 135 ms
Wall time: 241 ms
```
```
small_rep_computed["DoubleMuon"]
```
```
[{call_time: None, duration: 0.0405, performance_counters: {...}, ...},
{call_time: None, duration: 0.0882, performance_counters: {...}, ...},
{call_time: None, duration: 0.06, performance_counters: {...}, args: ..., ...}]
--------------------------------------------------------------------------------
backend: cpu
nbytes: 730 B
type: 3 * {
call_time: ?unknown,
duration: float64,
performance_counters: {
num_requested_bytes: int64,
num_requests: int64,
num_requested_chunks: int64
},
args: var * string,
kwargs: var * unknown,
exception: ?unknown,
...
}
```
```
small_computed
```
```
{'DoubleMuon': {'entries': 300090,
'mass': Hist(
StrCategory(['opposite', 'same'], name='sign'),
Regular(1000, 0.2, 200, transform=log, name='mass', label='$m_{\\mu\\mu}$ [GeV]'),
storage=Int64()) # Sum: 146806.0 (147001.0 with flow)},
'ZZ to 4mu': {'entries': 299814,
'mass': Hist(
StrCategory(['opposite', 'same'], name='sign'),
Regular(1000, 0.2, 200, transform=log, name='mass', label='$m_{\\mu\\mu}$ [GeV]'),
storage=Int64()) # Sum: 57211.0 (57331.0 with flow)}}
```
```
fig, ax = plt.subplots()
small_computed["DoubleMuon"]["mass"].plot1d(ax=ax)
ax.set_xscale("log")
ax.legend(title="Dimuon charge")
plt.show()
```
```
full_tg, rep = apply_to_fileset(
data_manipulation=MyProcessor("dask"),
fileset=preprocessed_available,
schemaclass=BaseSchema,
uproot_options={"allow_read_errors_with_report": (OSError, ValueError)},
)
```
Dask automatically uses a client if there is one alive to compute. If you haven’t destroyed the `client/cluster` above, this computation will use it. Look at the dask docs about how to configure computation.
```
%%time
out, rep = dask.compute(full_tg, rep)
```
```
CPU times: user 2 s, sys: 152 ms, total: 2.15 s
Wall time: 3.08 s
```
```
out
```
```
{'DoubleMuon': {'entries': 29308627,
'mass': Hist(
StrCategory(['opposite', 'same'], name='sign'),
Regular(1000, 0.2, 200, transform=log, name='mass', label='$m_{\\mu\\mu}$ [GeV]'),
storage=Int64()) # Sum: 14378856.0 (14397111.0 with flow)},
'ZZ to 4mu': {'entries': 1499064,
'mass': Hist(
StrCategory(['opposite', 'same'], name='sign'),
Regular(1000, 0.2, 200, transform=log, name='mass', label='$m_{\\mu\\mu}$ [GeV]'),
storage=Int64()) # Sum: 288707.0 (289326.0 with flow)}}
```
```
fig, ax = plt.subplots()
out["DoubleMuon"]["mass"].plot1d(ax=ax)
ax.set_xscale("log")
ax.legend(title="Dimuon charge")
plt.show()
```
[previous
Object systematics](systematics.html)
[next
Jit compilation with Numba](advanced_numba.html)
On this page
* [File access](#file-access)
* [Coffea Processors](#coffea-processors)
* [Filesets](#filesets)
* [Processing with Virtual mode](#processing-with-virtual-mode)
* [Processing with Dask mode](#processing-with-dask-mode)
+ [Preprocessing](#preprocessing)
+ [Preprocessed fileset](#preprocessed-fileset)
+ [Saving a preprocessed fileset](#saving-a-preprocessed-fileset)
+ [Slicing chunks and files](#slicing-chunks-and-files)
[Show Source](../_sources/notebooks/processing.ipynb.txt)
© Copyright 2025, Fermi National Accelerator Laboratory.
Created using [Sphinx](https://www.sphinx-doc.org/) 7.4.7.
Built with the [PyData Sphinx Theme](https://pydata-sphinx-theme.readthedocs.io/en/stable/index.html) 0.17.1.

2.6s · markdown via readability

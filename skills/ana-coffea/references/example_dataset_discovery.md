Dataset discovery tools — coffea 2026.4.1.dev3+gbfc8fd2cf.d20260501 documentation
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
* [Processing and Scaling](processing.html)
* [Jit compilation with Numba](advanced_numba.html)
* [Running inference tools](mltools.html)
* Dataset discovery tools
* [Dataset specification with FileSpec classes](filespec.html)
* [Coffea by Example](../examples.html)
* Dataset discovery tools
# Dataset discovery tools[#](#dataset-discovery-tools)
This is a rendered copy of [dataset\_discovery.ipynb](https://github.com/scikit-hep/coffea/blob/master/binder/dataset_discovery.ipynb). You can optionally run it interactively on [binder at this link](https://mybinder.org/v2/gh/coffeateam/coffea/master?filepath=binder%2Fdataset_discovery.ipynb)
This notebook shows some features to make the dataset discovery for CMS analysis easier.
The rucio sytem is queried to look for dataset and access to the list of all available file replicas.
Users can exploit these tools at 2 different levels:
* low level: use the `rucio_utils` module directly to just query rucio
* high level: use the `DataDiscoveryCLI` class to simplify dataset query, replicas filters and uproot preprocessing with dask
## Using Rucio utils directly[#](#using-rucio-utils-directly)
```
from coffea.dataset_tools import rucio_utils
from coffea.dataset_tools.dataset_query import print_dataset_query
from coffea.util import coffea_console
from rich.table import Table
```
```
client = rucio_utils.get_rucio_client()
client
```
```
```
```
query = "/TTToSemiLeptonic_*_13TeV-powheg-pythia8/RunIISummer20UL18NanoAODv9*/NANOAODSIM"
```
```
outlist, outtree = rucio_utils.query_dataset(
query,
client=client,
tree=True,
scope="cms",
)
outlist[1:5]
```
```
['/TTToSemiLeptonic_TuneCP5CR1_erdON_13TeV-powheg-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM',
'/TTToSemiLeptonic_TuneCP5CR2_13TeV-powheg-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v2/NANOAODSIM',
'/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM',
'/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/RunIISummer20UL18NanoAODv9-20UL18JMENano_106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM']
```
Let’s now pretty-print the results in a table using an utility function in the `dataset_query` module.
```
print_dataset_query(query, outtree)
```
```
Query: /TTToSemiLeptonic_*_13TeV-powheg-pythia8/RunIISummer20UL18NanoAODv9*/NANOAODSIM
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳┓
┃ Name ┃ Tag ┃┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇┩
│ TTToSemiLeptonic_TuneCP5CR1_13Te… │ (1) RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v2/NAN… ││
├───────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┼┤
│ TTToSemiLeptonic_TuneCP5CR1_erdO… │ (2) RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NAN… ││
├───────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┼┤
│ TTToSemiLeptonic_TuneCP5CR2_13Te… │ (3) RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v2/NAN… ││
├───────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┼┤
│ TTToSemiLeptonic_TuneCP5_13TeV-p… │ (4) RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NAN… ││
│ │ (5) RunIISummer20UL18NanoAODv9-20UL18JMENano_106X_upgrade2018_realistic_v… ││
│ │ (6) RunIISummer20UL18NanoAODv9-PUForMUOVal_106X_upgrade2018_realistic_v16… ││
│ │ (7) RunIISummer20UL18NanoAODv9-PUForTRK_TRK_106X_upgrade2018_realistic_v1… ││
│ │ (8) RunIISummer20UL18NanoAODv9-PUForTRKv2_TRKv2_106X_upgrade2018_realisti… ││
├───────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┼┤
│ TTToSemiLeptonic_TuneCP5_erdON_1… │ (9) RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NAN… ││
├───────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┼┤
│ TTToSemiLeptonic_TuneCP5down_13T… │ (10) RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NA… ││
├───────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┼┤
│ TTToSemiLeptonic_TuneCP5up_13TeV… │ (11) RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NA… ││
├───────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┼┤
│ TTToSemiLeptonic_Vcb_TuneCP5_13T… │ (12) RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v2/NA… ││
├───────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┼┤
│ TTToSemiLeptonic_hdampDOWN_TuneC… │ (13) RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NA… ││
├───────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┼┤
│ TTToSemiLeptonic_hdampUP_TuneCP5… │ (14) RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NA… ││
├───────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┼┤
│ TTToSemiLeptonic_mtop166p5_TuneC… │ (15) RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NA… ││
├───────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┼┤
│ TTToSemiLeptonic_mtop169p5_TuneC… │ (16) RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NA… ││
├───────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┼┤
│ TTToSemiLeptonic_mtop171p5_TuneC… │ (17) RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NA… ││
├───────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┼┤
│ TTToSemiLeptonic_mtop173p5_TuneC… │ (18) RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NA… ││
├───────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┼┤
│ TTToSemiLeptonic_mtop175p5_TuneC… │ (19) RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NA… ││
├───────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┼┤
│ TTToSemiLeptonic_mtop178p5_TuneC… │ (20) RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NA… ││
├───────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┼┤
│ TTToSemiLeptonic_widthx0p55_Tune… │ (21) RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NA… ││
├───────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┼┤
│ TTToSemiLeptonic_widthx0p7_TuneC… │ (22) RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NA… ││
├───────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┼┤
│ TTToSemiLeptonic_widthx0p85_Tune… │ (23) RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NA… ││
├───────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┼┤
│ TTToSemiLeptonic_widthx1p15_Tune… │ (24) RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NA… ││
├───────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┼┤
│ TTToSemiLeptonic_widthx1p3_TuneC… │ (25) RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NA… ││
├───────────────────────────────────┼────────────────────────────────────────────────────────────────────────────┼┤
│ TTToSemiLeptonic_widthx1p45_Tune… │ (26) RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NA… ││
└───────────────────────────────────┴────────────────────────────────────────────────────────────────────────────┴┘
```
### Dataset replicas[#](#dataset-replicas)
Let’s select one dataset and look for available replicas
```
dataset = outlist[0]
dataset
```
```
'/TTToSemiLeptonic_TuneCP5CR1_13TeV-powheg-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v2/NANOAODSIM'
```
Using the option `mode='full'` in the function `rucio_utils.get_dataset_file_replicas()` one gets all the available replicas.
```
try:
(
outfiles,
outsites,
sites_counts,
) = rucio_utils.get_dataset_files_replicas(
dataset,
allowlist_sites=[],
blocklist_sites=[],
regex_sites=[],
mode="full", # full or first. "full"==all the available replicas
client=client,
)
except Exception as e:
print(f"\n[red bold] Exception: {e}[/]")
```
```
def print_replicas(sites_counts):
coffea_console.print(f"[cyan]Sites availability for dataset: [red]{dataset}")
table = Table(title="Available replicas")
table.add_column("Index", justify="center")
table.add_column("Site", justify="left", style="cyan", no_wrap=True)
table.add_column("Files", style="magenta", no_wrap=True)
table.add_column("Availability", justify="center")
table.row_styles = ["dim", "none"]
Nfiles = len(outfiles)
sorted_sites = dict(sorted(sites_counts.items(), key=lambda x: x[1], reverse=True))
for i, (site, stat) in enumerate(sorted_sites.items()):
table.add_row(str(i), site, f"{stat} / {Nfiles}", f"{stat * 100 / Nfiles:.1f}%")
coffea_console.print(table)
```
```
print_replicas(sites_counts)
```
```
Sites availability for dataset:
/TTToSemiLeptonic_TuneCP5CR1_13TeV-powheg-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v2
/NANOAODSIM
```
```
Available replicas
┏━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Index ┃ Site ┃ Files ┃ Availability ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ 0 │ T2_DE_DESY │ 294 / 294 │ 100.0% │
│ 1 │ T1_DE_KIT_Disk │ 294 / 294 │ 100.0% │
│ 2 │ T1_UK_RAL_Disk │ 294 / 294 │ 100.0% │
│ 3 │ T1_RU_JINR_Disk │ 294 / 294 │ 100.0% │
│ 4 │ T3_CH_PSI │ 294 / 294 │ 100.0% │
│ 5 │ T3_KR_UOS │ 294 / 294 │ 100.0% │
│ 6 │ T1_US_FNAL_Disk │ 193 / 294 │ 65.6% │
│ 7 │ T2_US_Nebraska │ 99 / 294 │ 33.7% │
│ 8 │ T1_IT_CNAF_Disk │ 58 / 294 │ 19.7% │
│ 9 │ T2_US_Purdue │ 53 / 294 │ 18.0% │
│ 10 │ T2_BE_IIHE │ 50 / 294 │ 17.0% │
│ 11 │ T2_US_MIT │ 50 / 294 │ 17.0% │
│ 12 │ T1_ES_PIC_Disk │ 43 / 294 │ 14.6% │
│ 13 │ T2_US_Vanderbilt │ 40 / 294 │ 13.6% │
│ 14 │ T2_BR_SPRACE │ 39 / 294 │ 13.3% │
│ 15 │ T2_US_Florida │ 33 / 294 │ 11.2% │
│ 16 │ T2_IT_Legnaro │ 28 / 294 │ 9.5% │
│ 17 │ T2_US_UCSD │ 28 / 294 │ 9.5% │
│ 18 │ T2_UA_KIPT │ 26 / 294 │ 8.8% │
│ 19 │ T2_US_Caltech │ 24 / 294 │ 8.2% │
│ 20 │ T2_US_Wisconsin │ 22 / 294 │ 7.5% │
│ 21 │ T2_TR_METU │ 18 / 294 │ 6.1% │
│ 22 │ T2_ES_CIEMAT │ 17 / 294 │ 5.8% │
│ 23 │ T2_DE_RWTH │ 11 / 294 │ 3.7% │
│ 24 │ T2_BR_UERJ │ 7 / 294 │ 2.4% │
│ 25 │ T2_UK_SGrid_Bristol │ 3 / 294 │ 1.0% │
│ 26 │ T2_ES_IFCA │ 2 / 294 │ 0.7% │
└───────┴─────────────────────┴───────────┴──────────────┘
```
### Filtering sites[#](#filtering-sites)
Grid sites can be filtered in 3 different ways
* **allowlist**: if this list of specified, only the sites in the list are considered. No blocklist and regex are considered
* **blocklist**: if this list is specified, those sites are excluded from the replicas
* **regex\_sites**: regex filter the sites to be considered, on top of the blocklist
```
# Example with allowlist
try:
(
outfiles,
outsites,
sites_counts,
) = rucio_utils.get_dataset_files_replicas(
dataset,
allowlist_sites=["T2_DE_DESY", "T1_US_FNAL_Disk"],
blocklist_sites=[],
regex_sites=None,
mode="full", # full or first. "full"==all the available replicas
client=client,
)
except Exception as e:
print(f"\n[red bold] Exception: {e}[/]")
print_replicas(sites_counts)
```
```
Sites availability for dataset:
/TTToSemiLeptonic_TuneCP5CR1_13TeV-powheg-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v2
/NANOAODSIM
```
```
Available replicas
┏━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Index ┃ Site ┃ Files ┃ Availability ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ 0 │ T2_DE_DESY │ 294 / 294 │ 100.0% │
│ 1 │ T1_US_FNAL_Disk │ 193 / 294 │ 65.6% │
└───────┴─────────────────┴───────────┴──────────────┘
```
```
# Example with blocklist
try:
(
outfiles,
outsites,
sites_counts,
) = rucio_utils.get_dataset_files_replicas(
dataset,
allowlist_sites=[],
blocklist_sites=["T2_DE_DESY", "T3_CH_PSI"],
regex_sites=None,
mode="full", # full or first. "full"==all the available replicas
client=client,
)
except Exception as e:
print(f"\n[red bold] Exception: {e}[/]")
print_replicas(sites_counts)
```
```
Sites availability for dataset:
/TTToSemiLeptonic_TuneCP5CR1_13TeV-powheg-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v2
/NANOAODSIM
```
```
Available replicas
┏━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Index ┃ Site ┃ Files ┃ Availability ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ 0 │ T1_DE_KIT_Disk │ 294 / 294 │ 100.0% │
│ 1 │ T1_UK_RAL_Disk │ 294 / 294 │ 100.0% │
│ 2 │ T1_RU_JINR_Disk │ 294 / 294 │ 100.0% │
│ 3 │ T3_KR_UOS │ 294 / 294 │ 100.0% │
│ 4 │ T1_US_FNAL_Disk │ 193 / 294 │ 65.6% │
│ 5 │ T2_US_Nebraska │ 99 / 294 │ 33.7% │
│ 6 │ T1_IT_CNAF_Disk │ 58 / 294 │ 19.7% │
│ 7 │ T2_US_Purdue │ 53 / 294 │ 18.0% │
│ 8 │ T2_BE_IIHE │ 50 / 294 │ 17.0% │
│ 9 │ T2_US_MIT │ 50 / 294 │ 17.0% │
│ 10 │ T1_ES_PIC_Disk │ 43 / 294 │ 14.6% │
│ 11 │ T2_US_Vanderbilt │ 40 / 294 │ 13.6% │
│ 12 │ T2_BR_SPRACE │ 39 / 294 │ 13.3% │
│ 13 │ T2_US_Florida │ 33 / 294 │ 11.2% │
│ 14 │ T2_IT_Legnaro │ 28 / 294 │ 9.5% │
│ 15 │ T2_US_UCSD │ 28 / 294 │ 9.5% │
│ 16 │ T2_UA_KIPT │ 26 / 294 │ 8.8% │
│ 17 │ T2_US_Caltech │ 24 / 294 │ 8.2% │
│ 18 │ T2_US_Wisconsin │ 22 / 294 │ 7.5% │
│ 19 │ T2_TR_METU │ 18 / 294 │ 6.1% │
│ 20 │ T2_ES_CIEMAT │ 17 / 294 │ 5.8% │
│ 21 │ T2_DE_RWTH │ 11 / 294 │ 3.7% │
│ 22 │ T2_BR_UERJ │ 7 / 294 │ 2.4% │
│ 23 │ T2_UK_SGrid_Bristol │ 3 / 294 │ 1.0% │
│ 24 │ T2_ES_IFCA │ 2 / 294 │ 0.7% │
└───────┴─────────────────────┴───────────┴──────────────┘
```
```
# Example with regex
try:
(
outfiles,
outsites,
sites_counts,
) = rucio_utils.get_dataset_files_replicas(
dataset,
allowlist_sites=[],
blocklist_sites=[],
regex_sites=r"T[123]_(FR|IT|BE|CH|DE|ES|UK)_\w+",
mode="full", # full or first. "full"==all the available replicas
client=client,
)
except Exception as e:
print(f"\n[red bold] Exception: {e}[/]")
print_replicas(sites_counts)
```
```
Sites availability for dataset:
/TTToSemiLeptonic_TuneCP5CR1_13TeV-powheg-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v2
/NANOAODSIM
```
```
Available replicas
┏━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Index ┃ Site ┃ Files ┃ Availability ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ 0 │ T2_DE_DESY │ 294 / 294 │ 100.0% │
│ 1 │ T1_DE_KIT_Disk │ 294 / 294 │ 100.0% │
│ 2 │ T1_UK_RAL_Disk │ 294 / 294 │ 100.0% │
│ 3 │ T3_CH_PSI │ 294 / 294 │ 100.0% │
│ 4 │ T1_IT_CNAF_Disk │ 58 / 294 │ 19.7% │
│ 5 │ T2_BE_IIHE │ 50 / 294 │ 17.0% │
│ 6 │ T1_ES_PIC_Disk │ 43 / 294 │ 14.6% │
│ 7 │ T2_IT_Legnaro │ 28 / 294 │ 9.5% │
│ 8 │ T2_ES_CIEMAT │ 17 / 294 │ 5.8% │
│ 9 │ T2_DE_RWTH │ 11 / 294 │ 3.7% │
│ 10 │ T2_UK_SGrid_Bristol │ 3 / 294 │ 1.0% │
│ 11 │ T2_ES_IFCA │ 2 / 294 │ 0.7% │
└───────┴─────────────────────┴───────────┴──────────────┘
```
## Using the DataDiscoveryCLI[#](#using-the-datadiscoverycli)
Manipulating the dataset query and replicas is simplified by the `DataDiscoveryCLI` class in `dataset_query` module.
```
from coffea.dataset_tools.dataset_query import DataDiscoveryCLI
```
```
dataset_definition = {
"/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIISummer20UL18NanoAODv9-106X*/NANOAODSIM": {
"short_name": "ZJets",
"metadata": {"xsec": 100.0, "isMC": True},
},
"/SingleMuon/Run2018C-UL20*_MiniAODv2_NanoAODv9_GT36*/NANOAOD": {"short_name": "SingleMuon", "metadata": {"isMC": False}},
}
```
The dataset definition is passed to a `DataDiscoveryCLI` to automatically query rucio and get replicas
```
ddc = DataDiscoveryCLI()
ddc.load_dataset_definition(dataset_definition, query_results_strategy="all", replicas_strategy="round-robin")
```
```
⠇ Querying rucio for replicas: /SingleMuon/Run2018C-UL2018_MiniAODv2_NanoAODv9_GT36-v1/NANOAOD
```
```
Sites availability for dataset: /SingleMuon/Run2018C-UL2018_MiniAODv2_NanoAODv9_GT36-v1/NANOAOD
```
```
Available replicas
┏━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Index ┃ Site ┃ Files ┃ Availability ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ 0 │ T2_DE_DESY │ 67 / 67 │ 100.0% │
│ 1 │ T3_KR_KISTI │ 67 / 67 │ 100.0% │
│ 2 │ T2_TW_NCHC │ 67 / 67 │ 100.0% │
│ 3 │ T2_BE_IIHE │ 67 / 67 │ 100.0% │
│ 4 │ T2_US_Purdue │ 67 / 67 │ 100.0% │
│ 5 │ T2_ES_CIEMAT │ 67 / 67 │ 100.0% │
│ 6 │ T3_FR_IPNL │ 67 / 67 │ 100.0% │
│ 7 │ T1_US_FNAL_Disk │ 61 / 67 │ 91.0% │
│ 8 │ T2_UK_London_IC │ 39 / 67 │ 58.2% │
│ 9 │ T1_FR_CCIN2P3_Disk │ 38 / 67 │ 56.7% │
│ 10 │ T2_US_Caltech │ 26 / 67 │ 38.8% │
│ 11 │ T2_CH_CERN │ 25 / 67 │ 37.3% │
│ 12 │ T2_DE_RWTH │ 22 / 67 │ 32.8% │
│ 13 │ T1_IT_CNAF_Disk │ 20 / 67 │ 29.9% │
│ 14 │ T2_US_Wisconsin │ 16 / 67 │ 23.9% │
│ 15 │ T2_US_Florida │ 16 / 67 │ 23.9% │
│ 16 │ T2_US_Nebraska │ 13 / 67 │ 19.4% │
│ 17 │ T2_TR_METU │ 11 / 67 │ 16.4% │
│ 18 │ T1_DE_KIT_Disk │ 11 / 67 │ 16.4% │
│ 19 │ T2_UK_SGrid_RALPP │ 6 / 67 │ 9.0% │
│ 20 │ T2_IT_Legnaro │ 6 / 67 │ 9.0% │
│ 21 │ T2_ES_IFCA │ 4 / 67 │ 6.0% │
│ 22 │ T2_FR_IPHC │ 2 / 67 │ 3.0% │
│ 23 │ T2_UK_London_Brunel │ 1 / 67 │ 1.5% │
└───────┴─────────────────────┴─────────┴──────────────┘
```
```
Replicas for /SingleMuon/Run2018C-UL2018_MiniAODv2_NanoAODv9_GT36-v1/NANOAOD
├── T2_DE_DESY
│ ├── root://dcache-cms-xrootd.desy.de:1094//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT
│ │ 36-v1/2520000/0144EC47-BFA3-EA43-BF05-BD4248ED6031.root
│ ├── root://dcache-cms-xrootd.desy.de:1094//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT
│ │ 36-v1/2520000/2747DEFE-A247-1F42-B0EF-E7B7F1D3FCD6.root
│ ├── root://dcache-cms-xrootd.desy.de:1094//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT
│ │ 36-v1/2520000/2DA9130E-8423-304C-9902-1E42CD72E658.root
│ ├── root://dcache-cms-xrootd.desy.de:1094//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT
│ │ 36-v1/2520000/63047CC0-38C6-F74C-9A00-0DF9050F7CF1.root
│ └── root://dcache-cms-xrootd.desy.de:1094//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT
│ 36-v1/2520000/8369B0EA-E4CC-AC4D-BD3F-0679B3310E09.root
├── T3_KR_KISTI
│ ├── root://cms-xrdr.sdfarm.kr:1094//xrd//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36
│ │ -v1/2520000/0C9615C1-7EE6-CD44-8FC0-04F63B2C16FD.root
│ ├── root://cms-xrdr.sdfarm.kr:1094//xrd//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36
│ │ -v1/2520000/152C304A-97AD-1649-BCB6-3EA0CCD0DD33.root
│ ├── root://cms-xrdr.sdfarm.kr:1094//xrd//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36
│ │ -v1/2520000/1CEB718A-7DC1-C74A-A7BE-A3C8D9FA785A.root
│ ├── root://cms-xrdr.sdfarm.kr:1094//xrd//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36
│ │ -v1/2520000/51515E3C-C640-3A4C-A16C-DC267FD142BF.root
│ ├── root://cms-xrdr.sdfarm.kr:1094//xrd//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36
│ │ -v1/2520000/7DEA3718-B7BC-EE42-A8BE-11C62BB8536D.root
│ ├── root://cms-xrdr.sdfarm.kr:1094//xrd//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36
│ │ -v1/2520000/81CEA7BA-9E66-BC4F-A96F-32642D59B653.root
│ └── root://cms-xrdr.sdfarm.kr:1094//xrd//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36
│ -v1/2520000/C4F476DA-3D00-334B-867C-7E12F94EE3AB.root
├── T2_ES_CIEMAT
│ ├── root://gaexrdoor.ciemat.es:1094///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1
│ │ /2520000/12FAE9F1-7139-924C-A8DE-9699A00FC994.root
│ ├── root://gaexrdoor.ciemat.es:1094///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1
│ │ /2520000/1DD0FAC6-3087-E44E-ABCB-8AF812C1310D.root
│ ├── root://gaexrdoor.ciemat.es:1094///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1
│ │ /2520000/3FE5B677-9AB3-0245-A1CF-4B320592F18F.root
│ ├── root://gaexrdoor.ciemat.es:1094///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1
│ │ /2520000/74A75B73-E5B8-C942-BBC9-1DDDD7F752FB.root
│ ├── root://gaexrdoor.ciemat.es:1094///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1
│ │ /2520000/8C8690F8-4FEE-1047-85F4-29E414B3D12C.root
│ └── root://gaexrdoor.ciemat.es:1094///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1
│ /2520000/DA47C0B6-BCAB-C54C-A6BF-B0A64E88E3D4.root
├── T1_FR_CCIN2P3_Disk
│ ├── root://ccxrdcms.in2p3.fr:1094/pnfs/in2p3.fr/data/cms/disk/data//store/data/Run2018C/SingleMuon/NANOAOD/UL20
│ │ 18_MiniAODv2_NanoAODv9_GT36-v1/2520000/26FC8C40-EA29-804C-B17D-84FB1C6BC505.root
│ ├── root://ccxrdcms.in2p3.fr:1094/pnfs/in2p3.fr/data/cms/disk/data//store/data/Run2018C/SingleMuon/NANOAOD/UL20
│ │ 18_MiniAODv2_NanoAODv9_GT36-v1/2520000/2D58C3FE-512A-1F48-9AEB-6F80379B8F4A.root
│ ├── root://ccxrdcms.in2p3.fr:1094/pnfs/in2p3.fr/data/cms/disk/data//store/data/Run2018C/SingleMuon/NANOAOD/UL20
│ │ 18_MiniAODv2_NanoAODv9_GT36-v1/2520000/30A3A1AB-2F27-C84E-9437-6BB3881F6856.root
│ └── root://ccxrdcms.in2p3.fr:1094/pnfs/in2p3.fr/data/cms/disk/data//store/data/Run2018C/SingleMuon/NANOAOD/UL20
│ 18_MiniAODv2_NanoAODv9_GT36-v1/2520000/A350E2E4-705C-2C4D-9B11-3436056EEBE7.root
├── T2_BE_IIHE
│ ├── root://maite.iihe.ac.be:1095//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/252
│ │ 0000/365F32F6-F971-1B4D-8E9D-C0ACD74FFB03.root
│ ├── root://maite.iihe.ac.be:1095//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/252
│ │ 0000/410C32AB-DEB5-404F-BC6B-92E8F560563F.root
│ ├── root://maite.iihe.ac.be:1095//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/252
│ │ 0000/6809B5E3-6DE6-1541-AE4C-E1804C877EDE.root
│ ├── root://maite.iihe.ac.be:1095//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/252
│ │ 0000/78AC6A39-C303-EB44-9264-71819CC70FCC.root
│ └── root://maite.iihe.ac.be:1095//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/252
│ 0000/7CCCB2C3-F210-2C42-85DF-AA00293FACFB.root
├── T2_US_Purdue
│ ├── root://eos.cms.rcac.purdue.edu///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/
│ │ 2520000/37312354-59AB-E44B-BC94-CF424D4B7DDB.root
│ ├── root://eos.cms.rcac.purdue.edu///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/
│ │ 2520000/42DC0F42-82E8-BE47-B04D-544B67274829.root
│ ├── root://eos.cms.rcac.purdue.edu///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/
│ │ 2520000/D7875684-9F26-084E-9B2B-5E9BB5D353E8.root
│ ├── root://eos.cms.rcac.purdue.edu///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/
│ │ 2520000/FAF0C67B-A8B4-8A4F-83B1-E43675CE9630.root
│ └── root://eos.cms.rcac.purdue.edu///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/
│ 2520000/FE5EEFA5-C07A-5C44-B66D-5B31BE02C7D3.root
├── T2_US_Wisconsin
│ ├── root://cmsxrootd.hep.wisc.edu:1094///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36
│ │ -v1/2520000/39D52C69-2035-A24B-A413-40976993651D.root
│ └── root://cmsxrootd.hep.wisc.edu:1094///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36
│ -v1/2520000/FCAF4145-8E3F-2142-BDCB-5E276523B592.root
├── T2_TW_NCHC
│ ├── root://se01.grid.nchc.org.tw//cms//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v
│ │ 1/2520000/459261DD-4441-6047-9FF2-1EDE468452C9.root
│ ├── root://se01.grid.nchc.org.tw//cms//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v
│ │ 1/2520000/6DDF448B-4605-5C41-9711-1C73EC5F01D3.root
│ ├── root://se01.grid.nchc.org.tw//cms//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v
│ │ 1/2520000/7B14228A-5331-DF4E-B677-7B8AA281D460.root
│ ├── root://se01.grid.nchc.org.tw//cms//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v
│ │ 1/2520000/7B181B92-AA2C-1E44-86FE-B074D359BBB3.root
│ ├── root://se01.grid.nchc.org.tw//cms//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v
│ │ 1/2520000/8223C4A3-D4BD-6A4B-A513-54B6668C7122.root
│ ├── root://se01.grid.nchc.org.tw//cms//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v
│ │ 1/2520000/A74EFE57-BAD2-C143-B8DC-817CE4F96FD7.root
│ ├── root://se01.grid.nchc.org.tw//cms//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v
│ │ 1/2520000/AE014F55-84BE-E84E-B447-0B614070CD17.root
│ ├── root://se01.grid.nchc.org.tw//cms//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v
│ │ 1/2520000/BCBF89A2-329C-744B-A38F-139EA8F94007.root
│ ├── root://se01.grid.nchc.org.tw//cms//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v
│ │ 1/2520000/D8D41BBC-D514-D342-A514-CCF48575D184.root
│ └── root://se01.grid.nchc.org.tw//cms//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v
│ 1/2520000/F1B3977A-E777-EC4D-8FC7-981FE4ED5E0C.root
├── T2_UK_London_IC
│ ├── root://gfe02.grid.hep.ph.ic.ac.uk:1094//pnfs/hep.ph.ic.ac.uk/data/cms//store/data/Run2018C/SingleMuon/NANOA
│ │ OD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/2520000/59DA0585-BD57-CE49-A15E-CDBAC5473EDE.root
│ ├── root://gfe02.grid.hep.ph.ic.ac.uk:1094//pnfs/hep.ph.ic.ac.uk/data/cms//store/data/Run2018C/SingleMuon/NANOA
│ │ OD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/2520000/F16A9138-7563-E540-B6AD-8A8A688B3830.root
│ └── root://gfe02.grid.hep.ph.ic.ac.uk:1094//pnfs/hep.ph.ic.ac.uk/data/cms//store/data/Run2018C/SingleMuon/NANOA
│ OD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/2520000/FE3D79A6-27D4-8948-A89B-2F966C5B29D4.root
├── T1_US_FNAL_Disk
│ ├── root://cmsdcadisk.fnal.gov//dcache/uscmsdisk/store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAO
│ │ Dv9_GT36-v1/2520000/62789325-3C0B-FC4D-B578-B41A396399E4.root
│ ├── root://cmsdcadisk.fnal.gov//dcache/uscmsdisk/store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAO
│ │ Dv9_GT36-v1/2520000/6EAA5EDB-0DB3-6E40-87DC-7AB582295D29.root
│ ├── root://cmsdcadisk.fnal.gov//dcache/uscmsdisk/store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAO
│ │ Dv9_GT36-v1/2520000/A59D511A-A419-714F-8EE1-8B8BAFEC04D5.root
│ ├── root://cmsdcadisk.fnal.gov//dcache/uscmsdisk/store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAO
│ │ Dv9_GT36-v1/2520000/B78A9B75-3B32-CF4E-A144-375189CF48AE.root
│ ├── root://cmsdcadisk.fnal.gov//dcache/uscmsdisk/store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAO
│ │ Dv9_GT36-v1/2520000/B9E9087C-255C-C24D-A733-FB9291DC7C3C.root
│ ├── root://cmsdcadisk.fnal.gov//dcache/uscmsdisk/store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAO
│ │ Dv9_GT36-v1/2520000/CDD2CDF9-72D0-4045-B28F-89002077FB89.root
│ └── root://cmsdcadisk.fnal.gov//dcache/uscmsdisk/store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAO
│ Dv9_GT36-v1/2520000/ED95384D-9D3D-AE45-8425-C4C080E691C5.root
├── T1_IT_CNAF_Disk
│ └── root://xrootd-cms.infn.it:1194///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/
│ 2520000/648ECD9C-8AAA-BB46-8683-C8987CCC73B9.root
├── T2_US_Nebraska
│ ├── root://xrootd-local.unl.edu:1094///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v
│ │ 1/2520000/69ABD79C-C684-8244-9F0D-153C6B8C2D9C.root
│ ├── root://xrootd-local.unl.edu:1094///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v
│ │ 1/2520000/AB8DD69D-A522-D44C-BB9C-209623F7D41A.root
│ └── root://xrootd-local.unl.edu:1094///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v
│ 1/2520000/B3487FE0-B172-AD47-A13A-388C0A9BF93F.root
├── T2_IT_Legnaro
│ └── root://t2-xrdcms.lnl.infn.it:7070///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-
│ v1/2520000/B1B449CE-5952-8347-A9A7-35FE231D0C72.root
├── T3_FR_IPNL
│ ├── root://lyogrid06.in2p3.fr//dpm/in2p3.fr/home/cms/data//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAO
│ │ Dv2_NanoAODv9_GT36-v1/2520000/BA02D468-A8CE-4F49-884F-F836BB481AD5.root
│ ├── root://lyogrid06.in2p3.fr//dpm/in2p3.fr/home/cms/data//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAO
│ │ Dv2_NanoAODv9_GT36-v1/2520000/BAAA6E00-7AC3-9947-9262-D9833D3A8B19.root
│ ├── root://lyogrid06.in2p3.fr//dpm/in2p3.fr/home/cms/data//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAO
│ │ Dv2_NanoAODv9_GT36-v1/2520000/CBD43A1E-AE2F-0B4D-A642-29FB2E9EB33B.root
│ ├── root://lyogrid06.in2p3.fr//dpm/in2p3.fr/home/cms/data//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAO
│ │ Dv2_NanoAODv9_GT36-v1/2520000/ECD4877E-707B-EA43-A38B-D1B700FBDE79.root
│ └── root://lyogrid06.in2p3.fr//dpm/in2p3.fr/home/cms/data//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAO
│ Dv2_NanoAODv9_GT36-v1/2520000/F09135D8-FCBE-AF40-BCE8-03A529C5C87F.root
├── T2_DE_RWTH
│ └── root://grid-cms-xrootd.physik.rwth-aachen.de:1094///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2
│ _NanoAODv9_GT36-v1/2520000/D40D1285-B075-D446-B1BF-86A463EF6993.root
├── T2_TR_METU
│ └── root://eymir.grid.metu.edu.tr//dpm/grid.metu.edu.tr/home/cms//store/data/Run2018C/SingleMuon/NANOAOD/UL2018
│ _MiniAODv2_NanoAODv9_GT36-v1/2520000/F34F4F00-3370-EF4D-AF44-39E474E6530F.root
└── T2_US_Florida
└── root://cmsio2.rc.ufl.edu:1094///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/2
520000/F6E44EA5-F4C6-E746-AD43-7A263F1E316E.root
```
```
Selected datasets:
```
```
Selected datasets
┏━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳┳┓
┃ … ┃ Dataset ┃┃┃
┡━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇╇┩
│ 1 │ /DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realisti… │││
│ 2 │ /SingleMuon/Run2018C-UL2018_MiniAODv2_NanoAODv9_GT36-v1/NANOAOD │││
└───┴───────────────────────────────────────────────────────────────────────────────────────────────────────────┴┴┘
```
### Filtering sites[#](#id1)
Sites filtering works in a very similar way for `DataDiscoveryCLI`
```
ddc = DataDiscoveryCLI()
ddc.do_regex_sites(r"T[123]_(CH|IT|UK|FR|DE)_\w+")
ddc.load_dataset_definition(dataset_definition, query_results_strategy="all", replicas_strategy="round-robin")
```
```
⠇ Querying rucio for replicas: /SingleMuon/Run2018C-UL2018_MiniAODv2_NanoAODv9_GT36-v1/NANOAOD
```
```
Sites availability for dataset: /SingleMuon/Run2018C-UL2018_MiniAODv2_NanoAODv9_GT36-v1/NANOAOD
```
```
Available replicas
┏━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Index ┃ Site ┃ Files ┃ Availability ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ 0 │ T2_DE_DESY │ 67 / 67 │ 100.0% │
│ 1 │ T3_FR_IPNL │ 67 / 67 │ 100.0% │
│ 2 │ T2_UK_London_IC │ 39 / 67 │ 58.2% │
│ 3 │ T1_FR_CCIN2P3_Disk │ 38 / 67 │ 56.7% │
│ 4 │ T2_CH_CERN │ 25 / 67 │ 37.3% │
│ 5 │ T2_DE_RWTH │ 22 / 67 │ 32.8% │
│ 6 │ T1_IT_CNAF_Disk │ 20 / 67 │ 29.9% │
│ 7 │ T1_DE_KIT_Disk │ 11 / 67 │ 16.4% │
│ 8 │ T2_UK_SGrid_RALPP │ 6 / 67 │ 9.0% │
│ 9 │ T2_IT_Legnaro │ 6 / 67 │ 9.0% │
│ 10 │ T2_FR_IPHC │ 2 / 67 │ 3.0% │
│ 11 │ T2_UK_London_Brunel │ 1 / 67 │ 1.5% │
└───────┴─────────────────────┴─────────┴──────────────┘
```
```
Replicas for /SingleMuon/Run2018C-UL2018_MiniAODv2_NanoAODv9_GT36-v1/NANOAOD
├── T2_CH_CERN
│ ├── root://eoscms.cern.ch//eos/cms//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/2
│ │ 520000/0144EC47-BFA3-EA43-BF05-BD4248ED6031.root
│ ├── root://eoscms.cern.ch//eos/cms//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/2
│ │ 520000/1DD0FAC6-3087-E44E-ABCB-8AF812C1310D.root
│ ├── root://eoscms.cern.ch//eos/cms//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/2
│ │ 520000/2747DEFE-A247-1F42-B0EF-E7B7F1D3FCD6.root
│ ├── root://eoscms.cern.ch//eos/cms//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/2
│ │ 520000/2DA9130E-8423-304C-9902-1E42CD72E658.root
│ ├── root://eoscms.cern.ch//eos/cms//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/2
│ │ 520000/39D52C69-2035-A24B-A413-40976993651D.root
│ ├── root://eoscms.cern.ch//eos/cms//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/2
│ │ 520000/69ABD79C-C684-8244-9F0D-153C6B8C2D9C.root
│ ├── root://eoscms.cern.ch//eos/cms//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/2
│ │ 520000/7CCCB2C3-F210-2C42-85DF-AA00293FACFB.root
│ └── root://eoscms.cern.ch//eos/cms//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/2
│ 520000/F34F4F00-3370-EF4D-AF44-39E474E6530F.root
├── T3_FR_IPNL
│ ├── root://lyogrid06.in2p3.fr//dpm/in2p3.fr/home/cms/data//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAO
│ │ Dv2_NanoAODv9_GT36-v1/2520000/0C9615C1-7EE6-CD44-8FC0-04F63B2C16FD.root
│ ├── root://lyogrid06.in2p3.fr//dpm/in2p3.fr/home/cms/data//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAO
│ │ Dv2_NanoAODv9_GT36-v1/2520000/30A3A1AB-2F27-C84E-9437-6BB3881F6856.root
│ ├── root://lyogrid06.in2p3.fr//dpm/in2p3.fr/home/cms/data//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAO
│ │ Dv2_NanoAODv9_GT36-v1/2520000/410C32AB-DEB5-404F-BC6B-92E8F560563F.root
│ ├── root://lyogrid06.in2p3.fr//dpm/in2p3.fr/home/cms/data//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAO
│ │ Dv2_NanoAODv9_GT36-v1/2520000/42DC0F42-82E8-BE47-B04D-544B67274829.root
│ ├── root://lyogrid06.in2p3.fr//dpm/in2p3.fr/home/cms/data//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAO
│ │ Dv2_NanoAODv9_GT36-v1/2520000/62789325-3C0B-FC4D-B578-B41A396399E4.root
│ ├── root://lyogrid06.in2p3.fr//dpm/in2p3.fr/home/cms/data//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAO
│ │ Dv2_NanoAODv9_GT36-v1/2520000/6809B5E3-6DE6-1541-AE4C-E1804C877EDE.root
│ ├── root://lyogrid06.in2p3.fr//dpm/in2p3.fr/home/cms/data//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAO
│ │ Dv2_NanoAODv9_GT36-v1/2520000/78AC6A39-C303-EB44-9264-71819CC70FCC.root
│ ├── root://lyogrid06.in2p3.fr//dpm/in2p3.fr/home/cms/data//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAO
│ │ Dv2_NanoAODv9_GT36-v1/2520000/A350E2E4-705C-2C4D-9B11-3436056EEBE7.root
│ ├── root://lyogrid06.in2p3.fr//dpm/in2p3.fr/home/cms/data//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAO
│ │ Dv2_NanoAODv9_GT36-v1/2520000/FCAF4145-8E3F-2142-BDCB-5E276523B592.root
│ └── root://lyogrid06.in2p3.fr//dpm/in2p3.fr/home/cms/data//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAO
│ Dv2_NanoAODv9_GT36-v1/2520000/FE3D79A6-27D4-8948-A89B-2F966C5B29D4.root
├── T2_UK_London_IC
│ ├── root://gfe02.grid.hep.ph.ic.ac.uk:1094//pnfs/hep.ph.ic.ac.uk/data/cms//store/data/Run2018C/SingleMuon/NANOA
│ │ OD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/2520000/12FAE9F1-7139-924C-A8DE-9699A00FC994.root
│ ├── root://gfe02.grid.hep.ph.ic.ac.uk:1094//pnfs/hep.ph.ic.ac.uk/data/cms//store/data/Run2018C/SingleMuon/NANOA
│ │ OD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/2520000/63047CC0-38C6-F74C-9A00-0DF9050F7CF1.root
│ ├── root://gfe02.grid.hep.ph.ic.ac.uk:1094//pnfs/hep.ph.ic.ac.uk/data/cms//store/data/Run2018C/SingleMuon/NANOA
│ │ OD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/2520000/8369B0EA-E4CC-AC4D-BD3F-0679B3310E09.root
│ ├── root://gfe02.grid.hep.ph.ic.ac.uk:1094//pnfs/hep.ph.ic.ac.uk/data/cms//store/data/Run2018C/SingleMuon/NANOA
│ │ OD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/2520000/AE014F55-84BE-E84E-B447-0B614070CD17.root
│ ├── root://gfe02.grid.hep.ph.ic.ac.uk:1094//pnfs/hep.ph.ic.ac.uk/data/cms//store/data/Run2018C/SingleMuon/NANOA
│ │ OD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/2520000/F16A9138-7563-E540-B6AD-8A8A688B3830.root
│ └── root://gfe02.grid.hep.ph.ic.ac.uk:1094//pnfs/hep.ph.ic.ac.uk/data/cms//store/data/Run2018C/SingleMuon/NANOA
│ OD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/2520000/FAF0C67B-A8B4-8A4F-83B1-E43675CE9630.root
├── T1_FR_CCIN2P3_Disk
│ ├── root://ccxrdcms.in2p3.fr:1094/pnfs/in2p3.fr/data/cms/disk/data//store/data/Run2018C/SingleMuon/NANOAOD/UL20
│ │ 18_MiniAODv2_NanoAODv9_GT36-v1/2520000/152C304A-97AD-1649-BCB6-3EA0CCD0DD33.root
│ ├── root://ccxrdcms.in2p3.fr:1094/pnfs/in2p3.fr/data/cms/disk/data//store/data/Run2018C/SingleMuon/NANOAOD/UL20
│ │ 18_MiniAODv2_NanoAODv9_GT36-v1/2520000/37312354-59AB-E44B-BC94-CF424D4B7DDB.root
│ ├── root://ccxrdcms.in2p3.fr:1094/pnfs/in2p3.fr/data/cms/disk/data//store/data/Run2018C/SingleMuon/NANOAOD/UL20
│ │ 18_MiniAODv2_NanoAODv9_GT36-v1/2520000/7B14228A-5331-DF4E-B677-7B8AA281D460.root
│ ├── root://ccxrdcms.in2p3.fr:1094/pnfs/in2p3.fr/data/cms/disk/data//store/data/Run2018C/SingleMuon/NANOAOD/UL20
│ │ 18_MiniAODv2_NanoAODv9_GT36-v1/2520000/7B181B92-AA2C-1E44-86FE-B074D359BBB3.root
│ ├── root://ccxrdcms.in2p3.fr:1094/pnfs/in2p3.fr/data/cms/disk/data//store/data/Run2018C/SingleMuon/NANOAOD/UL20
│ │ 18_MiniAODv2_NanoAODv9_GT36-v1/2520000/C4F476DA-3D00-334B-867C-7E12F94EE3AB.root
│ ├── root://ccxrdcms.in2p3.fr:1094/pnfs/in2p3.fr/data/cms/disk/data//store/data/Run2018C/SingleMuon/NANOAOD/UL20
│ │ 18_MiniAODv2_NanoAODv9_GT36-v1/2520000/D8D41BBC-D514-D342-A514-CCF48575D184.root
│ └── root://ccxrdcms.in2p3.fr:1094/pnfs/in2p3.fr/data/cms/disk/data//store/data/Run2018C/SingleMuon/NANOAOD/UL20
│ 18_MiniAODv2_NanoAODv9_GT36-v1/2520000/FE5EEFA5-C07A-5C44-B66D-5B31BE02C7D3.root
├── T2_FR_IPHC
│ └── root://sbgdcache.in2p3.fr///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/25200
│ 00/1CEB718A-7DC1-C74A-A7BE-A3C8D9FA785A.root
├── T2_DE_DESY
│ ├── root://dcache-cms-xrootd.desy.de:1094//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT
│ │ 36-v1/2520000/26FC8C40-EA29-804C-B17D-84FB1C6BC505.root
│ ├── root://dcache-cms-xrootd.desy.de:1094//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT
│ │ 36-v1/2520000/2D58C3FE-512A-1F48-9AEB-6F80379B8F4A.root
│ ├── root://dcache-cms-xrootd.desy.de:1094//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT
│ │ 36-v1/2520000/459261DD-4441-6047-9FF2-1EDE468452C9.root
│ ├── root://dcache-cms-xrootd.desy.de:1094//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT
│ │ 36-v1/2520000/51515E3C-C640-3A4C-A16C-DC267FD142BF.root
│ ├── root://dcache-cms-xrootd.desy.de:1094//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT
│ │ 36-v1/2520000/648ECD9C-8AAA-BB46-8683-C8987CCC73B9.root
│ ├── root://dcache-cms-xrootd.desy.de:1094//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT
│ │ 36-v1/2520000/74A75B73-E5B8-C942-BBC9-1DDDD7F752FB.root
│ ├── root://dcache-cms-xrootd.desy.de:1094//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT
│ │ 36-v1/2520000/81CEA7BA-9E66-BC4F-A96F-32642D59B653.root
│ ├── root://dcache-cms-xrootd.desy.de:1094//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT
│ │ 36-v1/2520000/8223C4A3-D4BD-6A4B-A513-54B6668C7122.root
│ ├── root://dcache-cms-xrootd.desy.de:1094//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT
│ │ 36-v1/2520000/8C8690F8-4FEE-1047-85F4-29E414B3D12C.root
│ ├── root://dcache-cms-xrootd.desy.de:1094//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT
│ │ 36-v1/2520000/B78A9B75-3B32-CF4E-A144-375189CF48AE.root
│ ├── root://dcache-cms-xrootd.desy.de:1094//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT
│ │ 36-v1/2520000/BAAA6E00-7AC3-9947-9262-D9833D3A8B19.root
│ ├── root://dcache-cms-xrootd.desy.de:1094//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT
│ │ 36-v1/2520000/BCBF89A2-329C-744B-A38F-139EA8F94007.root
│ ├── root://dcache-cms-xrootd.desy.de:1094//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT
│ │ 36-v1/2520000/CBD43A1E-AE2F-0B4D-A642-29FB2E9EB33B.root
│ ├── root://dcache-cms-xrootd.desy.de:1094//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT
│ │ 36-v1/2520000/D40D1285-B075-D446-B1BF-86A463EF6993.root
│ ├── root://dcache-cms-xrootd.desy.de:1094//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT
│ │ 36-v1/2520000/DA47C0B6-BCAB-C54C-A6BF-B0A64E88E3D4.root
│ ├── root://dcache-cms-xrootd.desy.de:1094//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT
│ │ 36-v1/2520000/ECD4877E-707B-EA43-A38B-D1B700FBDE79.root
│ ├── root://dcache-cms-xrootd.desy.de:1094//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT
│ │ 36-v1/2520000/ED95384D-9D3D-AE45-8425-C4C080E691C5.root
│ └── root://dcache-cms-xrootd.desy.de:1094//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT
│ 36-v1/2520000/F1B3977A-E777-EC4D-8FC7-981FE4ED5E0C.root
├── T1_DE_KIT_Disk
│ ├── root://cmsxrootd-kit-disk.gridka.de:1094///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv
│ │ 9_GT36-v1/2520000/365F32F6-F971-1B4D-8E9D-C0ACD74FFB03.root
│ ├── root://cmsxrootd-kit-disk.gridka.de:1094///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv
│ │ 9_GT36-v1/2520000/3FE5B677-9AB3-0245-A1CF-4B320592F18F.root
│ ├── root://cmsxrootd-kit-disk.gridka.de:1094///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv
│ │ 9_GT36-v1/2520000/6DDF448B-4605-5C41-9711-1C73EC5F01D3.root
│ ├── root://cmsxrootd-kit-disk.gridka.de:1094///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv
│ │ 9_GT36-v1/2520000/6EAA5EDB-0DB3-6E40-87DC-7AB582295D29.root
│ └── root://cmsxrootd-kit-disk.gridka.de:1094///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv
│ 9_GT36-v1/2520000/7DEA3718-B7BC-EE42-A8BE-11C62BB8536D.root
├── T2_DE_RWTH
│ ├── root://grid-cms-xrootd.physik.rwth-aachen.de:1094///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2
│ │ _NanoAODv9_GT36-v1/2520000/59DA0585-BD57-CE49-A15E-CDBAC5473EDE.root
│ ├── root://grid-cms-xrootd.physik.rwth-aachen.de:1094///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2
│ │ _NanoAODv9_GT36-v1/2520000/A59D511A-A419-714F-8EE1-8B8BAFEC04D5.root
│ └── root://grid-cms-xrootd.physik.rwth-aachen.de:1094///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2
│ _NanoAODv9_GT36-v1/2520000/B9E9087C-255C-C24D-A733-FB9291DC7C3C.root
├── T1_IT_CNAF_Disk
│ ├── root://xrootd-cms.infn.it:1194///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/
│ │ 2520000/A74EFE57-BAD2-C143-B8DC-817CE4F96FD7.root
│ ├── root://xrootd-cms.infn.it:1194///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/
│ │ 2520000/AB8DD69D-A522-D44C-BB9C-209623F7D41A.root
│ ├── root://xrootd-cms.infn.it:1194///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/
│ │ 2520000/B3487FE0-B172-AD47-A13A-388C0A9BF93F.root
│ ├── root://xrootd-cms.infn.it:1194///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/
│ │ 2520000/CDD2CDF9-72D0-4045-B28F-89002077FB89.root
│ ├── root://xrootd-cms.infn.it:1194///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/
│ │ 2520000/D7875684-9F26-084E-9B2B-5E9BB5D353E8.root
│ └── root://xrootd-cms.infn.it:1194///store/data/Run2018C/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9_GT36-v1/
│ 2520000/F09135D8-FCBE-AF40-BCE8-03A529C5C87F.root
└── T2_UK_SGrid_RALPP
├── root://mover.pp.rl.ac.uk:1094/pnfs/pp.rl.ac.uk/data/cms//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_Mini
│ AODv2_NanoAODv9_GT36-v1/2520000/B1B449CE-5952-8347-A9A7-35FE231D0C72.root
├── root://mover.pp.rl.ac.uk:1094/pnfs/pp.rl.ac.uk/data/cms//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_Mini
│ AODv2_NanoAODv9_GT36-v1/2520000/BA02D468-A8CE-4F49-884F-F836BB481AD5.root
└── root://mover.pp.rl.ac.uk:1094/pnfs/pp.rl.ac.uk/data/cms//store/data/Run2018C/SingleMuon/NANOAOD/UL2018_Mini
AODv2_NanoAODv9_GT36-v1/2520000/F6E44EA5-F4C6-E746-AD43-7A263F1E316E.root
```
```
Selected datasets:
```
```
Selected datasets
┏━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳┳┓
┃ … ┃ Dataset ┃┃┃
┡━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇╇┩
│ 1 │ /DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realisti… │││
│ 2 │ /SingleMuon/Run2018C-UL2018_MiniAODv2_NanoAODv9_GT36-v1/NANOAOD │││
└───┴───────────────────────────────────────────────────────────────────────────────────────────────────────────┴┴┘
```
```
ddc.do_list_selected()
```
```
Selected datasets:
```
```
Selected datasets
┏━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳┳┓
┃ … ┃ Dataset ┃┃┃
┡━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇╇┩
│ 1 │ /DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realisti… │││
│ 2 │ /SingleMuon/Run2018C-UL2018_MiniAODv2_NanoAODv9_GT36-v1/NANOAOD │││
└───┴───────────────────────────────────────────────────────────────────────────────────────────────────────────┴┴┘
```
### Save the replicas metadata[#](#save-the-replicas-metadata)
```
ddc.do_save("replicas_info.json")
```
```
File replicas_info.json saved!
```
## DataDiscoveryCLI from shell[#](#datadiscoverycli-from-shell)
The DataDiscoveryCLI can be used directly from CLI
```
!python -m coffea.dataset_tools.dataset_query --help
```
```
usage: dataset_query.py [-h] [--cli] [-d DATASET_DEFINITION] [-o OUTPUT]
[-fo FILESET_OUTPUT] [-p] [--step-size STEP_SIZE]
[--dask-cluster DASK_CLUSTER]
[-as ALLOW_SITES [ALLOW_SITES ...]]
[-bs BLOCK_SITES [BLOCK_SITES ...]] [-rs REGEX_SITES]
[--query-results-strategy QUERY_RESULTS_STRATEGY]
[--replicas-strategy REPLICAS_STRATEGY]
options:
-h, --help show this help message and exit
--cli Start the dataset discovery CLI
-d DATASET_DEFINITION, --dataset-definition DATASET_DEFINITION
Dataset definition file
-o OUTPUT, --output OUTPUT
Output name for dataset discovery output (no fileset
preprocessing)
-fo FILESET_OUTPUT, --fileset-output FILESET_OUTPUT
Output name for fileset
-p, --preprocess Preprocess with dask
--step-size STEP_SIZE
Step size for preprocessing
--dask-cluster DASK_CLUSTER
Dask cluster url
-as ALLOW_SITES [ALLOW_SITES ...], --allow-sites ALLOW_SITES [ALLOW_SITES ...]
List of sites to be allowlisted
-bs BLOCK_SITES [BLOCK_SITES ...], --block-sites BLOCK_SITES [BLOCK_SITES ...]
List of sites to be blocklisted
-rs REGEX_SITES, --regex-sites REGEX_SITES
Regex string to be used to filter the sites
--query-results-strategy QUERY_RESULTS_STRATEGY
Mode for query results selection: [all|manual]
--replicas-strategy REPLICAS_STRATEGY
Mode for selecting replicas for datasets:
[manual|round-robin|choose]
```
```
!python -m coffea.dataset_tools.dataset_query --cli -d dataset_definition.json
```
## Preprocess the fileset with dask[#](#preprocess-the-fileset-with-dask)
The replicas metadata contain the file location in the CMS grid.
This info can be **preprocessed** with uproot and dask-awkward to extract the **fileset**. Practically a fileset is a collection of metadata about the file location, file name, chunks splitting, that can be used directly to configure the uproot reading.
This step replaces the preprocessing step in coffea 0.7.x. The output of the preprocessing can be used directly to start an analysis with dask-awkward.
The preprocessing is performed locally with multiple processes if `dask_cluster==None`, but a pre-existing dask cluster url can be passed.
```
fileset_total = ddc.do_preprocess(
output_file="fileset",
step_size=10000, # chunk size for files splitting
align_to_clusters=False,
scheduler_url=None,
)
```
```
⠙ Preprocessing files to extract available chunks with dask
```
```
Saved available fileset chunks to fileset_available.json.gz
```
```
Saved all fileset chunks to fileset_all.json.gz
```
```
import gzip
import json
with gzip.open("fileset_available.json.gz", "rt") as file:
fileset_available = json.load(file)
```
```
dataset = "/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v2/NANOAODSIM"
for i, (file, meta) in enumerate(fileset_available[dataset]["files"].items()):
print(file, meta)
if i > 3:
break
```
```
root://cmsxrd.ts.infn.it:1094///store/mc/RunIISummer20UL18NanoAODv9/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/100000/13D0AD97-6B32-CB4C-BA87-5E37BA4CF20E.root {'object_path': 'Events', 'steps': [[0, 10000], [10000, 20000], [20000, 30000], [30000, 40000], [40000, 50000], [50000, 59081]], 'uuid': 'fbe50b00-1f7e-11ec-97b8-2bbee183beef'}
root://cmsxrd.ts.infn.it:1094///store/mc/RunIISummer20UL18NanoAODv9/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/230000/00C9792D-ACD2-2547-BB04-097F0C4E47E3.root {'object_path': 'Events', 'steps': [[0, 10000], [10000, 20000], [20000, 30000], [30000, 40000], [40000, 50000], [50000, 60000], [60000, 70000], [70000, 80000], [80000, 90000], [90000, 100000], [100000, 110000], [110000, 120000], [120000, 130000], [130000, 138192]], 'uuid': '938a4fe2-1d77-11ec-bddf-59319e86beef'}
root://dcache-cms-xrootd.desy.de:1094//store/mc/RunIISummer20UL18NanoAODv9/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/230000/00EA9563-5449-D24E-9566-98AE8E2A61AE.root {'object_path': 'Events', 'steps': [[0, 10000], [10000, 20000], [20000, 30000], [30000, 40000], [40000, 50000], [50000, 60000], [60000, 70000], [70000, 80000], [80000, 90000], [90000, 100000], [100000, 110000], [110000, 120000], [120000, 130000], [130000, 140000], [140000, 150000], [150000, 160000], [160000, 170000], [170000, 180000], [180000, 190000], [190000, 200000], [200000, 210000], [210000, 220000], [220000, 230000], [230000, 240000], [240000, 250000], [250000, 260000], [260000, 270000], [270000, 280000], [280000, 290000], [290000, 300000], [300000, 310000], [310000, 320000], [320000, 330000], [330000, 340000], [340000, 350000], [350000, 360000], [360000, 370000], [370000, 380000], [380000, 390000], [390000, 400000], [400000, 410000], [410000, 420000], [420000, 430000], [430000, 440000], [440000, 450000], [450000, 460000], [460000, 470000], [470000, 480000], [480000, 490000], [490000, 500000], [500000, 510000], [510000, 520000], [520000, 530000], [530000, 540000], [540000, 550000], [550000, 560000], [560000, 570000], [570000, 580000], [580000, 590000], [590000, 600000], [600000, 610000], [610000, 620000], [620000, 630000], [630000, 640000], [640000, 650000], [650000, 660000], [660000, 670000], [670000, 680000], [680000, 690000], [690000, 700000], [700000, 710000], [710000, 720000], [720000, 730000], [730000, 740000], [740000, 750000], [750000, 760000], [760000, 770000], [770000, 780000], [780000, 790000], [790000, 800000], [800000, 810000], [810000, 820000], [820000, 830000], [830000, 840000], [840000, 850000], [850000, 860000], [860000, 870000], [870000, 880000], [880000, 890000], [890000, 900000], [900000, 910000], [910000, 920000], [920000, 930000], [930000, 940000], [940000, 950000], [950000, 960000], [960000, 970000], [970000, 980000], [980000, 990000], [990000, 1000000], [1000000, 1010000], [1010000, 1020000], [1020000, 1030000], [1030000, 1040000], [1040000, 1050000], [1050000, 1060000], [1060000, 1070000], [1070000, 1080000], [1080000, 1090000], [1090000, 1100000], [1100000, 1110000], [1110000, 1120000], [1120000, 1130000], [1130000, 1140000], [1140000, 1150000], [1150000, 1160000], [1160000, 1170000], [1170000, 1180000], [1180000, 1190000], [1190000, 1200000], [1200000, 1210000], [1210000, 1220000], [1220000, 1230000], [1230000, 1240000], [1240000, 1250000], [1250000, 1260000], [1260000, 1270000], [1270000, 1280000], [1280000, 1290000], [1290000, 1300000], [1300000, 1310000], [1310000, 1320000], [1320000, 1330000], [1330000, 1340000], [1340000, 1350000], [1350000, 1360000], [1360000, 1370000], [1370000, 1380000], [1380000, 1390000], [1390000, 1400000], [1400000, 1410000], [1410000, 1420000], [1420000, 1430000], [1430000, 1440000], [1440000, 1450000], [1450000, 1460000], [1460000, 1470000], [1470000, 1480000], [1480000, 1490000], [1490000, 1500000], [1500000, 1510000], [1510000, 1520000], [1520000, 1530000], [1530000, 1540000], [1540000, 1550000], [1550000, 1551326]], 'uuid': 'ced110a0-1b0f-11ec-b2e9-09c08e80beef'}
root://grid-cms-xrootd.physik.rwth-aachen.de:1094///store/mc/RunIISummer20UL18NanoAODv9/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/230000/068B0797-DEF5-9341-BBBE-EDBE50EBC6A1.root {'object_path': 'Events', 'steps': [[0, 10000], [10000, 20000], [20000, 30000], [30000, 40000], [40000, 50000], [50000, 60000], [60000, 70000], [70000, 80000], [80000, 90000], [90000, 100000], [100000, 110000], [110000, 120000], [120000, 130000], [130000, 140000], [140000, 150000], [150000, 160000], [160000, 170000], [170000, 180000], [180000, 190000], [190000, 200000], [200000, 210000], [210000, 220000], [220000, 230000], [230000, 240000], [240000, 250000], [250000, 260000], [260000, 270000], [270000, 280000], [280000, 290000], [290000, 300000], [300000, 310000], [310000, 320000], [320000, 330000], [330000, 340000], [340000, 350000], [350000, 360000], [360000, 370000], [370000, 380000], [380000, 390000], [390000, 400000], [400000, 410000], [410000, 420000], [420000, 430000], [430000, 440000], [440000, 450000], [450000, 460000], [460000, 470000], [470000, 480000], [480000, 490000], [490000, 500000], [500000, 510000], [510000, 520000], [520000, 530000], [530000, 540000], [540000, 550000], [550000, 560000], [560000, 570000], [570000, 580000], [580000, 590000], [590000, 600000], [600000, 610000], [610000, 620000], [620000, 630000], [630000, 640000], [640000, 650000], [650000, 660000], [660000, 670000], [670000, 680000], [680000, 690000], [690000, 700000], [700000, 710000], [710000, 720000], [720000, 730000], [730000, 740000], [740000, 750000], [750000, 760000], [760000, 770000], [770000, 780000], [780000, 790000], [790000, 800000], [800000, 810000], [810000, 820000], [820000, 830000], [830000, 840000], [840000, 850000], [850000, 860000], [860000, 870000], [870000, 880000], [880000, 890000], [890000, 900000], [900000, 910000], [910000, 920000], [920000, 930000], [930000, 940000], [940000, 950000], [950000, 960000], [960000, 970000], [970000, 980000], [980000, 990000], [990000, 1000000], [1000000, 1010000], [1010000, 1020000], [1020000, 1030000], [1030000, 1040000], [1040000, 1050000], [1050000, 1060000], [1060000, 1070000], [1070000, 1080000], [1080000, 1090000], [1090000, 1100000], [1100000, 1110000], [1110000, 1120000], [1120000, 1130000], [1130000, 1138724]], 'uuid': 'd86ab2e2-1b28-11ec-8504-738a8e80beef'}
root://cmsxrd.ts.infn.it:1094///store/mc/RunIISummer20UL18NanoAODv9/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/230000/0CFD79EF-41AB-4B4A-8F62-06393273EEDE.root {'object_path': 'Events', 'steps': [[0, 10000], [10000, 20000], [20000, 30000], [30000, 40000], [40000, 50000], [50000, 60000], [60000, 70000], [70000, 80000], [80000, 90000], [90000, 100000], [100000, 110000], [110000, 120000], [120000, 130000], [130000, 140000], [140000, 150000], [150000, 160000], [160000, 170000], [170000, 180000], [180000, 190000], [190000, 200000], [200000, 210000], [210000, 220000], [220000, 230000], [230000, 240000], [240000, 250000], [250000, 260000], [260000, 270000], [270000, 280000], [280000, 290000], [290000, 300000], [300000, 310000], [310000, 320000], [320000, 330000], [330000, 340000], [340000, 350000], [350000, 360000], [360000, 370000], [370000, 380000], [380000, 390000], [390000, 400000], [400000, 410000], [410000, 420000], [420000, 430000], [430000, 440000], [440000, 450000], [450000, 460000], [460000, 470000], [470000, 480000], [480000, 490000], [490000, 500000], [500000, 510000], [510000, 520000], [520000, 530000], [530000, 540000], [540000, 550000], [550000, 560000], [560000, 570000], [570000, 580000], [580000, 590000], [590000, 600000], [600000, 610000], [610000, 620000], [620000, 630000], [630000, 640000], [640000, 650000], [650000, 660000], [660000, 670000], [670000, 680000], [680000, 690000], [690000, 700000], [700000, 710000], [710000, 720000], [720000, 730000], [730000, 740000], [740000, 750000], [750000, 760000], [760000, 770000], [770000, 780000], [780000, 790000], [790000, 800000], [800000, 810000], [810000, 820000], [820000, 830000], [830000, 840000], [840000, 850000], [850000, 860000], [860000, 870000], [870000, 880000], [880000, 890000], [890000, 900000], [900000, 910000], [910000, 911868]], 'uuid': '9d799986-1ad9-11ec-9257-fc1b1e0abeef'}
```
[previous
Running inference tools](mltools.html)
[next
Dataset specification with FileSpec classes](filespec.html)
On this page
* [Using Rucio utils directly](#using-rucio-utils-directly)
+ [Dataset replicas](#dataset-replicas)
+ [Filtering sites](#filtering-sites)
* [Using the DataDiscoveryCLI](#using-the-datadiscoverycli)
+ [Filtering sites](#id1)
+ [Save the replicas metadata](#save-the-replicas-metadata)
* [DataDiscoveryCLI from shell](#datadiscoverycli-from-shell)
* [Preprocess the fileset with dask](#preprocess-the-fileset-with-dask)
[Show Source](../_sources/notebooks/dataset_discovery.ipynb.txt)
© Copyright 2025, Fermi National Accelerator Laboratory.
Created using [Sphinx](https://www.sphinx-doc.org/) 7.4.7.
Built with the [PyData Sphinx Theme](https://pydata-sphinx-theme.readthedocs.io/en/stable/index.html) 0.17.1.

2.6s · markdown via readability

Dataset specification with FileSpec classes — coffea 2026.4.1.dev3+gbfc8fd2cf.d20260501 documentation
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
* [Dataset discovery tools](dataset_discovery.html)
* Dataset specification with FileSpec classes
* [Coffea by Example](../examples.html)
* Dataset specification with FileSpec classes
# Dataset specification with FileSpec classes[#](#dataset-specification-with-filespec-classes)
This is a rendered copy of [filespec.ipynb](https://github.com/scikit-hep/coffea/blob/master/binder/filespec.ipynb). You can optionally run it interactively on [binder at this link](https://mybinder.org/v2/gh/coffeateam/coffea/master?filepath=binder%2Ffilespec.ipynb)
This notebook provides a comprehensive guide to using the new Pydantic-based FileSpec classes in Coffea’s dataset tools. These classes provide type-safe, validated data structures for managing file specifications, datasets, and filesets in high-energy physics data analysis workflows.
## Overview[#](#overview)
The FileSpec system provides:
* **Type-safe data structures** with automatic validation
* **Automatic format detection** for ROOT and Parquet files
* **Seamless integration** with existing Coffea functions
* **JSON serialization/deserialization** for data persistence
* **Automatic promotion** between optional and concrete specifications
## Table of Contents[#](#table-of-contents)
1. [Basic File Specifications](#basic-file-specifications)
2. [InputFiles, PreprocessedFiles](#coffea-file-dict)
3. [Dataset Specifications](#dataset-specifications)
4. [Fileset Specifications](#fileset-specifications)
5. [Integration with Preprocessing](#integration-with-preprocessing)
6. [Integration with apply\_to\_fileset](#integration-with-apply_to_fileset)
7. [Dataset Manipulation Functions](#dataset-manipulation-functions)
8. [Advanced Usage Examples](#advanced-usage-examples)
9. [Migration from Legacy Formats](#migration-from-legacy-formats)
```
# Import necessary libraries
from pydantic import ValidationError
import rich
import dask
# Import the FileSpec classes and dataset tools
from coffea.dataset_tools import (
# FileSpec classes
ROOTFileSpec,
ParquetFileSpec,
CoffeaROOTFileSpec,
CoffeaROOTFileSpecOptional,
CoffeaParquetFileSpec,
CoffeaParquetFileSpecOptional,
InputFiles,
DatasetSpec,
DataGroupSpec,
# Dataset manipulation functions
preprocess,
apply_to_fileset,
max_chunks,
max_chunks_per_file,
slice_chunks,
slice_files,
max_files,
filter_files,
# ModelFactory utility class
ModelFactory,
)
from coffea.nanoevents import NanoAODSchema
from coffea.processor.test_items import NanoEventsProcessor
print("FileSpec classes and dataset tools imported successfully!")
```
```
FileSpec classes and dataset tools imported successfully!
```
## 1. Basic File Specifications[#](#basic-file-specifications)
The FileSpec system provides several classes for representing individual file specifications:
### File Specification Hierarchy[#](#file-specification-hierarchy)
* **ROOTFileSpec**: Basic specification for ROOT files
* **ParquetFileSpec**: Basic specification for Parquet files
* **CoffeaROOTFileSpecOptional**: ROOT files with optional metadata
* **CoffeaROOTFileSpec**: ROOT files with complete metadata (required)
* **CoffeaParquetFileSpecOptional**: Parquet files with optional metadata
* **CoffeaParquetFileSpec**: Parquet files with complete metadata (required)
```
# 1.1 Basic ROOTFileSpec for ROOT files
print("=== Basic ROOTFileSpec ===")
# Minimal ROOT file specification
uproot_spec = ROOTFileSpec(object_path="Events")
print("Basic ROOT spec:")
rich.print(uproot_spec)
print(f"Format: {uproot_spec.format}")
print(f"Steps: {uproot_spec.steps}")
# ROOT file specification with steps
uproot_spec_with_steps = ROOTFileSpec(
object_path="Events",
steps=[[0, 1000], [1000, 2000], [2000, 3000]]
)
print("\nROOT spec with steps:")
rich.print(uproot_spec_with_steps)
```
```
=== Basic ROOTFileSpec ===
Basic ROOT spec:
```
```
ROOTFileSpec(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
num_selected_entries=None
)
```
```
Format: root
Steps: None
ROOT spec with steps:
```
```
ROOTFileSpec(
object_path='Events',
steps=[[0, 1000], [1000, 2000], [2000, 3000]],
num_entries=None,
format='root',
lfn=None,
pfn=None,
num_selected_entries=3000
)
```
```
# 1.2 Basic ParquetFileSpec for Parquet files
print("=== Basic ParquetFileSpec ===")
# Minimal Parquet file specification
parquet_spec = ParquetFileSpec()
print("Basic Parquet spec:")
rich.print(parquet_spec)
print(f"Format: {parquet_spec.format}")
print(f"Object path (always None): {parquet_spec.object_path}")
# Parquet file specification with steps
parquet_spec_with_steps = ParquetFileSpec(
steps=[[0, 5000], [5000, 10000]]
)
print("\nParquet spec with steps:")
rich.print(parquet_spec_with_steps)
```
```
=== Basic ParquetFileSpec ===
Basic Parquet spec:
```
```
ParquetFileSpec(
object_path=None,
steps=None,
num_entries=None,
format='parquet',
lfn=None,
pfn=None,
num_selected_entries=None
)
```
```
Format: parquet
Object path (always None): None
Parquet spec with steps:
```
```
ParquetFileSpec(
object_path=None,
steps=[[0, 5000], [5000, 10000]],
num_entries=None,
format='parquet',
lfn=None,
pfn=None,
num_selected_entries=10000
)
```
```
# 1.3 CoffeaROOTFileSpecOptional - ROOT files with optional metadata
print("=== CoffeaROOTFileSpecOptional ===")
# Optional specification with minimal data
coffea_uproot_optional = CoffeaROOTFileSpecOptional(object_path="Events")
print("Optional ROOT spec:")
rich.print(coffea_uproot_optional)
# Optional specification with some metadata
coffea_uproot_partial = CoffeaROOTFileSpecOptional(
object_path="Events",
steps=[[0, 1000]],
num_entries=1000
)
print("Partial ROOT spec:")
rich.print(coffea_uproot_partial)
# Optional specification with all metadata
coffea_uproot_complete = CoffeaROOTFileSpecOptional(
object_path="Events",
steps=[[0, 1000], [1000, 2000]],
num_entries=2000,
uuid="12345678-90ab-cdef-1234-567890abcdef"
)
print("Complete optional ROOT spec:")
rich.print(coffea_uproot_complete)
```
```
=== CoffeaROOTFileSpecOptional ===
Optional ROOT spec:
```
```
CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
)
```
```
Partial ROOT spec:
```
```
CoffeaROOTFileSpecOptional(
object_path='Events',
steps=[[0, 1000]],
num_entries=1000,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=1000
)
```
```
Complete optional ROOT spec:
```
```
CoffeaROOTFileSpecOptional(
object_path='Events',
steps=[[0, 1000], [1000, 2000]],
num_entries=2000,
format='root',
lfn=None,
pfn=None,
uuid='12345678-90ab-cdef-1234-567890abcdef',
num_selected_entries=2000
)
```
```
# 1.4 CoffeaROOTFileSpec - ROOT files with required metadata
print("=== CoffeaROOTFileSpec ===")
# Complete specification (all fields required)
try:
coffea_uproot_required = CoffeaROOTFileSpec(
object_path="Events",
steps=[[0, 1000], [1000, 2000]],
num_entries=2000,
uuid="12345678-90ab-cdef-1234-567890abcdef"
)
print("Complete required ROOT spec:")
rich.print(coffea_uproot_required)
except ValidationError as e:
print(f"Validation error: {e}")
# Attempt to create incomplete specification (should fail)
try:
incomplete_spec = CoffeaROOTFileSpec(object_path="Events")
print("This shouldn't print - validation should fail!")
except ValidationError as e:
print(f"Expected validation error for incomplete spec: {e.error_count()} errors")
rich.print(e)
```
```
=== CoffeaROOTFileSpec ===
Complete required ROOT spec:
```
```
CoffeaROOTFileSpec(
object_path='Events',
steps=[[0, 1000], [1000, 2000]],
num_entries=2000,
format='root',
lfn=None,
pfn=None,
uuid='12345678-90ab-cdef-1234-567890abcdef',
num_selected_entries=2000
)
```
```
Expected validation error for incomplete spec: 3 errors
```
```
3 validation errors for CoffeaROOTFileSpec
steps
Field required [type=missing, input_value={'object_path': 'Events'}, input_type=dict]
For further information visit https://errors.pydantic.dev/2.11/v/missing
num_entries
Field required [type=missing, input_value={'object_path': 'Events'}, input_type=dict]
For further information visit https://errors.pydantic.dev/2.11/v/missing
uuid
Field required [type=missing, input_value={'object_path': 'Events'}, input_type=dict]
For further information visit https://errors.pydantic.dev/2.11/v/missing
```
```
# 1.5 Parquet specifications (similar pattern)
print("=== CoffeaParquetFileSpec ===")
# Optional Parquet specification
parquet_optional = CoffeaParquetFileSpecOptional(
steps=[[0, 5000]],
num_entries=5000,
uuid="parquet-uuid-example"
)
print("Optional Parquet spec:")
rich.print(parquet_optional)
# Required Parquet specification
parquet_required = CoffeaParquetFileSpec(
steps=[[0, 5000], [5000, 10000]],
num_entries=10000,
uuid="parquet-uuid-complete"
)
print("Required Parquet spec:")
rich.print(parquet_required)
```
```
=== CoffeaParquetFileSpec ===
Optional Parquet spec:
```
```
CoffeaParquetFileSpecOptional(
object_path=None,
steps=[[0, 5000]],
num_entries=5000,
format='parquet',
lfn=None,
pfn=None,
uuid='parquet-uuid-example',
num_selected_entries=5000
)
```
```
Required Parquet spec:
```
```
CoffeaParquetFileSpec(
object_path=None,
steps=[[0, 5000], [5000, 10000]],
num_entries=10000,
format='parquet',
lfn=None,
pfn=None,
uuid='parquet-uuid-complete',
num_selected_entries=10000
)
```
## 2. InputFiles Specification[#](#inputfiles-specification)
The `InputFiles` classe is a dictionary-like containers for any mixture of CoffeaFileSpec classes, both Uproot/Parquet and concrete/Optional. `PreprocessedFiles` is the specific subtype permitting only concrete FileSpecs. They automatically handle:
* **Format detection**: Automatically identifies if files are ROOT or Parquet, by testing the key (filename)
* **Dictionary-like interface**: Easy access to files using standard dict methods
* **FileSpec promotion**: Automatically tries to upcast CoffeaROOTFileSpecOptional and CoffeaParquetFileSpecOptional to their concrete classes, when the necessary fields have been set post-initialization (such as when they are preprocessed)
* **FileSpec-wide format**: Provides the `format` computed property to determine which format(s) are present.
The `InputFiles` or `PreprocessedFiles` forms the “files” subfield of the `DatasetSpec` class. Notably, unlike the FileSpec classes, it doesn’t require kwarg-setting in the constructor, simply pass in a regular dictionary of `{"filename1": dict|FileSpec, ..., "filenameN": dict|FileSpec}`
```
# 2.1 Create an InputFiles
print("=== InputFiles ===")
# using a dictioanry of CoffeaROOTFileSpec(Optional) and CoffeaParquetFileSpec(Optional)
dict_of_filespecs = {
"file1.root": CoffeaROOTFileSpec(
object_path="Events", steps=[[0, 10]], num_entries=10, uuid="uuid1"
),
"file1.parquet": CoffeaParquetFileSpec(
steps=[[0, 100]], num_entries=100, uuid="uuid2"
),
"file2.root": CoffeaROOTFileSpecOptional(
object_path="Events", steps=[[10, 20]], num_entries=None, uuid=None
),
}
filedict_from_filespecs = InputFiles(dict_of_filespecs)
print("InputFiles:")
rich.print(filedict_from_filespecs)
# computed property: format
print(f"Detected format(s): {filedict_from_filespecs.format}")
print(f"Number of files: {len(filedict_from_filespecs)}")
# Iteration over the file dict
print("Iterating over file dict:")
for fname, spec in filedict_from_filespecs.items():
print(f"File: {fname}\nSpec:")
rich.print(spec)
# __getitem__, __setitem__ access
print(f"Accessing 'file1.root': {filedict_from_filespecs['file1.root']}")
print("=== Modifying a file spec in the dict ===")
filedict_from_filespecs["file2.root"].num_entries = 20
filedict_from_filespecs["file3.root"] = CoffeaROOTFileSpec(
object_path="Events", steps=[[0, 30]], num_entries=30, uuid="uuid3"
)
# show keys
print(f"Keys in filedict: {list(filedict_from_filespecs.keys())}")
```
```
=== InputFiles ===
InputFiles:
```
```
InputFiles(
root={
'file1.root': CoffeaROOTFileSpec(
object_path='Events',
steps=[[0, 10]],
num_entries=10,
format='root',
lfn=None,
pfn=None,
uuid='uuid1',
num_selected_entries=10
),
'file1.parquet': CoffeaParquetFileSpec(
object_path=None,
steps=[[0, 100]],
num_entries=100,
format='parquet',
lfn=None,
pfn=None,
uuid='uuid2',
num_selected_entries=100
),
'file2.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=[[10, 20]],
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=10
)
}
)
```
```
Detected format(s): root|parquet
Number of files: 3
Iterating over file dict:
File: file1.root
Spec:
```
```
CoffeaROOTFileSpec(
object_path='Events',
steps=[[0, 10]],
num_entries=10,
format='root',
lfn=None,
pfn=None,
uuid='uuid1',
num_selected_entries=10
)
```
```
File: file1.parquet
Spec:
```
```
CoffeaParquetFileSpec(
object_path=None,
steps=[[0, 100]],
num_entries=100,
format='parquet',
lfn=None,
pfn=None,
uuid='uuid2',
num_selected_entries=100
)
```
```
File: file2.root
Spec:
```
```
CoffeaROOTFileSpecOptional(
object_path='Events',
steps=[[10, 20]],
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=10
)
```
```
Accessing 'file1.root': object_path='Events' steps=[[0, 10]] num_entries=10 format='root' lfn=None pfn=None uuid='uuid1' num_selected_entries=10
=== Modifying a file spec in the dict ===
Keys in filedict: ['file1.root', 'file1.parquet', 'file2.root', 'file3.root']
```
```
# 2.2 Create a InputFiles from pure dictionary
print("=== InputFiles from pure dictionary ===")
dict_of_dicts = {
"file1.root": {
"object_path": "Events",
"steps": [[0, 10]],
"num_entries": 10,
"uuid": "uuid1"
},
"file1.parquet": {
"steps": [[0, 100]],
"num_entries": 100,
"uuid": "uuid2"
},
"file2.root": {
"object_path": "Events",
"steps": [[10, 20]],
"num_entries": None,
"uuid": None
},
}
filedict_from_pure_dict = InputFiles(dict_of_dicts)
print("InputFiles from pure dictionary:")
rich.print(filedict_from_pure_dict)
```
```
=== InputFiles from pure dictionary ===
InputFiles from pure dictionary:
```
```
InputFiles(
root={
'file1.root': CoffeaROOTFileSpec(
object_path='Events',
steps=[[0, 10]],
num_entries=10,
format='root',
lfn=None,
pfn=None,
uuid='uuid1',
num_selected_entries=10
),
'file1.parquet': CoffeaParquetFileSpec(
object_path=None,
steps=[[0, 100]],
num_entries=100,
format='parquet',
lfn=None,
pfn=None,
uuid='uuid2',
num_selected_entries=100
),
'file2.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=[[10, 20]],
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=10
)
}
)
```
## 3. Dataset Specifications[#](#dataset-specifications)
The `DatasetSpec` class represents a collection of files that form a logical dataset. It automatically handles:
* **Format detection**: Automatically identifies if files are ROOT or Parquet
* **File validation**: Ensures all files in a dataset are compatible
* **Metadata management**: Stores dataset-level metadata and forms
* **Dictionary-like interface**: Easy access to files using standard dict methods
```
# 3.1 Creating DatasetSpec from file dictionaries
print("=== DatasetSpec Creation ===")
# Create a dataset from a simple file dictionary (ROOT files)
root_dataset_simple = DatasetSpec(
files={
"data_file_1.root": "Events",
"data_file_2.root": "Events",
"data_file_3.root": "Events"
},
metadata={"sample_type": "data", "year": 2023}
)
print("Simple ROOT dataset:")
rich.print(root_dataset_simple)
print(f"Detected format: {root_dataset_simple.format}")
print(f"Number of files: {len(root_dataset_simple.files)}")
print(f"Metadata: {root_dataset_simple.metadata}")
```
```
=== DatasetSpec Creation ===
Simple ROOT dataset:
```
```
DatasetSpec(
files=InputFiles(
root={
'data_file_1.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
),
'data_file_2.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
),
'data_file_3.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
)
}
),
metadata={'sample_type': 'data', 'year': 2023},
format='root',
compressed_form=None,
did=None
)
```
```
Detected format: root
Number of files: 3
Metadata: {'sample_type': 'data', 'year': 2023}
```
```
# 3.2 Creating DatasetSpec with complete file specifications
print("=== DatasetSpec with Complete Specifications ===")
# Create individual file specifications
file1_spec = CoffeaROOTFileSpec(
object_path="Events",
steps=[[0, 1000], [1000, 2000]],
num_entries=2000,
uuid="file1-uuid"
)
file2_spec = CoffeaROOTFileSpec(
object_path="Events",
steps=[[0, 1500], [1500, 3000]],
num_entries=3000,
uuid="file2-uuid"
)
# Create dataset with complete specifications
complete_dataset = DatasetSpec(
files=InputFiles({
"processed_data_1.root": file1_spec,
"processed_data_2.root": file2_spec
}),
metadata={"processing_version": "v2.1", "cross_section": 1.23},
)
print("Complete dataset:")
rich.print(complete_dataset)
print(f"Detected format: {complete_dataset.format}")
print(f"Number of files: {len(complete_dataset.files)}")
print(f"Ready for column-joining: {complete_dataset.joinable}")
```
```
=== DatasetSpec with Complete Specifications ===
Complete dataset:
```
```
DatasetSpec(
files=InputFiles(
root={
'processed_data_1.root': CoffeaROOTFileSpec(
object_path='Events',
steps=[[0, 1000], [1000, 2000]],
num_entries=2000,
format='root',
lfn=None,
pfn=None,
uuid='file1-uuid',
num_selected_entries=2000
),
'processed_data_2.root': CoffeaROOTFileSpec(
object_path='Events',
steps=[[0, 1500], [1500, 3000]],
num_entries=3000,
format='root',
lfn=None,
pfn=None,
uuid='file2-uuid',
num_selected_entries=3000
)
}
),
metadata={'processing_version': 'v2.1', 'cross_section': 1.23},
format='root',
compressed_form=None,
did=None
)
```
```
Detected format: root
Number of files: 2
Ready for column-joining: False
```
```
# 3.3 Mixed format handling
print("=== Mixed Format Datasets ===")
# Try to create a dataset with both ROOT and Parquet files
try:
mixed_dataset = DatasetSpec(
files={
"data.root": CoffeaROOTFileSpec(
object_path="Events",
steps=[[0, 1000]],
num_entries=1000,
uuid="root-uuid"
),
"data.parquet": CoffeaParquetFileSpec(
steps=[[0, 2000]],
num_entries=2000,
uuid="parquet-uuid"
)
}
)
print("Mixed format dataset:")
rich.print(mixed_dataset)
print(f"Detected format: {mixed_dataset.format}")
except ValidationError as e:
print(f"Validation error for mixed format dataset: {e}")
# If you need a mixed format, file an issue in the coffea GitHub repository requesting the feature, with an example of your usecase!
```
```
=== Mixed Format Datasets ===
Validation error for mixed format dataset: 1 validation error for DatasetSpec
Value error, format: format must be one of {'root', 'parquet'} [type=value_error, input_value={'files': {'data.root': C...selected_entries=2000)}}, input_type=dict]
For further information visit https://errors.pydantic.dev/2.11/v/value_error
```
```
# 3.4 DatasetSpec from file lists
print("=== DatasetSpec from File Lists ===")
# Create dataset from a list of file:object_path strings
dataset_from_list = DatasetSpec(
files=[
"simulation_1.root:Events",
"simulation_2.root:Events",
"root://simulation_3.root:Events",
"simulation_4.root.1:AuxiliaryData",
],
metadata={"sample_type": "simulation", "process": "ttbar"}
)
print("Dataset from list:")
rich.print(dataset_from_list)
print(f"Files: {list(dataset_from_list.files.keys())}")
```
```
=== DatasetSpec from File Lists ===
Dataset from list:
```
```
DatasetSpec(
files=InputFiles(
root={
'simulation_1.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
),
'simulation_2.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
),
'root://simulation_3.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
),
'simulation_4.root.1': CoffeaROOTFileSpecOptional(
object_path='AuxiliaryData',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
)
}
),
metadata={'sample_type': 'simulation', 'process': 'ttbar'},
format='root',
compressed_form=None,
did=None
)
```
```
Files: ['simulation_1.root', 'simulation_2.root', 'root://simulation_3.root', 'simulation_4.root.1']
```
## 4. Fileset Specifications[#](#fileset-specifications)
The `DataGroupSpec` class represents a collection of datasets, typically used for analysis workflows. It provides:
* **Multiple datasets management**: Handle multiple physics processes/samples
* **JSON serialization**: Save and load complete analysis configurations
* **Dictionary interface**: Access datasets by name
* **Validation**: Ensure all datasets are properly specified
```
# 4.1 Creating DataGroupSpec
print("=== DataGroupSpec Creation ===")
# Create a fileset with multiple datasets
analysis_fileset = DataGroupSpec({
"ttbar_simulation": DatasetSpec(
files={
"ttbar_1.root": "Events",
"ttbar_2.root": "Events"
},
metadata={"process": "ttbar", "cross_section": 831.8}
),
"single_top": DatasetSpec(
files={
"singletop_1.root": "Events",
"singletop_2.root": "Events"
},
metadata={"process": "single_top", "cross_section": 136.02}
),
"data": DatasetSpec(
files={
"data_2023A.root": "Events",
"data_2023B.root": "Events"
},
metadata={"is_data": True, "era": "2023"}
)
})
print("Analysis fileset:")
rich.print(analysis_fileset)
print(f"Number of datasets: {len(analysis_fileset)}")
print(f"Dataset names: {list(analysis_fileset.keys())}")
```
```
=== DataGroupSpec Creation ===
Analysis fileset:
```
```
DataGroupSpec(
root={
'ttbar_simulation': DatasetSpec(
files=InputFiles(
root={
'ttbar_1.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
),
'ttbar_2.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
)
}
),
metadata={'process': 'ttbar', 'cross_section': 831.8},
format='root',
compressed_form=None,
did=None
),
'single_top': DatasetSpec(
files=InputFiles(
root={
'singletop_1.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
),
'singletop_2.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
)
}
),
metadata={'process': 'single_top', 'cross_section': 136.02},
format='root',
compressed_form=None,
did=None
),
'data': DatasetSpec(
files=InputFiles(
root={
'data_2023A.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
),
'data_2023B.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
)
}
),
metadata={'is_data': True, 'era': '2023'},
format='root',
compressed_form=None,
did=None
)
}
)
```
```
Number of datasets: 3
Dataset names: ['ttbar_simulation', 'single_top', 'data']
```
```
# 4.2 Accessing and manipulating filesets
print("=== Fileset Access and Manipulation ===")
# Access individual datasets
ttbar_dataset = analysis_fileset["ttbar_simulation"]
print(f"TTbar dataset: {ttbar_dataset.metadata}")
# Iterate over datasets
print("\nDataset summary:")
for dataset_name, dataset in analysis_fileset.items():
num_files = len(dataset.files)
process = dataset.metadata.get("process", "unknown")
print(f" {dataset_name}: {num_files} files, process={process}")
# Add a new dataset
analysis_fileset["wjets"] = DatasetSpec(
files={"wjets_1.root": "Events"},
metadata={"process": "wjets", "cross_section": 61526.7}
)
print(f"\nAfter adding WJets: {len(analysis_fileset)} datasets")
```
```
=== Fileset Access and Manipulation ===
TTbar dataset: {'process': 'ttbar', 'cross_section': 831.8}
Dataset summary:
ttbar_simulation: 2 files, process=ttbar
single_top: 2 files, process=single_top
data: 2 files, process=unknown
After adding WJets: 4 datasets
```
```
# 4.3 JSON serialization and deserialization
print("=== JSON Serialization ===")
# Serialize fileset to JSON
fileset_json = analysis_fileset.model_dump_json(indent=2)
print("Fileset JSON (first 500 characters):")
print(fileset_json[:500] + "..." if len(fileset_json) > 500 else fileset_json)
# Deserialize from JSON
restored_fileset = DataGroupSpec.model_validate_json(fileset_json)
print(f"\nRestored fileset has {len(restored_fileset)} datasets")
print(f"Dataset names match: {set(analysis_fileset.keys()) == set(restored_fileset.keys())}")
```
```
=== JSON Serialization ===
Fileset JSON (first 500 characters):
{
"ttbar_simulation": {
"files": {
"ttbar_1.root": {
"object_path": "Events",
"steps": null,
"num_entries": null,
"format": "root",
"lfn": null,
"pfn": null,
"uuid": null,
"num_selected_entries": null
},
"ttbar_2.root": {
"object_path": "Events",
"steps": null,
"num_entries": null,
"format": "root",
"lfn": null,
"pfn": null,
"uuid": null,
"num_se...
Restored fileset has 4 datasets
Dataset names match: True
```
## 5. Integration with Preprocessing[#](#integration-with-preprocessing)
The `preprocess` function works seamlessly with FileSpec classes, and will promote Optional types to concrete types for successfully accessed elements of the datasets:
* **Calculate file steps**: Automatically determine optimal chunking
* **Extract metadata**: Get file UUIDs, entry counts, and schemas(using `save_form=True`)
* **Generate forms**: Create Awkward Array forms for type checking
* **Handle errors**: Skip bad files and report issues
```
# 5.1 Basic preprocessing with FileSpec
print("=== Preprocessing with FileSpec ===")
# Note: This is a demonstration - in practice you'd use real file paths
demo_fileset = DataGroupSpec({
"ZJets": {"files": ["https://raw.githubusercontent.com/scikit-hep/coffea/master/tests/samples/nano_dy.root:Events"]},
"Data": {"files": [
"https://raw.githubusercontent.com/scikit-hep/coffea/master/tests/samples/nano_dimuon.root:Events",
"nano_dimuon_not_there.root:Events",
]},
})
rich.print(demo_fileset)
print("Preprocessing the fileset...")
dataset_runnable, dataset_updated = preprocess(
demo_fileset,
step_size=7,
align_clusters=False,
files_per_batch=10,
skip_bad_files=True,
save_form=True,
)
print("Fileset after preprocessing (excluding compressed_form string):")
rich.print({k: v.model_dump(exclude="compressed_form") for k, v in dataset_runnable.items()})
print("Updated files (including inaccessible ones):")
rich.print({k: v.model_dump(exclude="compressed_form") for k, v in dataset_updated.items()})
#rich.print({dname: {k: v for k, v in dataset_updated[dname].files.items() if k not in dataset_runnable[dname].files} for dname in dataset_updated})
```
```
=== Preprocessing with FileSpec ===
```
```
DataGroupSpec(
root={
'ZJets': DatasetSpec(
files=InputFiles(
root={
'https://raw.githubusercontent.com/scikit-hep/coffea/master/tests/samples/nano_dy.root':
CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
)
}
),
metadata={},
format='root',
compressed_form=None,
did=None
),
'Data': DatasetSpec(
files=InputFiles(
root={
'https://raw.githubusercontent.com/scikit-hep/coffea/master/tests/samples/nano_dimuon.root':
CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
),
'nano_dimuon_not_there.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
)
}
),
metadata={},
format='root',
compressed_form=None,
did=None
)
}
)
```
```
Preprocessing the fileset...
Fileset after preprocessing (excluding compressed_form string):
```
```
{
'ZJets': {
'files': {
'https://raw.githubusercontent.com/scikit-hep/coffea/master/tests/samples/nano_dy.root': {
'object_path': 'Events',
'steps': [[0, 7], [7, 14], [14, 21], [21, 28], [28, 35], [35, 40]],
'num_entries': 40,
'format': 'root',
'lfn': None,
'pfn': None,
'uuid': 'a9490124-3648-11ea-89e9-f5b55c90beef',
'num_selected_entries': 40
}
},
'metadata': {},
'format': 'root',
'did': None
},
'Data': {
'files': {
'https://raw.githubusercontent.com/scikit-hep/coffea/master/tests/samples/nano_dimuon.root': {
'object_path': 'Events',
'steps': [[0, 7], [7, 14], [14, 21], [21, 28], [28, 35], [35, 40]],
'num_entries': 40,
'format': 'root',
'lfn': None,
'pfn': None,
'uuid': 'a210a3f8-3648-11ea-a29f-f5b55c90beef',
'num_selected_entries': 40
}
},
'metadata': {},
'format': 'root',
'did': None
}
}
```
```
Updated files (including inaccessible ones):
```
```
{
'ZJets': {
'files': {
'https://raw.githubusercontent.com/scikit-hep/coffea/master/tests/samples/nano_dy.root': {
'object_path': 'Events',
'steps': [[0, 7], [7, 14], [14, 21], [21, 28], [28, 35], [35, 40]],
'num_entries': 40,
'format': 'root',
'lfn': None,
'pfn': None,
'uuid': 'a9490124-3648-11ea-89e9-f5b55c90beef',
'num_selected_entries': 40
}
},
'metadata': {},
'format': 'root',
'did': None
},
'Data': {
'files': {
'https://raw.githubusercontent.com/scikit-hep/coffea/master/tests/samples/nano_dimuon.root': {
'object_path': 'Events',
'steps': [[0, 7], [7, 14], [14, 21], [21, 28], [28, 35], [35, 40]],
'num_entries': 40,
'format': 'root',
'lfn': None,
'pfn': None,
'uuid': 'a210a3f8-3648-11ea-a29f-f5b55c90beef',
'num_selected_entries': 40
},
'nano_dimuon_not_there.root': {
'object_path': 'Events',
'steps': None,
'num_entries': None,
'format': 'root',
'lfn': None,
'pfn': None,
'uuid': None,
'num_selected_entries': None
}
},
'metadata': {},
'format': 'root',
'did': None
}
}
```
## 6. Integration with apply\_to\_fileset[#](#integration-with-apply-to-fileset)
The `apply_to_fileset` function processes datasets using FileSpec classes:
```
# 6.1 Example processor for demonstration
to_compute = apply_to_fileset(
NanoEventsProcessor(),
dataset_runnable,
schemaclass=NanoAODSchema,
)
out = dask.compute(to_compute)[0]
rich.print(out)
```
```
/Users/nmangane/scikit-hep-dev-4/coffea/src/coffea/nanoevents/schemas/nanoaod.py:264: RuntimeWarning: Missing cross-reference index for LowPtElectron_electronIdx => Electron
warnings.warn(
/Users/nmangane/scikit-hep-dev-4/coffea/src/coffea/nanoevents/schemas/nanoaod.py:264: RuntimeWarning: Missing cross-reference index for LowPtElectron_genPartIdx => GenPart
warnings.warn(
/Users/nmangane/scikit-hep-dev-4/coffea/src/coffea/nanoevents/schemas/nanoaod.py:264: RuntimeWarning: Missing cross-reference index for LowPtElectron_photonIdx => Photon
warnings.warn(
/Users/nmangane/scikit-hep-dev-4/coffea/src/coffea/nanoevents/schemas/nanoaod.py:264: RuntimeWarning: Missing cross-reference index for FatJet_genJetAK8Idx => GenJetAK8
warnings.warn(
```
```
{
'ZJets': {
'mass': Hist(
StrCategory(['ZJets'], growth=True, name='dataset', label='Primary dataset'),
Regular(30000, 0.25, 300, name='mass', label='$m_{\\mu\\mu}$ [GeV]'),
storage=Double()) # Sum: 6.0,
'pt': Hist(
StrCategory(['ZJets'], growth=True, name='dataset', label='Primary dataset'),
Regular(30000, 0.24, 300, name='pt', label='$p_{T}$ [GeV]'),
storage=Double()) # Sum: 18.0,
'cutflow': {'ZJets_pt': np.int64(18), 'ZJets_mass': np.int64(6)},
'worker': set()
},
'Data': {
'mass': Hist(
StrCategory(['Data'], growth=True, name='dataset', label='Primary dataset'),
Regular(30000, 0.25, 300, name='mass', label='$m_{\\mu\\mu}$ [GeV]'),
storage=Double()) # Sum: 66.0,
'pt': Hist(
StrCategory(['Data'], growth=True, name='dataset', label='Primary dataset'),
Regular(30000, 0.24, 300, name='pt', label='$p_{T}$ [GeV]'),
storage=Double()) # Sum: 84.0,
'cutflow': {'Data_pt': np.int64(84), 'Data_mass': np.int64(66)},
'worker': set()
}
}
```
## 7. Dataset Manipulation Functions[#](#dataset-manipulation-functions)
Coffea provides powerful functions for manipulating FileSpec-based datasets:
* **max\_chunks**: Limit processing to first N chunks per dataset
* **max\_chunks\_per\_file**: Limit processing to first N chunks per file
* **slice\_chunks**: Select specific chunk ranges
* **max\_files**: Limit number of files per dataset
* **slice\_files**: Select specific file ranges
* **filter\_files**: Remove files based on criteria
```
# 7.1 Chunk-based manipulations
print("=== Chunk-based Manipulations ===")
# Create a sample fileset for demonstration
sample_fileset = DataGroupSpec({
"large_dataset": DatasetSpec(
files={
f"file_{i}.root": CoffeaROOTFileSpec(
object_path="Events",
steps=[[j*1000, (j+1)*1000] for j in range(10)], # 10 chunks per file
num_entries=10000,
uuid=f"uuid-{i}"
)
for i in range(3) # 3 files
},
metadata={"total_files": 3}
)
})
print(f"Original dataset: {len(sample_fileset['large_dataset'].files)} files")
# Limit to first 5 chunks total per dataset
limited_chunks = max_chunks(sample_fileset, maxchunks=5)
print("After max_chunks(5):")
total_chunks = sum(len(f.steps) for f in limited_chunks['large_dataset'].files.values())
print(f" Total chunks: {total_chunks}")
# Limit to first 2 chunks per file
limited_per_file = max_chunks_per_file(sample_fileset, maxchunks=2)
print("After max_chunks_per_file(2):")
for fname, fspec in limited_per_file['large_dataset'].files.items():
print(f" {fname}: {len(fspec.steps)} chunks")
```
```
=== Chunk-based Manipulations ===
Original dataset: 3 files
After max_chunks(5):
Total chunks: 5
After max_chunks_per_file(2):
file_0.root: 2 chunks
file_1.root: 2 chunks
file_2.root: 2 chunks
```
```
# 7.2 Advanced chunk slicing
print("=== Advanced Chunk Slicing ===")
# Slice specific chunk ranges
middle_chunks = slice_chunks(sample_fileset, slice(5, 15))
print("Middle chunks (5:15):")
total_chunks = sum(len(f.steps) for f in middle_chunks['large_dataset'].files.values())
print(f" Total chunks: {total_chunks}")
# Slice every other chunk
every_other = slice_chunks(sample_fileset, slice(None, None, 2))
print("Every other chunk (::2):")
total_chunks = sum(len(f.steps) for f in every_other['large_dataset'].files.values())
print(f" Total chunks: {total_chunks}")
# Slice per file vs per dataset
per_file_slice = slice_chunks(sample_fileset, slice(3), bydataset=False)
print("First 3 chunks per file:")
for fname, fspec in per_file_slice['large_dataset'].files.items():
print(f" {fname}: {len(fspec.steps)} chunks")
```
```
=== Advanced Chunk Slicing ===
Middle chunks (5:15):
Total chunks: 10
Every other chunk (::2):
Total chunks: 15
First 3 chunks per file:
file_0.root: 3 chunks
file_1.root: 3 chunks
file_2.root: 3 chunks
```
```
# 7.3 File-based manipulations
print("=== File-based Manipulations ===")
# Limit number of files
limited_files = max_files(sample_fileset, maxfiles=2)
print(f"After max_files(2): {len(limited_files['large_dataset'].files)} files")
# Slice specific files
first_two_files = slice_files(sample_fileset, slice(2))
print(f"First two files: {len(first_two_files['large_dataset'].files)} files")
print(f"File names: {list(first_two_files['large_dataset'].files.keys())}")
# Last file only
last_file = slice_files(sample_fileset, slice(-1, None))
print(f"Last file: {list(last_file['large_dataset'].files.keys())}")
```
```
=== File-based Manipulations ===
After max_files(2): 2 files
First two files: 2 files
File names: ['file_0.root', 'file_1.root']
Last file: ['file_2.root']
```
```
# 7.4 Filtering files
print("=== File Filtering ===")
# Create a sample with some empty files for filtering
fileset_with_empty = DataGroupSpec({
"mixed_dataset": DatasetSpec(
files={
"good_file_1.root": CoffeaROOTFileSpec(
object_path="Events",
steps=[[0, 1000]],
num_entries=1000,
uuid="good-1"
),
"empty_file.root": CoffeaROOTFileSpec(
object_path="Events",
steps=[[0, 0]], # Empty file
num_entries=0,
uuid="empty"
),
"good_file_2.root": CoffeaROOTFileSpec(
object_path="Events",
steps=[[0, 2000]],
num_entries=2000,
uuid="good-2"
)
}
)
})
print(f"Before filtering: {len(fileset_with_empty['mixed_dataset'].files)} files")
# Filter out empty files
filtered_fileset = filter_files(fileset_with_empty)
print(f"After filtering: {len(filtered_fileset['mixed_dataset'].files)} files")
print(f"Remaining files: {list(filtered_fileset['mixed_dataset'].files.keys())}")
```
```
=== File Filtering ===
Before filtering: 3 files
After filtering: 2 files
Remaining files: ['good_file_1.root', 'good_file_2.root']
```
## 8. Advanced Usage Examples[#](#advanced-usage-examples)
This section demonstrates advanced patterns and best practices for using FileSpec classes in real-world scenarios.
```
# 8.1 Building complex analysis filesets
print("=== Complex Analysis Fileset ===")
def build_analysis_fileset():
"""Build a comprehensive analysis fileset"""
# Signal samples
signal_samples = {}
for mass in [125, 200, 300]:
signal_samples[f"higgs_m{mass}"] = DatasetSpec(
files={
f"higgs_m{mass}_part{i}.root": CoffeaROOTFileSpec(
object_path="Events",
steps=[[j*5000, (j+1)*5000] for j in range(20)],
num_entries=100000,
uuid=f"higgs-{mass}-{i}"
)
for i in range(3)
},
metadata={
"process": "higgs",
"mass": mass,
"cross_section": 48.58 if mass == 125 else 10.0,
"is_signal": True
}
)
# Background samples
background_samples = {
"ttbar": DatasetSpec(
files={
f"ttbar_part{i}.root": "Events" for i in range(10)
},
metadata={"process": "ttbar", "cross_section": 831.8, "is_signal": False}
),
"wjets": DatasetSpec(
files={
f"wjets_part{i}.root": "Events" for i in range(15)
},
metadata={"process": "wjets", "cross_section": 61526.7, "is_signal": False}
)
}
# Data samples
data_samples = {
f"data_{era}": DatasetSpec(
files={
f"data_{era}_part{i}.root": "Events" for i in range(5)
},
metadata={"is_data": True, "era": era, "luminosity": 41.5}
)
for era in ["2022A", "2022B", "2022C", "2022D"]
}
# Combine all samples
all_samples = {}
all_samples.update(signal_samples)
all_samples.update(background_samples)
all_samples.update(data_samples)
return DataGroupSpec(all_samples)
# Build the fileset
full_analysis = build_analysis_fileset()
print(f"Full analysis fileset: {len(full_analysis)} datasets")
# Categorize datasets
signal_datasets = [name for name, ds in full_analysis.items()
if ds.metadata.get("is_signal", False)]
background_datasets = [name for name, ds in full_analysis.items()
if not ds.metadata.get("is_data", False) and not ds.metadata.get("is_signal", False)]
data_datasets = [name for name, ds in full_analysis.items()
if ds.metadata.get("is_data", False)]
print(f"Signal datasets: {len(signal_datasets)}")
print(f"Background datasets: {len(background_datasets)}")
print(f"Data datasets: {len(data_datasets)}")
```
```
=== Complex Analysis Fileset ===
Full analysis fileset: 9 datasets
Signal datasets: 3
Background datasets: 2
Data datasets: 4
```
```
# 8.2 Conditional processing and dataset selection
print("=== Conditional Processing ===")
def select_datasets_by_criteria(fileset: DataGroupSpec, **criteria) -> DataGroupSpec:
"""Select datasets matching specific criteria"""
selected = {}
for name, dataset in fileset.items():
match = True
for key, value in criteria.items():
if dataset.metadata.get(key) != value:
match = False
break
if match:
selected[name] = dataset
return DataGroupSpec(selected)
# Select only signal datasets
signal_only = select_datasets_by_criteria(full_analysis, is_signal=True)
print(f"Signal-only fileset: {len(signal_only)} datasets")
# Select 2022 data only
data_2022 = select_datasets_by_criteria(full_analysis, is_data=True)
data_2022_filtered = DataGroupSpec({
name: ds for name, ds in data_2022.items()
if "2022" in name
})
print(f"2022 data fileset: {len(data_2022_filtered)} datasets")
# Create a test subset with limited files
test_subset = DataGroupSpec({
name: max_files(DataGroupSpec({name: ds}), maxfiles=2)[name]
for name, ds in full_analysis.items()
if name in signal_datasets[:2] + background_datasets[:1]
})
print(f"Test subset: {len(test_subset)} datasets with limited files")
```
```
=== Conditional Processing ===
Signal-only fileset: 3 datasets
2022 data fileset: 4 datasets
Test subset: 3 datasets with limited files
```
```
# 8.3 Error handling and validation
print("=== Error Handling and Validation ===")
def validate_fileset(fileset: DataGroupSpec) -> dict:
"""Validate a fileset and return diagnostic information"""
diagnostics = {
"total_datasets": len(fileset),
"total_files": 0,
"empty_datasets": [],
"format_distribution": {},
"metadata_issues": []
}
for name, dataset in fileset.items():
# Count files
num_files = len(dataset.files)
diagnostics["total_files"] += num_files
# Check for empty datasets
if num_files == 0:
diagnostics["empty_datasets"].append(name)
# Track format distribution
fmt = dataset.format
diagnostics["format_distribution"][fmt] = diagnostics["format_distribution"].get(fmt, 0) + 1
# Check metadata
if not dataset.metadata:
diagnostics["metadata_issues"].append(f"{name}: No metadata")
elif "process" not in dataset.metadata and not dataset.metadata.get("is_data", False):
diagnostics["metadata_issues"].append(f"{name}: Missing process information")
return diagnostics
# Validate our analysis fileset
validation_results = validate_fileset(full_analysis)
print("Fileset validation results:")
for key, value in validation_results.items():
if isinstance(value, list) and len(value) == 0:
continue
print(f" {key}: {value}")
```
```
=== Error Handling and Validation ===
Fileset validation results:
total_datasets: 9
total_files: 54
format_distribution: {'root': 9}
```
```
# 8.4 Performance optimization strategies
print("=== Performance Optimization ===")
def optimize_fileset_for_processing(fileset: DataGroupSpec, target_chunk_size: int = 100000) -> DataGroupSpec:
"""Optimize fileset for processing performance"""
optimized = {}
for name, dataset in fileset.items():
# Calculate total events and files
total_events = sum(f.num_entries for f in dataset.files.values()
if hasattr(f, 'num_entries') and f.num_entries)
num_files = len(dataset.files)
if total_events == 0:
# Skip empty datasets
continue
# Determine optimal chunking strategy
if total_events < target_chunk_size:
# Small dataset - process as single chunk per file
chunk_strategy = "single_chunk_per_file"
optimized_dataset = dataset
elif num_files < 5:
# Few large files - use chunk slicing
chunk_strategy = "chunk_slicing"
max_chunks_total = max(1, total_events // target_chunk_size)
optimized_dataset = max_chunks(DataGroupSpec({name: dataset}),
maxchunks=max_chunks_total)[name]
else:
# Many files - limit files and chunks per file
chunk_strategy = "file_and_chunk_limiting"
max_files_count = min(num_files, 20) # Limit to 20 files
temp_fileset = max_files(DataGroupSpec({name: dataset}), maxfiles=max_files_count)
optimized_dataset = max_chunks_per_file(temp_fileset, maxchunks=5)[name]
optimized[name] = optimized_dataset
print(f" {name}: {chunk_strategy}, {len(optimized_dataset.files)} files")
return DataGroupSpec(optimized)
# Optimize our test subset
optimized_subset = optimize_fileset_for_processing(test_subset)
print(f"Optimized subset: {len(optimized_subset)} datasets")
rich.print(optimized_subset)
```
```
=== Performance Optimization ===
higgs_m125: chunk_slicing, 1 files
higgs_m200: chunk_slicing, 1 files
Optimized subset: 2 datasets
```
```
DataGroupSpec(
root={
'higgs_m125': DatasetSpec(
files=InputFiles(
root={
'higgs_m125_part0.root': CoffeaROOTFileSpec(
object_path='Events',
steps=[[0, 5000], [5000, 10000]],
num_entries=100000,
format='root',
lfn=None,
pfn=None,
uuid='higgs-125-0',
num_selected_entries=10000
)
}
),
metadata={'process': 'higgs', 'mass': 125, 'cross_section': 48.58, 'is_signal': True},
format='root',
compressed_form=None,
did=None
),
'higgs_m200': DatasetSpec(
files=InputFiles(
root={
'higgs_m200_part0.root': CoffeaROOTFileSpec(
object_path='Events',
steps=[[0, 5000], [5000, 10000]],
num_entries=100000,
format='root',
lfn=None,
pfn=None,
uuid='higgs-200-0',
num_selected_entries=10000
)
}
),
metadata={'process': 'higgs', 'mass': 200, 'cross_section': 10.0, 'is_signal': True},
format='root',
compressed_form=None,
did=None
)
}
)
```
## 9. Migration from pure dictionary Formats and conversion utility ModelFactory[#](#migration-from-pure-dictionary-formats-and-conversion-utility-modelfactory)
This section shows how to migrate from legacy dictionary-based filesets to the explicit FileSpec classes.
Largely, a well-defined legacy fileset (purely nested dictionary) can be converted merely by passing it into the DataGroupSpec as an argument.
It should be noted that DataGroupSpec, InputFiles, and PreprocessedFiles behave like dictionaries and expect a dictionary input, but the other filespec classes expect keyword arguments, and so when a dictionary is explicitly passed to the FileSpec constructors, they should be unpacked with the `**some_dict` syntax.
```
# 9.1 Legacy format examples
print("=== Legacy Format Migration ===")
# Legacy dictionary format (old style)
legacy_fileset = {
"ttbar": {
"files": {
"ttbar_1.root": "Events",
"ttbar_2.root": "Events"
}
},
"data": {
"files": {
"data_1.root": {
"object_path": "Events",
"steps": [[0, 1000], [1000, 2000]],
"num_entries": 2000,
"uuid": "legacy-uuid"
}
}
}
}
print("Legacy fileset structure:")
for name, content in legacy_fileset.items():
print(f" {name}: {len(content['files'])} files")
```
```
=== Legacy Format Migration ===
Legacy fileset structure:
ttbar: 2 files
data: 1 files
```
## ModelFactory[#](#modelfactory)
The `ModelFactory` class contains a few utility methods to help with manipulating the pydantic FileSpec classes. Largely, they serve as an example, with a few utilities regarding formats (which are called internally during validation/instantiation of the classes) plus conversion functions with simple logic for manipulating the filespec classes.
* **dict\_to\_ROOTFileSpec**: Tries to convert the dictionary to a concrete CoffeaROOTFileSpec, and failing that, falls back to the Optional type
* **dict\_to\_parquetfilespec**: Tries to convert the dictionary to a concrete CoffeaParquetFileSpec, and failing that, falls back to the Optional type
* **filespec\_to\_dict**: Inverse function to convert FileSpec to dictionaries. Thanks to pydantic functionality, merely calls `.model_dump()` on the class
* **dict\_to\_datasetspec**: Tries to convert the dictionary to a DatasetSpec, by utilizing the constructor.
* **datasetspec\_to\_dict**: If coerce\_filespec\_to\_dict is True (default), calls `.model_dump()` to completely convert to a dictionary. If False, only the outermost DatasetSpec is removed, leaving a dictionary of pydantic and elementary python types, which is the result of calling `dict(datasetspec)` instead of `.model_dump()`
* **valid\_format**: Ensures the format(s) are in the supported list for coffea processing
* **attempt\_promotion**: Will accept any of the FileSpec, DatasetSpec, or DataGroupSpec and try to promote any(nested) types within to concrete classes. Can effectively be emulated by calling the pydantic class constructor on the output of the original model’s `.model_dump()` method, with or without `**inputs` call in place (for non-dictionary-like models)
```
# 10.1 Converting formats
print("=== Converting legacy formats via ModelFactory ===")
print("The methods dict_to_ROOTFileSpec and dict_to_parquetfilespec are deprecated, as their functionality is covered by the pydantic models directly.")
print("For converting pydantic classes to dictionaries, the function datasetspec_to_dict demonstrates the two methods: model_dump() and dict(AModel).")
print("With the former, the entire model hierarchy is converted to dictionaries, while with the latter only the top-level model is converted, leaving nested models intact.")
pure_dictionary = ModelFactory.datasetspec_to_dict(full_analysis['ttbar'], coerce_filespec_to_dict=True)
print("DatasetSpec to pure dictionary (with coerce_filespec_to_dict=True):")
rich.print(pure_dictionary)
print("Accomplished via model_dump():")
rich.print(full_analysis['ttbar'].model_dump())
mixed_dictionary = ModelFactory.datasetspec_to_dict(full_analysis['ttbar'], coerce_filespec_to_dict=False)
print("DatasetSpec to top-level dictionary (with coerce_filespec_to_dict=False):")
rich.print(mixed_dictionary)
print("Now the partial conversion via dict():")
rich.print(dict(full_analysis['ttbar']))
```
```
=== Converting legacy formats via ModelFactory ===
The methods dict_to_ROOTFileSpec and dict_to_parquetfilespec are deprecated, as their functionality is covered by the pydantic models directly.
For converting pydantic classes to dictionaries, the function datasetspec_to_dict demonstrates the two methods: model_dump() and dict(AModel).
With the former, the entire model hierarchy is converted to dictionaries, while with the latter only the top-level model is converted, leaving nested models intact.
DatasetSpec to pure dictionary (with coerce_filespec_to_dict=True):
```
```
{
'files': {
'ttbar_part0.root': {
'object_path': 'Events',
'steps': None,
'num_entries': None,
'format': 'root',
'lfn': None,
'pfn': None,
'uuid': None,
'num_selected_entries': None
},
'ttbar_part1.root': {
'object_path': 'Events',
'steps': None,
'num_entries': None,
'format': 'root',
'lfn': None,
'pfn': None,
'uuid': None,
'num_selected_entries': None
},
'ttbar_part2.root': {
'object_path': 'Events',
'steps': None,
'num_entries': None,
'format': 'root',
'lfn': None,
'pfn': None,
'uuid': None,
'num_selected_entries': None
},
'ttbar_part3.root': {
'object_path': 'Events',
'steps': None,
'num_entries': None,
'format': 'root',
'lfn': None,
'pfn': None,
'uuid': None,
'num_selected_entries': None
},
'ttbar_part4.root': {
'object_path': 'Events',
'steps': None,
'num_entries': None,
'format': 'root',
'lfn': None,
'pfn': None,
'uuid': None,
'num_selected_entries': None
},
'ttbar_part5.root': {
'object_path': 'Events',
'steps': None,
'num_entries': None,
'format': 'root',
'lfn': None,
'pfn': None,
'uuid': None,
'num_selected_entries': None
},
'ttbar_part6.root': {
'object_path': 'Events',
'steps': None,
'num_entries': None,
'format': 'root',
'lfn': None,
'pfn': None,
'uuid': None,
'num_selected_entries': None
},
'ttbar_part7.root': {
'object_path': 'Events',
'steps': None,
'num_entries': None,
'format': 'root',
'lfn': None,
'pfn': None,
'uuid': None,
'num_selected_entries': None
},
'ttbar_part8.root': {
'object_path': 'Events',
'steps': None,
'num_entries': None,
'format': 'root',
'lfn': None,
'pfn': None,
'uuid': None,
'num_selected_entries': None
},
'ttbar_part9.root': {
'object_path': 'Events',
'steps': None,
'num_entries': None,
'format': 'root',
'lfn': None,
'pfn': None,
'uuid': None,
'num_selected_entries': None
}
},
'metadata': {'process': 'ttbar', 'cross_section': 831.8, 'is_signal': False},
'format': 'root',
'compressed_form': None,
'did': None
}
```
```
Accomplished via model_dump():
```
```
{
'files': {
'ttbar_part0.root': {
'object_path': 'Events',
'steps': None,
'num_entries': None,
'format': 'root',
'lfn': None,
'pfn': None,
'uuid': None,
'num_selected_entries': None
},
'ttbar_part1.root': {
'object_path': 'Events',
'steps': None,
'num_entries': None,
'format': 'root',
'lfn': None,
'pfn': None,
'uuid': None,
'num_selected_entries': None
},
'ttbar_part2.root': {
'object_path': 'Events',
'steps': None,
'num_entries': None,
'format': 'root',
'lfn': None,
'pfn': None,
'uuid': None,
'num_selected_entries': None
},
'ttbar_part3.root': {
'object_path': 'Events',
'steps': None,
'num_entries': None,
'format': 'root',
'lfn': None,
'pfn': None,
'uuid': None,
'num_selected_entries': None
},
'ttbar_part4.root': {
'object_path': 'Events',
'steps': None,
'num_entries': None,
'format': 'root',
'lfn': None,
'pfn': None,
'uuid': None,
'num_selected_entries': None
},
'ttbar_part5.root': {
'object_path': 'Events',
'steps': None,
'num_entries': None,
'format': 'root',
'lfn': None,
'pfn': None,
'uuid': None,
'num_selected_entries': None
},
'ttbar_part6.root': {
'object_path': 'Events',
'steps': None,
'num_entries': None,
'format': 'root',
'lfn': None,
'pfn': None,
'uuid': None,
'num_selected_entries': None
},
'ttbar_part7.root': {
'object_path': 'Events',
'steps': None,
'num_entries': None,
'format': 'root',
'lfn': None,
'pfn': None,
'uuid': None,
'num_selected_entries': None
},
'ttbar_part8.root': {
'object_path': 'Events',
'steps': None,
'num_entries': None,
'format': 'root',
'lfn': None,
'pfn': None,
'uuid': None,
'num_selected_entries': None
},
'ttbar_part9.root': {
'object_path': 'Events',
'steps': None,
'num_entries': None,
'format': 'root',
'lfn': None,
'pfn': None,
'uuid': None,
'num_selected_entries': None
}
},
'metadata': {'process': 'ttbar', 'cross_section': 831.8, 'is_signal': False},
'format': 'root',
'compressed_form': None,
'did': None
}
```
```
DatasetSpec to top-level dictionary (with coerce_filespec_to_dict=False):
```
```
{
'files': InputFiles(
root={
'ttbar_part0.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
),
'ttbar_part1.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
),
'ttbar_part2.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
),
'ttbar_part3.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
),
'ttbar_part4.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
),
'ttbar_part5.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
),
'ttbar_part6.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
),
'ttbar_part7.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
),
'ttbar_part8.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
),
'ttbar_part9.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
)
}
),
'metadata': {'process': 'ttbar', 'cross_section': 831.8, 'is_signal': False},
'format': 'root',
'compressed_form': None,
'did': None
}
```
```
Now the partial conversion via dict():
```
```
{
'files': InputFiles(
root={
'ttbar_part0.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
),
'ttbar_part1.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
),
'ttbar_part2.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
),
'ttbar_part3.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
),
'ttbar_part4.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
),
'ttbar_part5.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
),
'ttbar_part6.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
),
'ttbar_part7.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
),
'ttbar_part8.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
),
'ttbar_part9.root': CoffeaROOTFileSpecOptional(
object_path='Events',
steps=None,
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=None
)
}
),
'metadata': {'process': 'ttbar', 'cross_section': 831.8, 'is_signal': False},
'format': 'root',
'compressed_form': None,
'did': None
}
```
```
# 10.3 Promoting Specs to concrete types
print("=== Promoting Specs to Concrete Types ===")
print("ModelFactory.attempt_promotion can be used to update Spcs after parameters have been set, fulfilling the requirements of the non-Optional variants.")
starting_spec = CoffeaROOTFileSpecOptional(object_path="Events", steps=[[0, 1000]])
print("Starting with CoffeaROOTFileSpecOptional:")
rich.print(starting_spec)
starting_spec.num_entries = 1000
starting_spec.uuid = "promote-me"
print("After setting num_entries and uuid:")
rich.print(starting_spec)
promoted_spec = ModelFactory.attempt_promotion(starting_spec)
print("After promotion to CoffeaROOTFileSpec:")
rich.print(promoted_spec)
```
```
=== Promoting Specs to Concrete Types ===
ModelFactory.attempt_promotion can be used to update Spcs after parameters have been set, fulfilling the requirements of the non-Optional variants.
Starting with CoffeaROOTFileSpecOptional:
```
```
CoffeaROOTFileSpecOptional(
object_path='Events',
steps=[[0, 1000]],
num_entries=None,
format='root',
lfn=None,
pfn=None,
uuid=None,
num_selected_entries=1000
)
```
```
After setting num_entries and uuid:
```
```
CoffeaROOTFileSpecOptional(
object_path='Events',
steps=[[0, 1000]],
num_entries=1000,
format='root',
lfn=None,
pfn=None,
uuid='promote-me',
num_selected_entries=1000
)
```
```
After promotion to CoffeaROOTFileSpec:
```
```
CoffeaROOTFileSpec(
object_path='Events',
steps=[[0, 1000]],
num_entries=1000,
format='root',
lfn=None,
pfn=None,
uuid='promote-me',
num_selected_entries=1000
)
```
[previous
Dataset discovery tools](dataset_discovery.html)
[next
API Reference Guide](../api_reference.html)
On this page
* [Overview](#overview)
* [Table of Contents](#table-of-contents)
* [1. Basic File Specifications](#basic-file-specifications)
+ [File Specification Hierarchy](#file-specification-hierarchy)
* [2. InputFiles Specification](#inputfiles-specification)
* [3. Dataset Specifications](#dataset-specifications)
* [4. Fileset Specifications](#fileset-specifications)
* [5. Integration with Preprocessing](#integration-with-preprocessing)
* [6. Integration with apply\_to\_fileset](#integration-with-apply-to-fileset)
* [7. Dataset Manipulation Functions](#dataset-manipulation-functions)
* [8. Advanced Usage Examples](#advanced-usage-examples)
* [9. Migration from pure dictionary Formats and conversion utility ModelFactory](#migration-from-pure-dictionary-formats-and-conversion-utility-modelfactory)
* [ModelFactory](#modelfactory)
[Show Source](../_sources/notebooks/filespec.ipynb.txt)
© Copyright 2025, Fermi National Accelerator Laboratory.
Created using [Sphinx](https://www.sphinx-doc.org/) 7.4.7.
Built with the [PyData Sphinx Theme](https://pydata-sphinx-theme.readthedocs.io/en/stable/index.html) 0.17.1.

2.9s · markdown via readability

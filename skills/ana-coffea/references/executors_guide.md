# How to Scale with Executors (Coffea)

Source: https://coffea-hep.readthedocs.io/en/latest/user_guide/executors.html

## Overview

Coffea separates analysis logic from execution strategy. All executors implement the same interface consumed by `coffea.processor.Runner` — switch from local to cluster by changing only the `executor=` argument.

---

## IterativeExecutor

Sequential processing in the current Python process. Ideal for debugging and deterministic testing.

```python
runner = processor.Runner(
    executor=processor.IterativeExecutor(),
    schema=NanoAODSchema,
)
result = runner(fileset, processor_instance=my_processor)
```

---

## FuturesExecutor

CPU core parallelization on a single machine via `concurrent.futures`.

```python
from concurrent.futures import ThreadPoolExecutor

executor = processor.FuturesExecutor(
    workers=8,
    pool=ThreadPoolExecutor,  # optional: default is ProcessPoolExecutor
)
runner = processor.Runner(executor=executor, schema=NanoAODSchema)
result = runner(fileset, processor_instance=my_processor)
```

Key parameters:
- `workers`: number of parallel tasks
- `pool`: `ThreadPoolExecutor` or pre-constructed executor instance
- `merging`, `compression`: optimize throughput for large reductions

---

## DaskExecutor

Integrates with existing Dask clusters via `distributed.Client`.

```python
from dask.distributed import Client

client = Client("tcp://scheduler:8786")
runner = processor.Runner(
    executor=processor.DaskExecutor(client=client),
    schema=NanoAODSchema,
    savemetrics=True,
)
result, metrics = runner(fileset, processor_instance=my_processor)
```

- Use `client.upload_file` or package your environment to ensure workers have matching code
- `use_dataframes=True` returns Dask DataFrames

---

## ParslExecutor

Targets HPC systems via Parsl's `DataFlowKernel`.

```python
import parsl
from parsl.config import Config
from parsl.executors import HighThroughputExecutor

config = Config(executors=[HighThroughputExecutor(label="jobs")])
parsl.load(config)

executor = processor.ParslExecutor(config=config)
runner = processor.Runner(executor=executor, schema=NanoAODSchema)
result = runner(fileset, processor_instance=my_processor)
```

---

## TaskVineExecutor

Opportunistic and heterogeneous resources via TaskVine workflow engine. Stages processor code, data, and optional environment archives to connecting workers.

```python
executor = processor.TaskVineExecutor(
    port=9123,
    cores=2,
    disk=2048,
)
runner = processor.Runner(executor=executor, schema=NanoAODSchema)
result = runner(fileset, processor_instance=my_processor)
```

Coordinate workers via TaskVine CLI or Python APIs.

---

## Runner Configuration Parameters

| Parameter | Description |
|---|---|
| `schema` | NanoEvents schema class (e.g., `NanoAODSchema`) |
| `savemetrics=True` | Collect bytes read, columns touched, runtime stats |
| `checkpointer` | `processor.SimpleCheckpointer` for job persistence across restarts |
| `compression` | Default LZ4; set to `None` only for small accumulators |
| `chunksize` | Events per chunk (tune for memory/throughput trade-off) |
| `maxchunks` | Limit chunks for testing |

---

## Scaling Workflow

1. Prototype locally with `IterativeExecutor`
2. Parallelize on a single machine with `FuturesExecutor`
3. Scale to a cluster with `DaskExecutor` or `ParslExecutor`
4. Same processor code — only `executor=` changes

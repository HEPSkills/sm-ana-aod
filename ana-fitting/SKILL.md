----
name: ana-fitting
description:
---

# Final Analysis

Write and run the final analysis code (Including Data Preparation, Event Selection, Physics observable/object calculation, Fitting, Plotting)

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
from event_selector import *

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

2. **Event Selection and Physics observable/object calculation**

3. **Fitting**
   - Select one fitting tool (e.g. lmfit, pyhf)
   - Select the parameter of interests
   - Analyse the fitting model

4. **Plotting**
   - Use matplotlib and mplhep
   - Save figures to png and pdf.
   - DO NOT plt.show() .


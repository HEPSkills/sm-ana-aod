---
name: ana-setup-env
description: Use this skill when you need to initialize or troubleshoot the local environment for ATLAS Open Data analysis. It provides the necessary steps to install system-level dependencies and configures a Python virtual environment with essential High Energy Physics libraries. 
---

# Setup the environment

Recommended python version: 3.12

If no virtual environment `$HOME/.ana-venv`, follow the steps in (## Install dependencies) to set up the environment for analysis.

## Install dependencies

1. Install XRootD:
   - macOS: `brew install xrootd`
   - **Debian 11+/Ubuntu 22.04+**: `apt update && apt install build-essential cmake xrootd-client xrootd-server python3-xrootd`

2. Install Python Packages

```bash
python3 -m venv $HOME/.ana-venv
source $HOME/.ana-venv/bin/activate
pip install xrootd atlasopenmagic uproot awkward vector matplotlib mplhep pyyaml tqdm
```

3. Initialize from Python: `python3 -c "import sys; from atlasopenmagic import install_from_environment; install_from_environment()"`

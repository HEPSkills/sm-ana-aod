---
name: sm-ana-aod
description: Perform Standard Model searches and analysis using ATLAS Open Data. Use this skill when the user wants to analyze fundamental particles and forces, investigate Standard Model processes, or perform event selection and plotting using the ATLAS Open Data format and datasets.
---

# Standard Model Analysis with ATLAS Open Data (sm-ana-aod)

This skill provides a workflow for analyzing ATLAS Open Data to explore Standard Model physics.

## Overview

ATLAS Open Data provides simplified datasets (in ROOT format) for educational and research purposes. This skill helps in:
- Exploring Standard Model processes.
- Implementing event selection criteria (cuts).
- Calculating physical observables (invariant mass, transverse momentum, etc.).
- Generating histograms and plots.

## Workflow

1.  **Environment Setup**: Follow the [Environment Setup](#environment-setup) section to prepare the workspace.
2.  **Dataset Selection**: Identify the appropriate Standard Model samples (e.g., Single Electron, Single Muon, or MC samples for Z/W bosons).
3.  **Event Selection**: Apply selection criteria to isolate the process of interest.
4.  **Analysis & Plotting**: Calculate variables and visualize results.

## Environment Setup

Follow these steps to set up the analysis environment:

1.  **Attach to tmux session**: Ensure you are in a persistent tmux session.
2.  **Project Directory**: Navigate to or create your project base directory.
3.  **Python & Virtual Environment**: Ensure `python3.12` is available (install if missing).
    ```bash
    python3.12 -m venv venv
    source venv/bin/activate
    ```
4.  **Install XRootD**:
    - **macOS**: `brew install xrootd`
    - **Debian 11+/Ubuntu 22.04+**: `sudo apt install xrootd-client xrootd-server python3-xrootd`
5.  **Install python packages**:
    ```bash
    pip install xrootd atlasopenmagic
    ```
    Then, initialize from Python:
    ```python
    import sys
    from atlasopenmagic import install_from_environment
    install_from_environment()
    ```

## Resources

### References

- [ATLAS Open Data Documentation](https://opendata.atlas.cern/): Primary source for dataset information and analysis guides.

### Scripts

- Use Python with `uproot` for efficient data access.
- Use `awkward-array` for handling variable-length data in ROOT files.

## Guidelines

- Keep analysis scripts modular.
- Always validate the selection efficiency.
- Compare Data with Monte Carlo (MC) predictions where possible.

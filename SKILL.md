---
name: sm-ana-aod
description: Perform Standard Model searches and analysis using ATLAS Open Data. Use this skill when the user wants to analyze fundamental particles and forces, investigate Standard Model processes, or perform event selection and plotting using the ATLAS Open Data format and datasets.
---

# Standard Model Analysis with ATLAS Open Data (sm-ana-aod)

This skill provides a modular, production-ready framework for ATLAS Open Data analysis.

## Design Philosophy
- **Modern & Modular**: Separate data loading, selection, and plotting into reusable modules.
- **Config-Driven**: Use YAML files to define cuts, samples, and plotting parameters.
- **Iterative & Visual**: Output plots at each major step for validation.
- **Extensible**: Easy to add new functions or workflows.

## Project Structure (Recommended)
```text
analysis/
├── config/
│   ├── samples.yaml      # DID definitions, colors, labels
│   └── cuts.yaml         # Cutflow definitions
├── scripts/
│   ├── processor.py      # Core analysis loop (uproot/awkward)
│   ├── selection.py      # Physics selection functions
│   └── plotter.py        # Modern plotting (mplhep based)
└── main.py               # Entry point
```

## Workflow

1.  **Define Config**: Edit `config/cuts.yaml` to specify your selection (e.g., $E_T^{miss} > 150$ GeV, $n_{b-jets} == 2$).
2.  **Run Analysis**: Execute `main.py`. The processor will:
    - Download/Cache remote ROOT files via XRootD/HTTPS.
    - Apply the modular selection logic.
    - Save intermediate state for plotting.
3.  **Review Output**: Check the generated plots (e.g., `plots/cutflow.png`, `plots/m_bb_final.png`).

## Environment Setup

1.  **Attach to tmux session**: `tmux -S ${TMPDIR}/openclaw-tmux-sockets/openclaw.sock attach -t sm-ana-aod`
2.  **Install dependencies**:
    1. XRootD:
       - macOS: `brew install xrootd`
       - **Debian 11+/Ubuntu 22.04+**: `sudo apt install xrootd-client xrootd-server python3-xrootd`

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

## Resources
- [ATLAS Open Data](https://opendata.atlas.cern/)
- [mplhep Documentation](https://mplhep.readthedocs.io/en/latest/) (Preferred for HEP styling)

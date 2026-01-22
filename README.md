# XANES Analysis Tools

A collection of Python scripts for high-throughput XANES simulation and analysis, interfacing with the Materials Project API, FDMNES, and Parsl for parallel execution.

## Features

- **Database Creation**: Fetch material structures and properties from the Materials Project API (`create_db.py`).
- **Input Generation**: Automatically generate input files for FDMNES simulations (`create_fdmnes_inputs.py`).
- **Parallel Simulation**: Run FDMNES simulations in parallel across multiple nodes using Parsl (`parsl_fdmnes.py`).
- **Result Aggregation**: Collect and organize simulation results (`expand_db.py`).
- **Analysis & Plotting**: Tools for normalizing and plotting XANES spectra (`plot_xanes.py`, `exp_xanes_funcs.py`).

## Installation

1. Clone the repository.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1.  **Create Database**:
    ```bash
    python create_db.py
    ```
    This fetches structures from the Materials Project and saves them to `atoms_db.pkl`.

2.  **Generate Inputs**:
    ```bash
    python create_fdmnes_inputs.py
    ```
    This reads `atoms_db.pkl` and creates the directory structure and input files for FDMNES.

3.  **Run Simulations**:
    ```bash
    python parsl_fdmnes.py
    ```
    This executes the simulations on the configured computing resources. **Note**: Check and configure the `USER VARIABLES` section in `parsl_fdmnes.py` to match your HPC environment.

4.  **Process Results**:
    ```bash
    python expand_db.py
    ```
    This aggregates the simulation outputs.

## File Structure

- `create_db.py`: Fetches data from MP API.
- `create_fdmnes_inputs.py`: Prepares FDMNES inputs.
- `parsl_fdmnes.py`: Parallel execution script.
- `expand_db.py`: Post-processing and data aggregation.
- `plot_xanes.py`: Plotting utilities.
- `exp_xanes_funcs.py`: Experimental data handling.
- `fdmnes_funcs.py`: Core FDMNES IO functions.

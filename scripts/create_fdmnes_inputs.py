import shutil
import pickle
import os
from pathlib import Path
from xanes_bench import write_fdmnes_input

root_dir = Path(os.environ.get('PBS_O_WORKDIR', Path.cwd()))
if root_dir.name == 'fdmnes_batch_runs':
    root_dir = root_dir.parent
runs_dir = root_dir / 'fdmnes_batch_runs'

# If `fdmnes_batch_runs` exists, continue calculation from the largest `start_idx` found
start_idx = 0
if runs_dir.exists():
    for subdir in runs_dir.iterdir():
        try:
            start_idx = max(start_idx, int(subdir.name.split('_')[-1]))
        except ValueError:
            continue

    last_run = runs_dir / f'run_{start_idx}'
    if last_run.exists():
        shutil.rmtree(last_run)
else: # fresh start
    runs_dir.mkdir(parents=True)

# Loading DB
with open(root_dir / 'atoms_db.pkl', 'rb') as f:
    atoms_list = pickle.load(f)

# Creating the directory and input file (pickle preserves the order of the original list)
for i, atoms in enumerate(atoms_list, start=start_idx):
    curr_run_dir = runs_dir / f'run_{i}'
    curr_run_dir.mkdir(parents=True, exist_ok=True)

    z_absorber = max(atoms.get_atomic_numbers())
    write_fdmnes_input(ase_atoms=atoms,
                       input_file_dir=curr_run_dir,
                       z_absorber=z_absorber,
                       radius=6,
                       magnetism=False)

    # Writes a pickle file to store atoms object in order to match it with the FDMNES calc on the same dir
    pkl_filename = f'Z{z_absorber}_{atoms.info["MP-id"]}_{atoms.get_chemical_formula()}.pkl'
    with open(curr_run_dir / pkl_filename, 'wb') as f:
        pickle.dump(atoms, f)
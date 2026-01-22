import pickle
import os
from pathlib import Path
from fdmnes_funcs import extract_conv

root_dir = Path(os.environ.get('PBS_O_WORKDIR', Path.cwd()))
if root_dir.name == 'fdmnes_batch_runs':
    root_dir = root_dir.parent
runs_dir = root_dir / 'fdmnes_batch_runs'

if runs_dir.name != 'fdmnes_batch_runs':
    raise ValueError('You must submit the job or run the code from "fdmnes_batch_runs" or its parent directory!!')

# Iterating through the fdmnes_batch_runs directory
expanded_atoms_list = []
for sub_dir in runs_dir.glob('run_*'):
    # Unpickleling the atoms object inside it
    atoms_pkl_file = list(sub_dir.glob('*.pkl'))[0]
    with open(atoms_pkl_file, 'rb') as f:
        ase_atoms = pickle.load(f)

    # In case there are multiple _conv files because there are multiple Z_absorbers, what should I do? store each?
    ase_atoms.info.update({'FDMNES-xanes': extract_conv(fdmnes_output_dir=sub_dir)})

    expanded_atoms_list.append(ase_atoms)

# Pickleing expanded atoms list
with open(root_dir / 'atoms_db_expanded.pkl', 'wb') as f:
    pickle.dump(expanded_atoms_list, f)
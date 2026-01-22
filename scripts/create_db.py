import pickle
import os
from mp_api.client import MPRester
from pymatgen.io.ase import AseAtomsAdaptor
from pathlib import Path
# from pympler import asizeof

API_KEY = 'Pgvt9Q4pctLJeK7hDpB2F3ztUIjnDeym'
root_dir = Path(os.environ.get('PBS_O_WORKDIR', Path.cwd()))

atoms_list = []
with MPRester(API_KEY) as mpr:
    # querying the database
    doc_list = mpr.materials.summary.search(
        fields=['material_id', 'structure', 'xas', 'dos', 'symmetry'], # set of properties to fetch
        has_props=['dos', 'xas'],     # only fetching structures that have both 'dos' and 'xas'
        energy_above_hull=(0, 0.001), # only stable structs
        # is_metal=False, # only non-metallic (defined by band gap)
        # nelements=2, # filter by number of elements
        # elements=['Fe', 'O'], # only systems that contain `Fe` and/or `O`
        chemsys=['Fe2O3'],
        deprecated=False, # no deprecated structures
        num_chunks=1, # if None goes through the entire DB
        chunk_size=2, # size of each doc_list, larger is faster to avoid constantly querying the DB
    )

    for doc in doc_list:
        ase_atoms = AseAtomsAdaptor.get_atoms(doc.structure)
        # print(doc)
        # quit()
        ase_atoms.info.update({'MP-id' : str(doc.material_id),
                               'MP-xas': doc.xas,
                               'MP-dos': doc.dos})

        # print(asizeof.asizeof(ase_atoms) / 1024**2) # each atom object has ~0.03 MB, 90% being in info.
        atoms_list.append(ase_atoms)

# Pickling the list of atoms object. Up to ~1M structures can be pickled in a 32GB RAM system.
with open(root_dir / 'atoms_db.pkl', 'wb') as f:
    pickle.dump(atoms_list, f)


# MongoDB-style database. Each material entry is a "document". A document is similar to a JSON file (large dictionary)
# that contains all properties of that material. As if each document is a row in a spreadsheet and each property is
# a column (or "field"). We control which columns to retrieve through the field parameter.

# All fields present in MP database (not all structures have all of them)
# ['material_id', 'structure', 'chemsys', 'e_total', 'xas', 'dos',
# 'builder_meta', 'nsites', 'elements', 'nelements', 'composition', 'composition_reduced', 'formula_pretty',
# 'formula_anonymous', 'volume', 'density', 'density_atomic', 'symmetry', 'property_name', 'deprecated',
# 'deprecation_reasons', 'last_updated', 'origins', 'warnings', 'task_ids', 'uncorrected_energy_per_atom',
# 'energy_per_atom', 'formation_energy_per_atom', 'energy_above_hull', 'is_stable', 'equilibrium_reaction_energy_per_atom',
# 'decomposes_to','grain_boundaries', 'band_gap', 'cbm', 'vbm', 'efermi', 'is_gap_direct', 'is_metal',
# 'es_source_calc_id', 'bandstructure', 'dos', 'dos_energy_up', 'dos_energy_down', 'is_magnetic', 'ordering',
# 'total_magnetization', 'total_magnetization_normalized_vol', 'total_magnetization_normalized_formula_units',
# 'num_magnetic_sites', 'num_unique_magnetic_sites', 'types_of_magnetic_species', 'bulk_modulus', 'shear_modulus',
# 'universal_anisotropy', 'homogeneous_poisson', 'e_ionic', 'e_electronic', 'n', 'e_ij_max',
# 'weighted_surface_energy_EV_PER_ANG2', 'weighted_surface_energy', 'weighted_work_function', 'surface_anisotropy',
# 'shape_factor', 'has_reconstructed', 'possible_species', 'has_props', 'theoretical', 'database_Ids']

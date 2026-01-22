from ase import Atoms
from pathlib import Path
import numpy as np
from ase.io import read

def write_fdmnes_input(ase_atoms: Atoms,
                       z_absorber: int = None,
                       input_file_dir: Path = None,
                       radius: float = 6,
                       magnetism: bool = False,
                       ):
    if not isinstance(ase_atoms, Atoms):
        raise TypeError('ase_atoms must be an ase.Atoms object')

    atomic_numbers = ase_atoms.get_atomic_numbers()
    if z_absorber is None:
        z_absorber = atomic_numbers.max()

    if input_file_dir is None:
        input_file_dir = Path.cwd()

    with open(input_file_dir / 'fdmfile.txt', 'w') as f:
        f.write('1' + '\n')
        f.write('fdmnes_in.txt' + '\n')

    with open(input_file_dir / 'fdmnes_in.txt', 'w') as f:
        f.write('Filout' + '\n')
        f.write(f'{input_file_dir.name}' + 2*'\n')

        # Sets the energy mesh
        f.write('Range' + '\n')
        f.write('-55. 1.0 -10. 0.01 5. 0.1 150.' + 2*'\n')

        # Cluster Radius
        f.write('Radius' + '\n')
        f.write(f'{radius}' + 2*'\n')

        # Atomic number of the X-ray absorber
        f.write('Z_absorber' + '\n')
        f.write(f'{z_absorber}' + 2*'\n')

        # Enables magnetic contributions
        if magnetism:
            f.write('Magnetism' + 2*'\n')

        f.write('Green' + '\n')  # Use Green's function formalism for multiple scattering treatment
        f.write('Density_all' + '\n')  # Output total electron density for the cluster
        f.write('Quadrupole' + '\n')  # Include quadrupole transitions
        f.write('Spherical' + '\n')  # Start from spherical atomic densities
        f.write('SCF' + 2*'\n')  # Perform self-consistent field calculations on the cluster charge density

        if all(ase_atoms.pbc):
            f.write('Crystal' + '\n')

            # Writing cell lengths and angles
            f.write(' '.join(map(str, ase_atoms.cell.cellpar())) + '\n')

            # Atomic positions in fractional coordinates per required by periodic systems
            positions = np.round(ase_atoms.get_scaled_positions(), 6)

        else:
            f.write('Molecule' + '\n')

            # Writing cell lengths and angles
            cell_length = abs(ase_atoms.get_positions().max()) + abs(ase_atoms.get_positions().min())
            f.write(f'{cell_length} {cell_length} {cell_length} 90 90 90' + '\n')

            # Atomic positions in Cartesian coordinates per required by molecular systems
            positions = np.round(ase_atoms.get_positions(), 6)

        for i, position in enumerate(positions):
            f.write(f'{atomic_numbers[i]} ' + ' '.join(map(str, position)) + '\n')

        f.write('\n')
        f.write('Convolution' + '\n')
        f.write('End')


def get_normalized_xanes(conv_file: Path | str,
                         pre_edge_width: float=20.0,
                         post_edge_width: float=50.0,
                         calc_E0: bool=False
                         ) -> tuple[np.ndarray, np.ndarray]:
    energy_xas = np.loadtxt(conv_file, skiprows=1) # (N,2) array

    E = energy_xas[:, 0].astype(float)
    mu = energy_xas[:, 1].astype(float)

    # Finding edge energy E0 (onset of absorption) if file doesn't set 0 as reference
    if calc_E0:
        dmu_dE = np.gradient(mu, E)
        E0 = E[np.argmax(dmu_dE)]
    else:
        E0 = 0

    # Finding pre- and post-edge masks
    pre_mask = E <= (E0 - pre_edge_width)
    post_mask = E >= (E0 + post_edge_width)

    # Doing linear fits μ ~ m*E + b
    m_pre, b_pre = np.polyfit(E[pre_mask], mu[pre_mask], 1)
    m_post, b_post = np.polyfit(E[post_mask], mu[post_mask], 1)

    # Subtract pre-edge to shift the pre_line to mu = 0
    pre_line = m_pre*E + b_pre
    mu_corr = mu - pre_line

    # Computing normalized mu
    step = (m_post*E0 + b_post) - (m_pre*E0 + b_pre)
    mu_norm = mu_corr / step

    return np.column_stack([E, mu_norm]), energy_xas


def extract_conv(fdmnes_output_dir: Path | str) -> np.ndarray:
    if not isinstance(fdmnes_output_dir, Path):
        fdmnes_output_dir = Path(fdmnes_output_dir)

    energy_xas = {}
    for i, conv_file in enumerate(fdmnes_output_dir.glob('*conv.txt')):
        energy_xas[i] = np.loadtxt(conv_file, skiprows=1) # (N,2) array

    return energy_xas

def linear_combination_fitting(conv_list: list[np.ndarray]) -> np.ndarray:
    pass


struct = read('C:/Users/Vitor/Downloads/ANL/Cu_MnO2/(010)/center_2coord_H2O_CO/CONTCAR', format='vasp')
write_fdmnes_input(ase_atoms=struct,
                   z_absorber=29,
                   input_file_dir=Path('C:/Users/Vitor/Downloads/ANL/XANES'),
                   magnetism=False,
                   )
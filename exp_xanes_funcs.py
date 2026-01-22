import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from itertools import islice

# Under construction
class XANES:
    def __init__(self, energy = None, mu = None, metadata = None, xanes_file_path = None):
        if xanes_file_path is not None:
            self.energy, self.mu, self.metadata = XANES.extract_exp_xanes(xanes_file_path=xanes_file_path)
        else:
            self.energy = energy
            self.mu = mu
            self.metadata = dict()
            if isinstance(metadata, dict):
                self.metadata.update(metadata)
            else:
                raise ValueError('metadata must be a dict')

    # [incident intensity, transmission, Fe reference, fluorescence]
    # fluorescence/incident intensity or ln(abs(incident_intensity/transmission))

    def extract_exp_xanes(xanes_file_path: str | Path):
        """
        Extracts the XANES spectrum to a dataframe assuming commented lines in the beginning of the file starts with `#`
        and that the last commented line contains the names of the columns.
        """

        name_idx = 0
        n_fields = 0
        metadata_dict = {'beamline_name': '', 'date': '', 'edge_energy': ''}
        with open(xanes_file_path, 'r') as f:
            for i, line in enumerate(f):
                if line.startswith('#'):
                    for k in metadata_dict.keys():
                        if k in line:
                            metadata_dict[k] = line.split('=')[-1].strip(' ;"\n')
                else:
                    name_idx = i - 1
                    n_fields = len(line.split())
                    break

        with open(xanes_file_path, 'r') as f:
            names_line = next(islice(f, name_idx, name_idx + 1))

        # Creating dataframe
        col_names = names_line.rstrip(';\n').split()[-n_fields:]
        df = pd.read_table(xanes_path, skiprows=7, sep='\s+', names=col_names)

        # Sorting according to energy value
        df.sort_values(by='energy', inplace=True, ascending=True)

        return df['energy'].to_numpy(), df['energy'].to_numpy(), metadata_dict


# xanes_path = Path('C:/Users/Vitor/Downloads/Individual XAS scans/Fe_DM_FeN-3_1000.0002')
# xanes = XANES(xanes_file_path=xanes_path)
# print(xanes.mu.shape)

import numpy as np
import pandas as pd
from xanes_bench import get_normalized_xanes
from pathlib import Path
import matplotlib.pyplot as plt

# conv_file1 = Path(f'C:/Users/Vitor/Downloads/ANL/Cu_MnO2/(001)/center/XANES_conv.txt')
# conv_file2 = Path(f'C:/Users/Vitor/Downloads/ANL/Cu_MnO2/(010)/center_2coord/XANES_conv')
# conv_file3 = Path(f'C:/Users/Vitor/Downloads/ANL/Cu_MnO2/(010)/center_4coord/XANES_conv.txt')
# conv_file4 = Path(f'C:/Users/Vitor/Downloads/ANL/Cu_MnO2/(010)/center_2coord_CO/XANES_conv.txt')

# conv_file1 = Path(f'C:/Users/Vitor/Downloads/ANL/Cu_MnO2/(001)/center_CO/XANES_conv.txt')
# conv_file2 = Path(f'C:/Users/Vitor/Downloads/ANL/Cu_MnO2/(010)/side/XANES_conv.txt')
# conv_file3 = Path(f'C:/Users/Vitor/Downloads/ANL/Cu_MnO2/(010)/Cu_sub/XANES_conv.txt')
conv_file4 = Path(f'C:/Users/Vitor/Downloads/ANL/Cu_MnO2/(010)/center_2coord_H2O_CO/XANES_conv.txt')
# conv_file5 = Path(f'C:/Users/Vitor/Downloads/ANL/Cu_MnO2/(010)/Cu_sub_tetra/XANES_conv.txt')

# norm_energy_xas1, energy_xas1  = get_normalized_xanes(conv_file1, pre_edge_width=20, post_edge_width=50)
# norm_energy_xas2, energy_xas2  = get_normalized_xanes(conv_file2, pre_edge_width=20, post_edge_width=50)
# norm_energy_xas3, energy_xas3  = get_normalized_xanes(conv_file3, pre_edge_width=20, post_edge_width=50)
norm_energy_xas4, energy_xas4  = get_normalized_xanes(conv_file4, pre_edge_width=20, post_edge_width=50)
# norm_energy_xas5, energy_xas5  = get_normalized_xanes(conv_file5, pre_edge_width=20, post_edge_width=50)


# fig, ax = plt.subplots()
# ax.plot(norm_energy_xas1[:,0], norm_energy_xas1[:,1], lw=1.5, color='royalblue', label='(001) - Center')
# ax.plot(norm_energy_xas2[:,0], norm_energy_xas2[:,1], lw=1.5, color='crimson', label='(010) - 2 coord')
# ax.plot(norm_energy_xas3[:,0], norm_energy_xas3[:,1], lw=1.5, color='seagreen', label='(010) - 4 coord')
# ax.plot(norm_energy_xas4[:,0], norm_energy_xas4[:,1], lw=1.5, color='goldenrod', label='(010) - 3 coord (CO)')
# ax.plot(norm_energy_xas5[:,0], norm_energy_xas4[:,1], lw=1.5, color='pink', label='(010) - 3 coord (CO)')

# ax.plot(norm_energy_xas1[:,0], norm_energy_xas1[:,1], lw=1.5, color='orangered', label='(001) - Center CO')
# ax.plot(norm_energy_xas2[:,0], norm_energy_xas2[:,1], lw=1.5, color='crimson', label='(010) - Side')
# ax.plot(norm_energy_xas3[:,0], norm_energy_xas3[:,1], lw=1.5, color='seagreen', label='(010) - Sub')
# ax.plot(norm_energy_xas4[:,0], norm_energy_xas4[:,1], lw=1.5, color='goldenrod', label='(010) - Small Sq 1')
# ax.plot(norm_energy_xas5[:,0], norm_energy_xas5[:,1], lw=1.5, color='darkorchid', label='(010) - Small Sq 2')

# ax.plot(norm_energy_xas4[:,0], norm_energy_xas4[:,1], lw=1.5, color='goldenrod', label='(010) - Center 2-coord 2H2O')
# ax.plot(norm_energy_xas5[:,0], norm_energy_xas5[:,1], lw=1.5, color='darkorchid', label='(010) - Cu Sub. Tetra')
#
df = pd.DataFrame(norm_energy_xas4)
df.to_excel(conv_file4.parent / 'norm_xanes.xlsx')
plt.plot(energy_xas4[:,0], energy_xas4[:,1], lw=1.5, color='red', label='Non-normalized spectrum')
plt.show()
quit()

# ax.set_xlabel('Energy [eV]')
# ax.set_ylabel(r'$\mu_{\mathrm{norm}}$')
# plt.legend()
# plt.show()
# fig.savefig(f'C:/Users/Vitor/Downloads/ANL/XANES/Cu_XANES_energy2.png', dpi=200)


## Savinge excel files
# root_dir =  Path('C:/Users/Vitor/Downloads/ANL/Cu_MnO2/')
# all_xanes = []
# for xanes_file in root_dir.rglob('XANES_conv.txt'):
#     print(xanes_file)
#     norm_xanes, _ = get_normalized_xanes(xanes_file, pre_edge_width=20, post_edge_width=50)
#
#     all_xanes.append(norm_xanes)
#
# all_xanes = np.hstack(all_xanes)
# df = pd.DataFrame(all_xanes)
# print(df.head())
# df.to_excel('C:/Users/Vitor/Downloads/ANL/Cu_MnO2/all_xanes_corr.xlsx')

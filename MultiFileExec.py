import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

import selfMadeFunction as sefu # "se"lfMade"Fu"nction 自作関数

plt.rcParams["font.size"] = 20



directory_list=sefu.get_directory_list()

fig_multi_meanvelocity_RMS=plt.figure(figsize=(15,10)) # 三つ入った図の大きさ指定

first_dir=os.getcwd()

list_081415=['0000Hz','0800Hz','1400Hz','1500Hz']

for i in range(len(list_081415)):

    os.chdir(list_081415[i])
    csvfile_list=sefu.get_csvfile_name_List()
    file_num_list=sefu.get_file_name_number(csvfile_list)

    axes_row=np.arange((file_num_list[0]-53)/10,(file_num_list[-1]-53)/10+0.01,0.4)

    probe1_data_vmean,probe1_data_std=sefu.get_mean_and_RMS()

    print('row')
    for j in axes_row:
        print(j)
    print("std")
    for j in probe1_data_std:
        print(j)
    print("vmean")
    for j in probe1_data_vmean:
        print(j)


    array_vmean=np.array(probe1_data_vmean)+i*1.5
    array_std=np.array(probe1_data_std)+i*3

    axes_vmean=fig_multi_meanvelocity_RMS.add_subplot(2,1,1)
    axes_vmean.plot(array_vmean,axes_row,  linestyle='-',marker="o", markersize=4.0,color="b")
    axes_vmean.axvline(i*1.5, ls = "-", color = "k")
    axes_vmean.axvline(i*1.5+1,ls="--",color="k")

    axes_std=fig_multi_meanvelocity_RMS.add_subplot(2,1,2)
    axes_std.plot(array_std,axes_row,  linestyle='-',marker="o", markersize=4.0,color="r")
    axes_std.axvline(i*3, ls = "-", color = "k")
    axes_std.axvline(i*3+1.5,ls="--",color="k")

    print(list_081415[i])
    os.chdir(first_dir)

axes_vmean.axvline(1.5, ls = "-", color = "k",label="0 [-]")
axes_vmean.axvline(1.5+1,ls="--",color="k",label="1 [-]")
axes_std.axvline(3, ls = "-", color = "k",label="0 [-]")
axes_std.axvline(3+1.5,ls="--",color="k",label="1.5 [-]")

axes_vmean.set_xlabel("mean velocity  [-]")
axes_std.set_xlabel("turbulence intensity [-]")
axes_std.legend()

axes_vmean.set_ylabel("z/h [-]")
axes_std.set_ylabel("z/h [-]")
axes_vmean.legend(loc='upper right')
axes_std.legend(loc='upper right')


axes_vmean.set_xlim(0,1.5*len(list_081415))
axes_std.set_xlim(0,3*len(list_081415))

axes_vmean.tick_params(labelbottom=False)
axes_std.tick_params(labelbottom=False)

fig_multi_meanvelocity_RMS.savefig("VmeanAndStd_1000")

plt.show()

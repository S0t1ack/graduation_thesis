#以下起動する前にやることリスト
#csvファイルは等間隔に何かを計測したものであること
# ➤等間隔でないとグラフがおかしくなる(表示はできる)
#サンプリング周波数(fs = ～)を計測したときの値に変える
#コンター図分割と，スペクトル上限をいくらまで取るか指定する(スペクトル上限は指定の値以上はカットする)
#起動する前にcsvと同じディレクトリに入れる
#Anaconda promptを開き，python　(これのファイル名).pyと打って起動

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import ticker

import selfMadeFunction as sefu # "se"lfMade"Fu"nction 自作関数

plt.rcParams["font.size"] = 24

probe1_data_std=[] # probe1の標準偏差
probe1_data_vmean=[] # probe1の平均速度

fs=10000  # サンプリング周波数 100Hz => 10m秒間隔でサンプリング

h=1.5 # 出口幅

e=2.718281828459045
# カレントディレクトリのファイル名取得
csvfile_list=sefu.get_csvfile_name_List()
file_num_list=sefu.get_file_name_number(csvfile_list)
file_sum=len(csvfile_list) # csvファイルの合計

contour_div=200 # コンター図の分割
figure_max_spectrum=100000 # コンター図の色の上限

contour_div_list_at_logver=[]
contour_div_list_at_logver=sefu.get_contour_div_list_at_logver(contour_div,figure_max_spectrum)

fig_column_first_num=float(input("縦軸の下限値(一番上のファイルの数字)を入力してください(半角 マイナスも小数点も可):"))
# 縦軸の下限値
fig_column_distance=float(input("縦軸はいくら刻みであるかを入力してください(半角 小数点も可):"))
# いくら刻みの値か
fig_column_last_num=fig_column_first_num+fig_column_distance*file_sum
# 縦軸の上限値

#read_data=int(input("読み込むデータ(Probe1なら3 Probe2なら4を入力(半角)):"))
read_data=3
probe_no=read_data-2 # どちらのProbeか

N=len(pd.read_csv(csvfile_list[0],header=13).iloc[0:,read_data].values.flatten())
    # 一番上のファイルのNを取得

fft_two_nparray=np.empty((0,N),int) # 0が入ってるnparrayを予め作る必要

fig_two_dimension_fft=plt.figure(figsize=(15,6)) # 三つ入った図の大きさ指定

    # fftの図を作るための配列作成 平均流速と乱れ強さも作成している
for j in range(file_sum):
    data=pd.read_csv(csvfile_list[j],header=13).iloc[0:,read_data].values.flatten()
        #csvファイルの13行目から読み込んでいる．
        #iloc[First, Second]Firstで何行目から読み込むか Secondで何列目を読み込むか

    data_reshape=sefu.reshape_vector_scale(data,N) # dataをNの大きさに成形 足りない分は後ろに0を追加(Hanning窓でどっちみち0になる)

    frequency_list,amplitude_spectrum=sefu.get_fft_list(fs,data_reshape) # fft配列取得


    probe1_data_vmean.append(np.mean(data_reshape)) # 平均速度をリストに追加
    probe1_data_std.append(np.std(data_reshape)) # 標準偏差をリストに追加

    amplitude_spectrum_modified=sefu.modify_list_to_calc_contourf_in_fft_at_logver(amplitude_spectrum,figure_max_spectrum)
        # 得たスペクトルを配列に追加する前に計算負荷が少なくなるようにスペクトルを成形

    fft_two_nparray=sefu.add_vector_to_2array(fft_two_nparray,amplitude_spectrum_modified) #fft_two_nparrayに1×Nのベクトルを挿入
    print("読み込んでいるファイル："+str(csvfile_list[j]))

axes_column_tmp=sefu.get_file_name_number(csvfile_list) # ファイル名の数字を取得

axes_row_fft,axes_column_fft=np.mgrid[0 : fs : fs/N,
                                      fig_column_first_num : fig_column_last_num : fig_column_distance]
                                      # メッシュを切ってる meshgrid()関数では表示がバグったからmgrid()を使用

axes_row=np.arange(fig_column_first_num,fig_column_last_num,fig_column_distance) # 全体のための縦軸用意 小数以下を扱うためにnp.arange()にしている

    # 平均流速の図
axes_vmean=fig_two_dimension_fft.add_subplot(1,2,1)
axes_vmean.plot(probe1_data_vmean,axes_row,  linestyle='--',marker="o", markersize=5.0,color="b")
axes_vmean.set_ylim(min(axes_row),max(axes_row))
axes_vmean.set_xlim(0,15)
axes_vmean.set_xlabel("velocity  [m/s]")
axes_vmean.set_ylabel("z/h [-]")

    # 乱れ強さの図
axes_std=fig_two_dimension_fft.add_subplot(1,2,2)
axes_std.plot(probe1_data_std,axes_row,  linestyle='--',marker="o", markersize=5.0,color="r")
axes_std.set_ylim(min(axes_row),max(axes_row))
axes_std.set_xlim(0,2.5)
axes_std.set_xlabel("turbulence intensity [-]")

    # fftの図(大きい版)
fig_with_colorbar=plt.figure(figsize=(20,8))
plt.contourf(axes_row_fft,axes_column_fft,fft_two_nparray.T,cmap="plasma",locator=ticker.LogLocator(),levels=contour_div_list_at_logver)
plt.colorbar()
plt.axis([0,fs/2,fig_column_first_num,fig_column_last_num-fig_column_distance]) #軸の表示範囲
plt.ylabel("z/h [-]")
plt.xlabel("Frequency [Hz]")

    # 図の保存
fig_with_colorbar.savefig("2dimensiofftProbe"+str(probe_no))
fig_two_dimension_fft.savefig("2dimensionalfftandintensityandvelocityProbe"+str(probe_no))
plt.show()

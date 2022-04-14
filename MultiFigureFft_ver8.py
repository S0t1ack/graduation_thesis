#以下起動する前にやることリスト
#サンプリング周波数(fs = ～)を計測したときの値に変える
#起動する前にcsvと同じディレクトリに入れる
#Anaconda promptを開き，python　(これのファイル名).pyと打って起動
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import selfMadeFunction as sefu

probe1_data_vmean=[] # probe1の平均速度
probe1_data_std=[] # probe1の標準偏差

#fs=int(input("サンプリング周波数:")) # サンプリング周波数を標準入力で受け取る
fs=10000                             # サンプリング周波数 100Hz => 10m秒間隔でサンプリング
read_data=int(input("読み込むデータ(Probe1なら3 Probe2なら4を入力(半角)):"))
probe_no=read_data-2

fft_figure=plt.figure(figsize=(16,8)) # FFTを表示する図の宣言と全体の大きさ指定
std_and_vmean_figure=plt.figure(figsize=(8,8)) # 乱れ強さと平均流速を表示する図の宣言と全体の大きさ指定

figure_max_spectrum=20000 # 図に表示する最大の振幅スペクトル

csvfile_list=sefu.get_csvfile_name_List() # csvファイルのリスト取得
figure_array_row,figure_array_column=sefu.get_figure_array(csvfile_list) # 図を横・縦にいくつ配置するかを取得
file_sum=len(csvfile_list) # csvファイルの合計

ax=[0]*file_sum # 一つ一つのグラフ file_sumの大きさの0が入ったリストを作成
               # これがないと配列外参照するなと怒られる

for j in range(file_sum):
    data=pd.read_csv(csvfile_list[j],header=13).iloc[0:,read_data].values.flatten()
    #iloc[First, Second]Firstで何行目から読み込むか Secondで何列目を読み込むか
    #何列目を読み込むかを変更することでどのプローブを読み込むか指定できる

    frequency_list,amplitude_spectrum=sefu.get_fft_list(fs,data)

    ax[j]=fft_figure.add_subplot(figure_array_row,figure_array_column,j+1)
    # 振幅スペクトル
    ax[j].plot(frequency_list, amplitude_spectrum,  linestyle='-')
    ax[j].axis([0, fs/2, 0, figure_max_spectrum])
    ax[j].text(fs/4,figure_max_spectrum*3/4,csvfile_list[j],color="#72777b") # ファイル名 text()の最初二つの引数はx，y座標，三つ目は表示するテキスト

    probe1_data_vmean.append(np.mean(data)) # データの平均速度をリストに追加
    ax[j].text(fs/4,figure_max_spectrum/2,'Vmean:'+str(round(probe1_data_vmean[j],2)),color="#72777b") # 平均速度 小数第二位で四捨五入

    probe1_data_std.append(np.std(data)) # 標準偏差をリストに追加
    ax[j].text(fs/4,figure_max_spectrum/4,'RMS:'+str(round(probe1_data_std[j],2)),color="#72777b") # 標準偏差(乱れ強さ) 小数第二位で四捨五入

    print("読み込んでいるファイル："+csvfile_list[j])
fft_figure.suptitle('probe'+str(probe_no),size=30)

# probe1の乱れ強さグラフ
axes_std_and_vmean_row=list(range(0,file_sum,1)) # 平均流速と乱れ強さを表示するグラフの横軸配列
                                            # 横軸をmmや周波数にしたい場合はこれをいじること

axes_probe1_data_std=std_and_vmean_figure.add_subplot(2,1,1)
axes_probe1_data_std.plot(axes_std_and_vmean_row,probe1_data_std, linestyle='None',marker="o", markersize=4.0,color="r")
axes_probe1_data_std.set_xlim(min(axes_std_and_vmean_row),max(axes_std_and_vmean_row))
axes_probe1_data_std.set_ylim(0,1.5)

axes_probe1_data_std.set_ylabel("turbulence intensity [-]")

axes_probe1_data_vmean=std_and_vmean_figure.add_subplot(2,1,2)
axes_probe1_data_vmean.plot(axes_std_and_vmean_row,probe1_data_vmean,linestyle='None',marker="o", markersize=4.0,color="b")
axes_probe1_data_vmean.set_xlim(min(axes_std_and_vmean_row),max(axes_std_and_vmean_row))
axes_probe1_data_vmean.set_ylim(0,15)

axes_probe1_data_vmean.set_xlabel("file [-]")
axes_probe1_data_vmean.set_ylabel("velocity  [m/s]")

std_and_vmean_figure.suptitle('probe1')

fft_figure.savefig("fft_figureProbe"+str(probe_no))
std_and_vmean_figure.savefig("std_and_vmean_figureProve"+str(probe_no))

plt.show()

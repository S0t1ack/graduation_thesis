#以下起動する前にやることリスト
#サンプリング周波数(fs = ～)を計測したときの値に変える
#起動する前にcsvと同じディレクトリに入れる
#Anaconda promptを開き，python　(これのファイル名).pyと打って起動
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import selfMadeFunction as sefu


csvfile_list=sefu.get_csvfile_name_List() # csvファイルのリスト取得
figure_array_row,figure_array_column=sefu.get_figure_array(csvfile_list) # 図を横・縦にいくつ配置するかを取得
file_sum=len(csvfile_list) # csvファイルの合計

probe1_data_vmean=[] # probe1の平均速度
probe1_data_std=[] # probe1の標準偏差

figure_max_spectrum=20000 # 図に表示する最大の振幅スペクトル

fft_figure=plt.figure(figsize=(16,8)) # FFTを表示する図の宣言と全体の大きさ指定

ax=fft_figure.add_subplot(1,1,1)

read_data=3


#1つ目のプローブ(Excel3列目)

for j in range(file_sum):
    data=pd.read_csv(csvfile_list[j],header=13).iloc[0:,read_data].values.flatten()
    #iloc[First, Second]Firstで何行目から読み込むか Secondで何列目を読み込むか
    #何列目を読み込むかを変更することでどのプローブを読み込むか指定できる
    fs=10000

    frequency_list,amplitude_spectrum=sefu.get_fft_list(fs,data)

    ax.plot(frequency_list,amplitude_spectrum,alpha=0.5,color=[0.5,0,(1/file_sum)*j]) # alphaでプロット線の透明度を指定(1が最大) colorはRGB値で指定(1が最大)

    print("読み込んでいるファイル："+csvfile_list[j])

ax.axis([0, fs/2, 0,figure_max_spectrum]) # 軸の範囲の指定

fft_figure.suptitle('probe1',size=30)
fft_figure.savefig("Spectrum_vs_InputFrequency.png") # figureオブジェクトのfigを保存

plt.show()

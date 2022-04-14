# いろいろ自作関数
# __init__.pyの意味などはhttps://qiita.com/FN_Programming/items/2dcabc93365a62397afeを参照した

import numpy as np
import scipy.fftpack
import pandas as pd
from scipy import signal
import math
import os
import re

# サンプリング周波数と測定データを引数にしてFFTした後
# Matplotlibで表示させるためのリストを二つ返す
def get_fft_list(sampling_frequency,originaldata):
    originaldata_detrend=signal.detrend(originaldata)
    #元信号のトレンド除去
    #最小二乗法で回帰分析を行い，元信号から回帰分析分を引いている

    start=0 #サンプリングする開始位置
    N=len(originaldata_detrend) # FFTのサンプル数 読み込んだ配列の大きさ

    han=signal.hann(N) # hanning窓

    lowpass_filter=signal.firwin(numtaps=21,cutoff=sampling_frequency/2-1,fs=sampling_frequency)
    #2020/10/04着手 lowpass_filterの作成
    #numtapsはよくわからん cutoffで切る周波数を選択 fs/2未満にしろと怒られたからfs/2-1にした
    #参照(https://helve-python.hatenablog.jp/entry/2018/06/18/000000)

    originaldata_detrend_lowpass=signal.lfilter(lowpass_filter,1,originaldata_detrend)
    #lowpass_filterをかけている
    #デジタル処理のローパスフィルタをかけているわけだがこれでいいのか疑問
    #AnalogDiscovery2の方で元からかかっているかもしれない
    #元からかかっているならこの処理はしてもしなくてもよい

    originaldata_detrend_lowpass_window=han*originaldata_detrend_lowpass
    #ハニング窓関数をかけている，計算は，窓関数ベクトルと信号ベクトルの内積を計算している

    originaldata_detrend_lowpass_window_fft=scipy.fftpack.fft(originaldata_detrend_lowpass_window[start:start+N])
    #ScipyでFFTをStartからStart+Nの位置でかけている
    #FFTは配列の大きさと配列の値のみに依存する(サンプリング周波数は考慮されていない)
    #詳細は離散フーリエ変換の定義を参照

    frequency_list=scipy.fftpack.fftfreq(N,d=1.0/sampling_frequency)
    #ScipyでかけたFFTのグラフを作成するために，横軸の配列を作成
    #このリストはサンプリング点の数とサンプリング周波数のみに依存する

    amplitude_spectrum=[np.sqrt(c.real ** 2 + c.imag ** 2) for c in originaldata_detrend_lowpass_window_fft]
    #複素フーリエ級数×2πから振幅スペクトルを求めている
    #振幅スペクトル配列作成

    return frequency_list, amplitude_spectrum

# カレントディレクトリのファイル名取得
def get_csvfile_name_List():
    file_name=[] # ファイル名リスト
    for file in os.listdir():
        base, ext = os.path.splitext(file)
        if ext == '.csv' or ext == ".CSV": # .csvがついているならば以下を実行
            file_name.append(file) # ファイル名リストに追加
    return file_name

# 図にどのようにファイルを並べるかの調整
# 引数はカレントディレクトリのファイルが入ったリスト
def get_figure_array(file_list):
    figure_array_row_max=5 # 最大の行 図が気に入らなかったらここを調整すると綺麗になるかも
    if len(file_list) < figure_array_row_max:
        figure_array_row=len(file_list) # 最大の行以下のファイル数なら一列に並べる
        figure_array_column=1 #列が一つ
    else:
        figure_array_row=figure_array_row_max # 行の数がfileyokolim
        figure_array_column=math.ceil(len(file_list)/figure_array_row_max) # 切り上げ ex.)11なら2列
    return figure_array_row, figure_array_column

def add_vector_to_2array(two_nparray,vector):
    two_nparray=np.append(two_nparray,np.array(vector).reshape(1,-1),axis=0)
    # twoNpArrayに1×len(vector)のベクトルを追加
    return two_nparray # 追加した配列を返す

# ベクトルを指定された大きさにそろえる
def reshape_vector_scale(vector,N):
    if len(vector)<N: # 渡された配列の大きさがNより小さければ以下を実行
        print("配列の大きさが指定された数よりも小さいです 足りない分は最後に0を挿入します\n"
                + "渡された配列の大きさ:"+str(len(vector))+"\n"
                + "Nの大きさ"+str(N))
        while len(vector)<N: # 渡された配列の大きさがN未満の間は以下を実行
            vector=np.append(vector,0) # 0を配列の最後に追加
    elif len(vector)>N:
        while len(vector)>N: # 渡された配列の大きさがN超過の間は以下を実行
            vector=np.delete(vector,-1) # 配列の最後の値を削除
    return vector

# 引数に渡したリストのうち数字部分だけを格納する
def get_file_name_number(file_list):
    file_name_number_list=[]
    for p in file_list:
        file_name_number_list.append(int(re.sub("\\D","",p))) # 与えられたリストの要素の数字部分だけを収納
    return file_name_number_list

# 数字だけが入ったリストを引数に，軸がz方向の変位となる図を作るための配列を作成する関数
def get_high_figure_array_row(file_num_list):
    figure_array_row_high=[]
    for p in file_num_list:
        figure_array_row_high.append((53-p)*0.1) # 53を中心にとり，0.1ごとにずらしていることが前提
    return figure_array_row_high

# contourfを高速化するためfftの負の周波数領域の要素に0を代入し，各値をdivide_numの分割に合わせた値にする
# scipyfftで計算したときにのみ使える？numpyfftで計算するとおかしくなるかも
def modify_list_to_calc_contourf_in_fft_at_logver(spectrum_list,max_spectrum):
    for k in range(int(len(spectrum_list)/2)):  # fftは周波数領域にて偶関数となるため，半分だけ計算すればよい
        spectrum_list[-k] = 0                   # 配列の最後からk番目の要素に0を代入 contourfの高速化狙い
        spectrum_list[k] = int(spectrum_list[k]) # 元の値にdivide_numに合わせた分割を行う
        if spectrum_list[k] <= 1:                # 1以下の値は1.0000001を代入
            spectrum_list[k] = 1.0000001         # 1だとLogスケールで表せない(白い部分が出てくる)
        if spectrum_list[k] > max_spectrum: # divide_numより大きい値があればdivide_numに書き換える
            spectrum_list[k] = max_spectrum
    return spectrum_list

# logのコンター図を作りたいときに使う levelを指定するための配列を作っている
def get_contour_div_list_at_logver(divide_num,max_spectrum):
    contour_div_list_at_logver=[]
    for k in range(divide_num):
        contour_div_list_at_logver.append(10**(logarithm(max_spectrum)/divide_num*k))
    return contour_div_list_at_logver

# contourfを高速化するためfftの負の周波数領域の要素に0を代入し，各値をdivide_numの分割に合わせた値にする
# scipyfftで計算したときにのみ使える？numpyfftで計算するとおかしくなるかも
def modify_list_to_calc_contourf_in_fft(spectrum_list,divide_num,max_spectrum):
    for k in range(int(len(spectrum_list)/2)):  # fftは周波数領域にて偶関数となるため，半分だけ計算すればよい
        spectrum_list[-k] = 0                   # 配列の最後からk番目の要素に0を代入 contourfの高速化狙い
        spectrum_list[k] = int(spectrum_list[k]*divide_num/max_spectrum) # 元の値にdivide_numに合わせた分割を行う
        if spectrum_list[k] > divide_num: # divide_numより大きい値があればdivide_numに書き換える
            spectrum_list[k] = divide_num
    return spectrum_list

def logarithm(value):
    try:
        return math.log10(value)
    except ValueError:
        return -1000000

#カレントディレクトリ内のディレクトリを返す
def get_directory_list():
    path=os.getcwd()
    files = os.listdir(path)
    directory_list = [f for f in files if os.path.isdir(os.path.join(path, f))]
    return directory_list

#カレントディレクトリのcsvファイルの平均速度と乱れ強さ取得
def get_mean_and_RMS():

    # カレントディレクトリのファイル名取得
    csvfile_list=get_csvfile_name_List()
    file_num_list=get_file_name_number(csvfile_list)
    file_sum=len(csvfile_list) # csvファイルの合計

    probe1_data_std=[] # probe1の標準偏差
    probe1_data_vmean=[] # probe1の平均速度

    for j in range(file_sum):
        data=pd.read_csv(csvfile_list[j],header=13).iloc[0:,3].values.flatten()
        probe1_data_vmean.append(np.mean(data)/10.59) # 無次元平均速度をリストに追加
        probe1_data_std.append(np.std(data)) # 標準偏差をリストに追加

    return probe1_data_vmean,probe1_data_std

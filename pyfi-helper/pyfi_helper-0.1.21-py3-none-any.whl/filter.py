# author Huang Ren, Qi Haoling
import numpy as np
from scipy import signal
import pandas as pd
import matplotlib.pyplot as  plt
import matplotlib as mpl
from pyfi import line_graph

mpl.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
mpl.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

def frequency_energy(raw):
  """
  通过傅里叶变换，展示原始序列的傅里叶变换频谱图
  并把波峰标出
  输入：
  raw: Series格式的原始序列
  输出：
  傅里叶变换频谱图
  """
  # 判断输入是否是series
  if str(type(raw))[-8:-2]!='Series':
     return "输入的序列不是Series格式哦，请重新输入"
 
  n = len(raw)
  num=1024
  if int(n/1024)==0:
      num = 1024
  else:
      tmp = int(n/1024)
      num = num*tmp
  fft_size = num*4#需要大于原序列数据个数
  seq = raw#获取表格中第3列的数据
  seq_log = np.array(seq)#生成数组
  dseq_log = seq_log#也可以选择去趋势项 signal.detrend(seq_log)，但是去趋势可能导致滤波后序列和原序列的数量级出现差别
  peak_num_min=3#取前3大能量值
  peak_num_max=10#考察前几大能量值
  
  #构造一个新的序列用于构建频域图的X轴
  freq_index = [i for i in range(fft_size)]
  freq_index[:int(fft_size/2+1)] = [i/fft_size for i in range(0,int(fft_size/2+1))]
  freq_index[int(fft_size/2+1):] = [i/fft_size for i in range(int(-fft_size/2+1),0)]#重新定义一个序列
  
  #傅里叶变换
  data_fft = abs(np.fft.fftshift(np.fft.fft(dseq_log, fft_size)))#对程序输入的时间序列进行快速傅里叶变换，并进行移频
  freq_index = np.fft.fftshift(freq_index)#对重新定义的序列进行移频，把位于边缘的图像移动到中心，中心移动到边缘（平移）
  
  #找到频域的峰
  loc_raw = list(signal.find_peaks(data_fft[int(fft_size/2):])[0])#找到频域的峰所在位置
  peak_raw = data_fft[int(fft_size/2):][loc_raw]#在频域序列中标注峰
  data_dict = { key: value for key,value in zip(loc_raw,peak_raw)}#将峰值的位置和值表示在一起
  temp = sorted(data_dict.items(),key=lambda x:x[1],reverse=True)#对峰值按照值的大小进行排序，大的在前
  loc_peaks_max = temp[:peak_num_max]#取前peak_num_max大峰的位置
  loc_peaks_min = temp[:peak_num_min]#取前3大峰的位置
  power=data_fft[int(fft_size/2+1):]
  #画图，标注峰值
  plt.figure(figsize=(20,10),dpi=100)#图片大小
  plt.plot(freq_index[int(fft_size/2+1):],data_fft[int(fft_size/2+1):])
  plt.grid(True)
  plt.xlabel('频率(Hz)')
  plt.ylabel('幅度')
  for i in range(peak_num_max):
    plt.text(freq_index[loc_peaks_max[i][0]+int(fft_size/2-1)],loc_peaks_max[i][1],'['+\
    str(round(freq_index[loc_peaks_max[i][0]+int(fft_size/2-1)],4))\
    +','+str(round(loc_peaks_max[i][1],4))+']')#在图上标记坐标，【频率，能量值】


def f_filter(raw, weight_votality):
    """
    时域层面的滤波
    :param raw:
    :param weight_votality:
    :return:
    """
    fft_size = 1024 * 4  # 需要大于原序列数据个数
    seq = raw.iloc[:]  # 获取表格中第3列的数据
    seq_log = np.array(seq)  # 生成数组
    dseq_log = seq_log  # 也可以选择去趋势项 signal.detrend(seq_log)，但是去趋势可能导致滤波后序列和原序列的数量级出现差别
    peak_num_min = 3  # 取前3大能量值
    peak_num_max = 10  # 考察前几大能量值

    # 构造一个新的序列用于构建频域图的X轴
    freq_index = [i for i in range(fft_size)]
    freq_index[:int(fft_size / 2 + 1)] = [i / fft_size for i in range(0, int(fft_size / 2 + 1))]
    freq_index[int(fft_size / 2 + 1):] = [i / fft_size for i in range(int(-fft_size / 2 + 1), 0)]  # 重新定义一个序列

    # 傅里叶变换
    data_fft = abs(np.fft.fftshift(np.fft.fft(dseq_log, fft_size)))  # 对程序输入的时间序列进行快速傅里叶变换，并进行移频
    freq_index = np.fft.fftshift(freq_index)  # 对重新定义的序列进行移频，把位于边缘的图像移动到中心，中心移动到边缘（平移）

    b, a = signal.butter(2, 2 * req_stop_final / 0.5, 'lowpass')  # 配置滤波器 2 表示滤波器的阶数，截止频率是第三个峰的频率
    filtedData = signal.filtfilt(b, a, dseq_log)  # 最优的滤波序列
    return pd.Series(filtedData, index=raw.index)    #, req_stop_final


def t_filter(df, period, order, isShow=False):
    '''
    butterworth时域滤波函数
    输入：1. df: df为需要进行滤波（平滑）的时间序列，需要为Series格式，index为时间
         2. period：输入需要平滑的分钟、天数或月份
         3. order:1 or 2,代表滤波器阶数，其中1会更领先，2会更平滑
         4. isShow=True,画相应阶数滤波器的图以及对应的群延迟图
    输出：滤波（平滑）后的时间序列，为Series
    '''
    # 判断输入是否是series
    if str(type(df))[-8:-2]!='Series':
        return "输入的序列不是Series格式哦，请重新输入"
    # 一阶
    filter1 = [df[0]]
    b1, a1 = signal.butter(1, 1 /period, 'lowpass')
    for i in range(1, len(df)):
        tmp = -a1[1] * filter1[-1] + b1[0] * df[i] + b1[1] * df[i - 1]
        filter1.append(tmp)
    s_filter1 = pd.Series(filter1, index=df.index)

    # 二阶
    filter2 = [df[0], df[1]]
    b2, a2 = signal.butter(2, 1 /period, 'lowpass')
    for j in range(2, len(df)):
        tmp = -a2[1] * filter2[-1] - a2[2] * filter2[-2] + b2[0] * df[j] + b2[1] * df[j - 1] + b2[2] * df[j - 2]
        filter2.append(tmp)
    s_filter2 = pd.Series(filter2, index=df.index)


    #画相应滤波器阶数的图以及群延迟图
    if isShow is True:
        d1 = 2*np.pi*1/period  #截止频率
        d = np.arange(100)
        d= d/20
        w1,gd1 = signal.group_delay((b1, a1))
        w2,gd2 = signal.group_delay((b2, a2))

        values = []
        for i in range(2):
            n=i+1
            value = pd.Series(np.sqrt(1/(1+np.power((d/d1),2*n))))
            value.index = d
            values.append(value)

        fig, axs = plt.subplots(3, 1, figsize=(35,17), sharex = False)
        if order ==1:
            axs[0].plot(values[0])
            axs[0].set_title("一阶滤波器频域图")


            axs[1].plot(w1,gd1)
            axs[1].set_title("一阶滤波器群延迟")

            axs[2].plot(s_filter1)
            axs[2].plot(df)
            axs[2].set_title("滤波前后先后序列")
            axs[2].legend(['滤波后序列','原始序列'],fontsize=20)
        if order==2:
            axs[0].plot(values[1])
            axs[0].set_title("二阶滤波器频域图")


            axs[1].plot(w2,gd2)
            axs[1].set_title("二阶滤波器群延迟")

            axs[2].plot(s_filter2)
            axs[2].plot(df)
            axs[2].set_title("滤波前后序列")
            axs[2].legend(['滤波后序列','原始序列'])

    if order == 1:
        return s_filter1
    else:
        return s_filter2


def t_filtfilter(df,periods, order,isShow=False):
    """
    零相位滞后滤波序列
    输入：
    df:Series格式的原序列
    periods：输入需要平滑的分钟、天数或月份
    order: 滤波器阶数
    isShow:是否画图，True:画图，False:不画图
    输出：
    data:零相位滞后滤波序列
    """
     # 判断输入是否是series
    if str(type(df))[-8:-2]!='Series':
        return "输入的序列不是Series格式哦，请重新输入"
    
    b, a = signal.butter(order, 1/periods, 'lowpass')  
    data = signal.filtfilt(b, a, df)  # 最优的滤波序列
    data = pd.Series(data,index=df.index)
    if isShow==True:
        line_graph([df,data],legend_list=["原序列","零滞后序列"])
    return data
    

def delay():
    pass
    
def freq_graph():
    pass
    

if __name__ == "__main__":
    from pyfi import eco_ip, line_graph
    raw = eco_ip(begin_date="2002-01-01", end_date="2019-01-01") # 输入的原序列所在表格
    weight_votality = 0.5  # 数中波动性的权重
    filteddata = f_filter(raw, weight_votality)  # 最优的滤波后序列和截止频率
    line_graph([raw, filteddata])

from matplotlib import pyplot as plt
import matplotlib.cm as cm
import pandas as pd
import numpy as np
import seaborn as sns
from tqdm import tqdm
from utils import *
from math import ceil
import os

df = read_file()

# def get_qujian(num, _max=1):
#     """
#     获取区间
#     """
#     qujian = range(0, 10, _max)
#     i = 0
#     for i in range(len(qujian)):
#         j = i + 1
#         if j == len(qujian):
#             break
#         start = qujian[i]
#         end = qujian[j]
#         if start <= num < end:
#             return (f'{start}-{end}', i)
#     return (f'>= 10', i)

def get_qujian(num):
    """
    ＜5,5-8,8-10,10-12,12-15,＞15
    """
    if num < 5:
        return ('<5', 0)
    if 5 <= num < 8:
        return ('5-8', 1)
    if 8 <= num < 10:
        return ('8-10', 2)
    if 10 <= num < 12:
        return ('10-12', 3)
    if 12 <= num < 15:
        return ('12-15', 4)
    if num >= 15:
        return ('>=15', 5)

def main(city):
    city_df = df[df[city] == True]
    def _plot(city_df, path):
        
        city_df['qujian'] = city_df['Height_top'].apply(get_qujian)
        data = city_df.groupby('qujian')['Index_stm'].count().to_frame()
        data = data.reset_index()
        data.columns = ['区间', '数量']
        data['占比'] = data['数量'].apply(lambda x: round(x / data['数量'].sum(), 4) * 100) 
        data['索引'] = data['区间'].apply(lambda x: x[1])
        data['区间'] = data['区间'].apply(lambda x: x[0])
        data = data.sort_values(['索引'])
        plt.figure(figsize=(12, 10))
        ax = sns.barplot(data=data, x='区间', y='占比', color='#96bad6')
        ax.set_xlabel('Height_top(km)', fontsize=16) #设置x轴名称
        ax.set_ylabel('Frequency(%)', fontsize=16) #设置y轴名称
        plt.savefig(path, dpi=200)
       
        # data.to_excel(path.replace('png', 'xlsx'), index=False)
    
    base_path = './images/新增_8_高度_top'
    if not os.path.exists(base_path):
        os.mkdir(base_path)
    _plot(city_df, f'{base_path}/{city}_all.png')

    for month in range(6, 9):
	    _city_df = city_df[city_df['Month'] == month]
	    _plot(_city_df, f'{base_path}/{city}_{month}.png')



if __name__ == '__main__':
	for city in ['tianshui', 'lanzhou', 'zhangye']:
		print(city)
		main(city)
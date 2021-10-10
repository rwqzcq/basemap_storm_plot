"""
风暴面积的百分比图，此处的面积是所有时次的面积，而非风暴最大面积横坐标标注Area（km2），纵坐标百分比Frequency（%）
"""
from matplotlib import pyplot as plt
import matplotlib.cm as cm
import pandas as pd
import numpy as np
import seaborn as sns
from tqdm import tqdm
from utils import *
import os
from math import floor, ceil

df = read_file()
df = df[df['MaxRef'] > 0]
_config = get_city_config()
area = _config['area']
center = _config['center']


def main(city):
    city_df = df[df[city] == True]

    def _plot(city_df, path):
        data = city_df
        data = data[['MaxRef']] 
        data.columns = ['面积']
        data['qujian'] = data['面积'].apply(lambda x: get_qujian(x, 60, 5)) # 最大值80，间隔为10

        data = data.groupby('qujian')['面积'].count().to_frame()
        data = data.reset_index()
        data.columns = ['区间', '数量']
        data['占比'] = data['数量'].apply(lambda x: round(x / data['数量'].sum(), 4) * 100) 
        data['索引'] = data['区间'].apply(lambda x: x[1])
        data['区间'] = data['区间'].apply(lambda x: x[0])
        data = data.sort_values(['索引'])
        plt.figure(figsize=(12, 10))
        ax = sns.barplot(data=data, x='区间', y='占比', color='#96bad6')
        ax.set_ylabel('Frequency(%)', fontsize=16) #设置y轴名称
        ax.set_xlabel(r'Reflectivity(dBZ)', fontsize=16) #设置y轴名称
        plt.savefig(path, dpi=200)
    
    base_path = './images/新增_14_风暴最大反射因子'
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
"""
持续时间分布
"""
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

def main(city):
    city_df = df[df[city] == True]

    def _plot(city_df, path):
        data = []
        for index_stm, item in tqdm(city_df.groupby(df['Index_stm'])):
            last_minutes = item['N_route'].max() * 6
            data.append([index_stm, last_minutes])
        data = pd.DataFrame(data=data, columns=['index_stm', 'last_minutes'])
        # data['last_interval'] = data['last_minutes'].apply(lambda x: ceil(x / 12) * 12)
        data['qujian'] = data['last_minutes'].apply(lambda x: get_qujian(x, 96, 12)[0])
        plt.figure(figsize=(12, 10))
        # 画成柱状图
        plot_data = data.groupby(data['qujian'])['index_stm'].count().to_frame()
        plot_data = plot_data.reset_index()
        plot_data.columns = ['持续时间', '数量']
        plot_data['占比'] = plot_data['数量'].apply(lambda x: round(x / plot_data['数量'].sum(), 4) * 100)
        ax = sns.barplot(data=plot_data, x='持续时间', y='占比', color='#96bad6')
        ax.set_xlabel('Duration(min)', fontsize=16) #设置x轴名称
        ax.set_ylabel('Frequency(%)', fontsize=16) #设置y轴名称
        plt.savefig(path, dpi=200)
    
    base_path = './images/新增_7_持续时间'
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
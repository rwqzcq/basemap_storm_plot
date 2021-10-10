"""
传播速度箱线图
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

def process_box(value):
    """
    统一刻度到3.0
    """
    value = ceil(value / 30) * 0.5
    if value >= 3.0:
        return 3.0
    return value

df = read_file()
df = df[df['Speed'] > 0]
def main(city):
    city_df = df[df[city] == True]
    def box_plot(city_df, path):
        data = []
        for index_stm, item in tqdm(city_df.groupby(df['Index_stm'])):
            last_minutes = item['N_route'].max() * 6
            max_speed = item['Speed'].median() # 中位数
            data.append([index_stm, last_minutes, max_speed])
        data = pd.DataFrame(data=data, columns=['index_stm', 'last_minutes', 'max_speed'])
        data = data[data['max_speed'] > 0]
        data['last_interval'] = data['last_minutes'].apply(process_box)
        # 新增一个3.0
        if data['last_interval'].max() < 3:
            data = data.append({'last_interval': 3, 'max_speed': 0, 'index_stm': -1}, ignore_index=True)
        plt.figure(figsize=(12, 10))
        ax = sns.boxplot(data=data, x = "last_interval", y = "max_speed", showfliers=True)
        ax.set_xlabel('Duration(h)', fontsize=16) #设置x轴名称
        ax.set_ylabel('Speed(km/h)', fontsize=16) #设置y轴名称
        plt.savefig(path, dpi=200)
    
    base_path = './images/4_传播速度'
    if not os.path.exists(base_path):
        os.mkdir(base_path)
    box_plot(city_df, f'{base_path}/{city}_all.png')

    for month in range(6, 9):
	    _city_df = city_df[city_df['Month'] == month]
	    box_plot(_city_df, f'{base_path}/{city}_{month}.png')



if __name__ == '__main__':
	for city in ['tianshui', 'lanzhou', 'zhangye']:
		print(city)
		main(city)
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

df = read_file()

def main(city):
    city_df = df[df[city] == True]

    def box_plot(city_df, path):
        data = []
        for index_stm, item in tqdm(city_df.groupby(['Index_stm'])):
            item = item[item['N_route'] >= 2]
            if item.shape[0] <= 1:
                continue
            last_minutes = item['N_route'].max() * 6
            # item['next_lon'] = item['Longitude'].shift(1)
            # item['next_lat'] = item['Latitude'].shift(1)
            # item = item.dropna(subset=['next_lon', 'next_lat'])
            # item['distance'] = item.apply(lambda row: cal_distance(float(row['next_lon']), float(row['next_lat']), float(row['Longitude']), float(row['Latitude'])), axis=1)
            item['distance'] = item['Speed'] * 0.1 # 距离 = 速度 * 0.1
            data.append([index_stm, last_minutes, item['distance'].sum()])
            
        data = pd.DataFrame(data=data, columns=['index_stm', 'last_minutes', 'distance'])
        data['last_interval'] = data['last_minutes'].apply(process_box)
        if data['last_interval'].max() < 3:
            data = data.append({'last_interval': 3, 'distance': 0, 'index_stm': -1}, ignore_index=True)
        plt.figure(figsize=(12, 10))
        ax = sns.boxplot(data=data, x = "last_interval", y = "distance", showfliers=False)
        ax.set_xlabel('Duration(h)', fontsize=16) #设置x轴名称
        ax.set_ylabel('Distance(km)', fontsize=16) #设置y轴名称
        plt.savefig(path, dpi=200)
    
    base_path = './images/5_传播距离'
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
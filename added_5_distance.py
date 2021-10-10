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

# def get_qujian(num, _max=10):
#     """
#     获取区间
#     """
#     qujian = range(0, 120, _max)
#     i = 0
#     for i in range(len(qujian)):
#         j = i + 1
#         if j == len(qujian):
#             break
#         start = qujian[i]
#         end = qujian[j]
#         if start <= num < end:
#             return (f'{start}-{end}', i)
#     return (f'>= 120', i)

def main(city):
    city_df = df[df[city] == True]
    def _plot(city_df, path):
        """
        所有传播距离的占比
        """
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
            item['distance'] = item['Speed'] * 0.1
            data.append([index_stm, last_minutes, item['distance'].sum()])
        data = pd.DataFrame(data=data, columns=['index_stm', 'last_minutes', 'distance'])
        data = data[data['distance'] > 0]
        data = data[['distance']] 
        data.columns = ['距离']
        data['qujian'] = data['距离'].apply(lambda x: get_qujian(x, step=10))

        data = data.groupby('qujian')['距离'].count().to_frame()
        data = data.reset_index()
        data.columns = ['区间', '数量']
        data['占比'] = data['数量'].apply(lambda x: round(x / data['数量'].sum(), 4) * 100) 
        data['索引'] = data['区间'].apply(lambda x: x[1])
        data['区间'] = data['区间'].apply(lambda x: x[0])
        data = data.sort_values(['索引'])

        plt.figure(figsize=(12, 10))
        ax = sns.barplot(data=data, x='区间', y='占比', color='#96bad6')
        ax.set_xlabel('Distance(km)', fontsize=16) #设置x轴名称
        ax.set_ylabel('Frequency(%)', fontsize=16) #设置y轴名称
        plt.savefig(path, dpi=200)
        # data.to_excel(path.replace('png', 'xlsx'), index=False)
        
    
    base_path = './images/新增_5_传播距离'
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
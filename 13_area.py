from matplotlib import pyplot as plt
import matplotlib.cm as cm
import pandas as pd
import numpy as np
import seaborn as sns
from tqdm import tqdm
from mpl_toolkits.basemap import Basemap
from utils import *
import os
from math import floor, ceil

df = read_file()
_config = get_city_config()
area = _config['area']
center = _config['center']

def main(city):
    city_df = df[df[city] == True]

    def _plot(city_df, path):
        data = []
        for index_stm, item in tqdm(city_df.groupby(['Index_stm'])):
            last_time = item['N_route'].max() * 6
            area = item['Area'].median() # 中位数
            data.append([last_time, area])
        data = pd.DataFrame(data=data, columns=['last_time', 'Area'])
        data['last_interval'] = data['last_time'].apply(process_box)
        if data['last_interval'].max() < 3:
            data = data.append({'last_interval': 3, 'Area': 0, 'index_stm': -1}, ignore_index=True)
        plt.figure(figsize=(12, 10))
        ax = sns.boxplot(data=data, x = "last_interval", y = "Area", showfliers=False)
        ax.set_xlabel('Duration(h)', fontsize=16) #设置x轴名称
        ax.set_ylabel(r'$Area(km^{2})$', fontsize=16) #设置y轴名称
        plt.savefig(path, dpi=200)
    
    base_path = './images/13_风暴面积'
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
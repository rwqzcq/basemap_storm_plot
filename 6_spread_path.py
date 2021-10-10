"""
传播路径
"""
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
df = df[df['N_route'] >= 2]

_config = get_city_config()
area = _config['area']
center = _config['center']

def main(city):
    city_df = df[df[city] == True]

    def _plot(city_df, path):
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot()
        
        lonl, lonr, latd, latu = area[city] # 设置城市的范围
        lon_center, lat_center = center[city] # 设置中心点
        m = Basemap(projection='merc',llcrnrlat=latd,llcrnrlon=lonl,urcrnrlat=latu,urcrnrlon=lonr) # 设置地图区域
        mlon_center, mlat_center = m(lon_center,lat_center) # 中心点坐标转换
        file_map1 = './Map_data/bou2_4m/bou2_4l'
        file_map2 = './Map_data/bou3_4m/diquJie_polyline'
        m.readshapefile(file_map1, 'chn',color='k', ax=ax) # 读取地图文件
        m.readshapefile(file_map2, 'chn',color='k', ax=ax)
        
        parallels = np.arange(floor(latd), ceil(latu) + 0.5, 0.5) # 33 36.5 0.5
        m.drawparallels(parallels, labels=[1, 0, 0, 0 ], color='grey',fontsize=18, ax=ax) # 设置纬线
        meridians = np.arange(floor(lonl), ceil(lonr) + 0.5, 0.5) # 104, 108.5 0.5
        m.drawmeridians(meridians, labels=[0, 0, 0, 1], color='grey',fontsize=18, ax=ax) # 设置经线

        # 加灰色底图
        lons = np.arange(lonl*100,lonr*100+0.001,1).astype('int') # 生成一个从10248到10522的等差数列
        lats = np.arange(latd*100,latu*100+0.001,1).astype('int') # 生成一个从3490到3710的等差数列
        lon_center, lat_center = center[city] # 设置中心点
        ref_grid = np.zeros((len(lats),len(lons))) # 生成一个表格，宽度是221，高度是275
        ref_grid[ref_grid==0] = np.nan
        for ii in range(len(lons)):
            for jj in range(len(lats)):
                if (m(lons[ii]/100,lats[jj]/100)[0]-mlon_center)**2+(m(lons[ii]/100,lats[jj]/100)[1]-mlat_center)**2<=(150*1000)**2 :
                    ref_grid[jj,ii] = 0 # 把中心点150KM范围内的点设置为0
        lonsx, latsx = np.meshgrid(lons/100, lats/100)#网格化经纬度，使得每个点都有经纬度
        colors=('#C0C0C0','#7895FA','#385EF3','#7CFC00','#FFD700','#EA8F20','#F46135','#E30000')	
        X,Y = m(lonsx,latsx)#经纬度对应到地图上
        ax.contourf(X,Y,ref_grid,colors=colors,extend='both',antialiased=True,levels=np.arange(1, 8, 1))#

        for index_stm, item in tqdm(city_df.groupby(['Index_stm'])):
            is_start = True
            if item['Index_route'].count() <= 1:
                continue
            item = item.sort_values(by=['Index_route'])
            item['next_lon'] = item['Longitude'].shift(1)
            item['next_lat'] = item['Latitude'].shift(1)

            item_index = 0
            item_length = item.shape[0]

            for _, row in item.iterrows():
                item_index += 1
                x = row['Longitude']
                y = row['Latitude']
                lon, lat = x, y
                x, y = m(x, y) # 坐标进行转换
                # 过滤掉没有在150km范围内的点
                if (m(lon, lat)[0]-mlon_center)**2+(m(lon, lat)[1]-mlat_center)**2 > (150*1000)**2: # 没有在150km范围之内
                    continue
                if is_start == True:
                    m.scatter(x, y, 10, marker='o',color='blue', ax=ax) # 画点图
                    is_start = False
                else:
                    if item_index == item_length:
                        m.scatter(x, y, 20, marker='o',color='red', ax=ax) # 画点图
                    else:
                        m.scatter(x, y, 10, marker='o',color='k', ax=ax) # 画点图

                x1, y1 = row['next_lon'], row['next_lat']
                if pd.isna(x1) == True: # 是起始点
                    continue
                x1, y1 = m(x1, y1)
                if x == x1 and y == y1: # 相同的点则去除
                    continue
                m.plot([x, x1],[y, y1], linewidth=1, color='black', ax=ax)
        plt.savefig(path, dpi=200)
    
    base_path = './images/6_传播路径'
    if not os.path.exists(base_path):
        os.mkdir(base_path)

    for month in range(6, 9):
        _city_df = city_df[city_df['Month'] == month]
        for (start, end) in [(2, 8), (8, 14), (14, 20)]: # 08-14，14-20,20-02,02-08
            section_city_df = _city_df[(_city_df['Hour'] >= start) & (_city_df['Hour'] < end)]
            _plot(section_city_df, f'{base_path}/{city}_{month}_{start}_{end}.png')
            hours_3 = [start, start+3, end]
            for i in range(2):
                start = hours_3[i]
                end = hours_3[i + 1]
                section_city_df = _city_df[(_city_df['Hour'] >= start) & (_city_df['Hour'] < end)]
                _plot(section_city_df, f'{base_path}/{city}_{month}_{start}_{end}.png')
            
        start, end = 20, 2
        section_city_df = _city_df[(_city_df['Hour'] >= start) | (_city_df['Hour'] < end)]
        _plot(section_city_df, f'{base_path}/{city}_{month}_{start}_{end}.png')
        hours_3 = [start, start+3, end]
        for i in range(2):
            start = hours_3[i]
            end = hours_3[i + 1]
            section_city_df = _city_df[(_city_df['Hour'] >= start) & (_city_df['Hour'] < end)]
            _plot(section_city_df, f'{base_path}/{city}_{month}_{start}_{end}.png')
        


if __name__ == '__main__':
	for city in ['tianshui', 'lanzhou', 'zhangye']:
		print(city)
		main(city)

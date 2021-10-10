"""
不同高度
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

_config = get_city_config()
area = _config['area']
center = _config['center']

def main(city):
    city_df = df[df[city] == True]
    def _plot(city_df, path, level):
        lonl, lonr, latd, latu = area[city] # 设置城市的范围
        lons = np.arange(lonl*100,lonr*100+0.001,1).astype('int') # 生成一个从10248到10522的等差数列
        lats = np.arange(latd*100,latu*100+0.001,1).astype('int') # 生成一个从3490到3710的等差数列
        lon_center, lat_center = center[city] # 设置中心点
        ref_grid = np.zeros((len(lats),len(lons))) # 生成一个表格，宽度是221，高度是275
        ref_grid[ref_grid==0] = np.nan
        m = Basemap(projection='merc',llcrnrlat=latd,llcrnrlon=lonl,urcrnrlat=latu,urcrnrlon=lonr)
        mlon_center,mlat_center = m(lon_center,lat_center)
        for ii in range(len(lons)):
            for jj in range(len(lats)):
                if (m(lons[ii]/100,lats[jj]/100)[0]-mlon_center)**2+(m(lons[ii]/100,lats[jj]/100)[1]-mlat_center)**2<=(150*1000)**2 :
                    ref_grid[jj,ii] = 0 # 把中心点150KM范围内的点设置为0

        for _, row in tqdm(city_df.iterrows()):
            lon = row['Longitude']
            lat = row['Latitude']
            if (m(lon, lat)[0]-mlon_center)**2+(m(lon, lat)[1]-mlat_center)**2<=(150*1000)**2 :
                ref_grid[np.where(lats==round(lat*100))[0][0], np.where(lons==round(lon*100))[0][0]] += row['Height_top']

        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot()

        file_map1 = './Map_data/bou2_4m/bou2_4l'
        file_map2 = './Map_data/bou3_4m/diquJie_polyline'
        m.readshapefile(file_map1, 'chn',color='k', ax=ax) # 读取地图文件
        m.readshapefile(file_map2, 'chn',color='k', ax=ax)
        m.drawparallels(np.arange(int(latd), int(latu)+1, 0.5), labels=[1, 0, 0, 0 ], color='grey',fontsize=18, ax=ax)#, fontsize=12)#labels=[1, 0, 0, 0 ]表示上下左右（1开），一般用于兰伯特投影
        #m.drawmeridians(np.arange(102.35, 106.35, 1), labels=[0, 0, 0, 1], color='grey',fontsize=16, ax=ax[m_szx])#, fontsize=12)
        m.drawmeridians(np.arange(int(lonl), int(lonr)+1, 0.5), labels=[0, 0, 0, 1], color='grey',fontsize=18, ax=ax)#, fontsize=12)
        lonsx,latsx = np.meshgrid(lons/100, lats/100)#网格化经纬度，使得每个点都有经纬度	
        X,Y = m(lonsx,latsx)#经纬度对应到地图上
        colors=('#C0C0C0','#7895FA','#385EF3','#7CFC00','#FFD700','#EA8F20','#F46135','#E30000', '#8E388E', '#FF00FF')
        c = ax.contourf(X,Y,ref_grid,colors=colors,extend='both',antialiased=True, levels=level)# # np.arange(0, 100, 10)
        cb = plt.colorbar(c,ax=ax,orientation='vertical', cax = fig.add_axes([0.9, 0.2, 0.018, 0.60]))#,ticks=np.arange(35,60, 2)
        cb.ax.tick_params(labelsize=18,direction='out')
        cb.set_label('Num',fontdict={'size':18})  # 设置纵坐标轴的标签
        plt.savefig(path, dpi=200)
    
    base_path = './images/8_高度'
    if not os.path.exists(base_path):
        os.mkdir(base_path)
    levels = {
        'low': np.arange(0, 20, 2),
        'mid': np.arange(0, 20, 2),
        'high': np.arange(0, 20, 2)
    }
    for month in range(6, 9):
        _city_df = city_df[city_df['Month'] == month]
        for (label, start, end) in [('low', 0, 6), ('mid', 6, 12)]:
            section_city_df = _city_df[(_city_df['Height_top'] >= start) &(_city_df['Height_top'] < end)]
            _plot(section_city_df, f'{base_path}/{city}_{month}_{label}.png', level=levels[label])
        
        label = 'high'
        start = 12
        section_city_df = _city_df[(_city_df['Height_top'] >= start)]
        _plot(section_city_df, f'{base_path}/{city}_{month}_{label}.png', level=levels[label])

if __name__ == '__main__':
	for city in ['tianshui', 'lanzhou', 'zhangye']:
		print(city)
		main(city)

from matplotlib import pyplot as plt
import matplotlib.cm as cm
import pandas as pd
import numpy as np
import seaborn as sns
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Circle
import matplotlib.patches as mpatches
from tqdm import tqdm
from utils import *
from math import ceil, floor
import os

df = read_file()
_config = get_city_config()
area = _config['area']
center = _config['center']

labels = ["<6", "6-12", ">=12"]
colors = ['#7895FA', '#FFD700', '#7CfC00']

def get_level(height):
    """
    获取区间
    """
    if height < 6:
        return 0
    if 6 <= height < 12:
        return 1
    if height >= 12:
        return 2
    

def main(city):
    city_df = df[df[city] == True]

    def _plot(city_df, path):
        lonl, lonr, latd, latu = area[city]
        lon_center, lat_center = center[city] # 设置中心点
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot()
        m = Basemap(projection='merc',llcrnrlat=latd, llcrnrlon=lonl, urcrnrlat=latu, urcrnrlon=lonr) # 设置地图区域
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
        shadow_colors=('#C0C0C0','#7895FA','#385EF3','#7CFC00','#FFD700','#EA8F20','#F46135','#E30000')	
        X,Y = m(lonsx,latsx)#经纬度对应到地图上
        ax.contourf(X,Y,ref_grid,colors=shadow_colors,extend='both',antialiased=True,levels=np.arange(1, 8, 1))#

        plot_data = {l: [[], []] for l in labels}
        for _, item in tqdm(city_df.iterrows()):
            lon = item['Longitude']
            lat = item['Latitude']
            x, y = m(lon, lat)
            level = get_level(item['Height_ctr'])
            if (m(lon, lat)[0]-mlon_center)**2+(m(lon, lat)[1]-mlat_center)**2 > (150*1000)**2: # 没有在150km范围之内
                continue
            _label = labels[level]
            plot_data[_label][0].append(x)
            plot_data[_label][1].append(y)
        
        l = []
        for index, _label in enumerate(labels):
            _color = colors[index]
            xs, ys = plot_data[_label]
            if len(xs) == 0:
                continue
            _ax = m.scatter(xs, ys, marker='o', color=_color)
            l.append(_ax)
        plt.legend(l, labels, loc=4, title=r'Height_stm(km)', fontsize=14, bbox_to_anchor=(1.23, 0.2))
        plt.savefig(path, dpi=200)

    
    base_path = './images/新增_8_高度_ctr_分层'
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
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Circle
import matplotlib.patches as mpatches
import os
from utils import *
from math import ceil, floor
from tqdm import tqdm

df = read_file()
_config = get_city_config()
area = _config['area']
center = _config['center']

def main(city):
	# city = 'tianshui'
	city_df = df[df[city] == True]
	start = get_start(city_df)

	def scatter_plot(start, path):
		lonl, lonr, latd, latu = area[city]
		fig = plt.figure(figsize=(12, 10))
		ax = fig.add_subplot()
		m = Basemap(projection='merc',llcrnrlat=latd,llcrnrlon=lonl,urcrnrlat=latu,urcrnrlon=lonr) # 设置地图区域
		lon_center, lat_center = center[city]
		file_map1 = './Map_data/bou2_4m/bou2_4l'
		file_map2 = './Map_data/bou3_4m/diquJie_polyline'
		m.readshapefile(file_map1, 'chn',color='k', ax=ax) # 读取地图文件
		m.readshapefile(file_map2, 'chn',color='k', ax=ax)
		parallels = np.arange(floor(latd), ceil(latu) + 0.5, 0.5) # 33 36.5 0.5
		m.drawparallels(parallels, labels=[1, 0, 0, 0 ], color='grey',fontsize=18, ax=ax) # 设置纬线
		meridians = np.arange(floor(lonl), ceil(lonr) + 0.5, 0.5) # 104, 108.5 0.5
		m.drawmeridians(meridians, labels=[0, 0, 0, 1], color='grey',fontsize=18, ax=ax) # 设置经线
		for _, row in tqdm(start.iterrows()):
			x = row['Longitude']
			y = row['Latitude']
			x, y = m(x, y) # 坐标进行转换
			m.scatter(x, y, 5,marker='o',color='k', ax=ax) # 画点图
		plt.savefig(path, dpi=200)

	def shadow_plot(start, path):
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
		for _, row in tqdm(start.iterrows()):
			lon = row['Longitude']
			lat = row['Latitude']
			if (m(lon, lat)[0]-mlon_center)**2+(m(lon, lat)[1]-mlat_center)**2<=(150*1000)**2 :
				ref_grid[np.where(lats==round(lat*100))[0][0], np.where(lons==round(lon*100))[0][0]] += 1
		fig = plt.figure(figsize=(12, 10))
		ax = fig.add_subplot()
		file_map1 = './Map_data/bou2_4m/bou2_4l'
		file_map2 = './Map_data/bou3_4m/diquJie_polyline'
		m.readshapefile(file_map1, 'chn',color='k', ax=ax) # 读取地图文件
		m.readshapefile(file_map2, 'chn',color='k', ax=ax)
		m.drawparallels(np.arange(int(latd),int(latu)+1, 0.5), labels=[1, 0, 0, 0 ], color='grey',fontsize=18, ax=ax)#, fontsize=12)#labels=[1, 0, 0, 0 ]表示上下左右（1开），一般用于兰伯特投影
		#m.drawmeridians(np.arange(102.35, 106.35, 1), labels=[0, 0, 0, 1], color='grey',fontsize=16, ax=ax[m_szx])#, fontsize=12)
		m.drawmeridians(np.arange(int(lonl), int(lonr)+1, 0.5), labels=[0, 0, 0, 1], color='grey',fontsize=18, ax=ax)#, fontsize=12)
		lonsx,latsx = np.meshgrid(lons/100, lats/100)#网格化经纬度，使得每个点都有经纬度	
		X,Y = m(lonsx,latsx)#经纬度对应到地图上
		colors=('#C0C0C0','#7895FA','#385EF3','#7CFC00','#FFD700','#EA8F20','#F46135','#E30000')
		c = ax.contourf(X,Y,ref_grid,colors=colors,extend='both',antialiased=True,levels=np.arange(1, 8, 1))#
		cb = plt.colorbar(c,ax=ax,orientation='vertical',cax = fig.add_axes([0.9, 0.2, 0.018, 0.60]))#,ticks=np.arange(35,60, 2)
		cb.set_label('Num',fontdict={'size':18})  # 设置纵坐标轴的标签
		cb.ax.tick_params(labelsize=18,direction='out')
		plt.savefig(path, dpi=200) 

	base_path = './images/1_起始点'
	if not os.path.exists(base_path):
		os.mkdir(base_path)

	shadow_plot(start, f'{base_path}/{city}_all.png')
	for month in range(6, 9):
	    _start = start[start['Month'] == month]
	    shadow_plot(_start, f'{base_path}/{city}_{month}.png')


if __name__ == '__main__':
	for city in ['tianshui', 'lanzhou', 'zhangye']:
		print(city)
		main(city)
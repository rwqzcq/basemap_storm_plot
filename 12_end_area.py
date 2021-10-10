from matplotlib import pyplot as plt
import matplotlib.cm as cm
import pandas as pd
import numpy as np
import seaborn as sns
from tqdm import tqdm
from mpl_toolkits.basemap import Basemap
from utils import *
import os
from math import floor, ceil, pi

def get_levels(area):
    levels = np.arange(0, 120, 20)
    level_index = 0
    for index, start in enumerate(levels):
        next_index = index + 1
        if next_index == len(levels):
            break
        end = levels[next_index]
        if area >= start and area < end:
            return level_index
        level_index += 1
    if area >= 100:
        return level_index



df = read_file()
df = get_end(df)
df['level'] = df['Area'].apply(get_levels)

_config = get_city_config()
area = _config['area']
center = _config['center']

def main(city):
    city_df = df[df[city] == True]

    def _plot(city_df, path):

        def shoot(lon, lat, azimuth, maxdist=None):
            """Shooter Function
            Original javascript on http://williams.best.vwh.net/gccalc.htm
            Translated to python by Thomas Lecocq
            """
            glat1 = lat * np.pi / 180.
            glon1 = lon * np.pi / 180.
            s = maxdist / 1.852
            faz = azimuth * np.pi / 180.

            EPS= 0.00000000005
            if ((np.abs(np.cos(glat1))<EPS) and not (np.abs(np.sin(faz))<EPS)):
                print("Only N-S courses are meaningful, starting at a pole!")

            a=6378.13/1.852
            f=1/298.257223563
            r = 1 - f
            tu = r * np.tan(glat1)
            sf = np.sin(faz)
            cf = np.cos(faz)
            if (cf==0):
                b=0.
            else:
                b=2. * np.arctan2 (tu, cf)

            cu = 1. / np.sqrt(1 + tu * tu)
            su = tu * cu
            sa = cu * sf
            c2a = 1 - sa * sa
            x = 1. + np.sqrt(1. + c2a * (1. / (r * r) - 1.))
            x = (x - 2.) / x
            c = 1. - x
            c = (x * x / 4. + 1.) / c
            d = (0.375 * x * x - 1.) * x
            tu = s / (r * a * c)
            y = tu
            c = y + 1
            while (np.abs (y - c) > EPS):

                sy = np.sin(y)
                cy = np.cos(y)
                cz = np.cos(b + y)
                e = 2. * cz * cz - 1.
                c = y
                x = e * cy
                y = e + e - 1.
                y = (((sy * sy * 4. - 3.) * y * cz * d / 6. + x) *
                    d / 4. - cz) * sy * d + tu

            b = cu * cy * cf - su * sy
            c = r * np.sqrt(sa * sa + b * b)
            d = su * cy + cu * sy * cf
            glat2 = (np.arctan2(d, c) + np.pi) % (2*np.pi) - np.pi
            c = cu * cy - su * sy * cf
            x = np.arctan2(sy * sf, c)
            c = ((-3. * c2a + 4.) * f + 4.) * c2a * f / 16.
            d = ((e * cy * c + cz) * sy * c + y) * sa
            glon2 = ((glon1 + x - (1. - c) * d * f + np.pi) % (2*np.pi)) - np.pi

            baz = (np.arctan2(sa, b) + np.pi) % (2 * np.pi)

            glon2 *= 180./np.pi
            glat2 *= 180./np.pi
            baz *= 180./np.pi

            return (glon2, glat2, baz)

        def equi(m, centerlon, centerlat, radius, *args, **kwargs):
            glon1 = centerlon
            glat1 = centerlat
            X = []
            Y = []
            for azimuth in range(0, 360):
                glon2, glat2, baz = shoot(glon1, glat1, azimuth, radius)
                X.append(glon2)
                Y.append(glat2)
            X.append(X[0])
            Y.append(Y[0])

            #m.plot(X,Y,**kwargs) #Should work, but doesn't...
            X,Y = m(X,Y)
            plt.plot(X,Y,**kwargs)

            
        lonl, lonr, latd, latu = area[city]
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot()
        m = Basemap(projection='merc',llcrnrlat=latd, llcrnrlon=lonl, urcrnrlat=latu, urcrnrlon=lonr) # 设置地图区域
        lon_center, lat_center = center[city]
        file_map1 = './Map_data/bou2_4m/bou2_4l'
        file_map2 = './Map_data/bou3_4m/diquJie_polyline'
        m.readshapefile(file_map1, 'chn',color='k', ax=ax) # 读取地图文件
        m.readshapefile(file_map2, 'chn',color='k', ax=ax)
        parallels = np.arange(floor(latd), ceil(latu) + 0.5, 0.5) # 33 36.5 0.5
        m.drawparallels(parallels, labels=[1, 0, 0, 0 ], color='grey',fontsize=18, ax=ax) # 设置纬线
        meridians = np.arange(floor(lonl), ceil(lonr) + 0.5, 0.5) # 104, 108.5 0.5
        m.drawmeridians(meridians, labels=[0, 0, 0, 1], color='grey',fontsize=18, ax=ax) # 设置经线
        for _, row in tqdm(city_df.iterrows()):
            x = row['Longitude']
            y = row['Latitude']
            x, y = m(x, y) # 坐标进行转换
            _area = row['Area']
            r = (_area / (pi**2))
            equi(m, row['Longitude'], row['Latitude'], r, lw=1, color='k')
        #     m.scatter(x, y, 3, marker='o', color='k', ax=ax) # 画中心点
        plt.savefig(path, dpi=200)
    
    def _plot2(city_df, path):
        lonl, lonr, latd, latu = area[city]
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot()
        m = Basemap(projection='merc',llcrnrlat=latd, llcrnrlon=lonl, urcrnrlat=latu, urcrnrlon=lonr) # 设置地图区域
        lon_center, lat_center = center[city]
        file_map1 = './Map_data/bou2_4m/bou2_4l'
        file_map2 = './Map_data/bou3_4m/diquJie_polyline'
        m.readshapefile(file_map1, 'chn',color='k', ax=ax) # 读取地图文件
        m.readshapefile(file_map2, 'chn',color='k', ax=ax)
        parallels = np.arange(floor(latd), ceil(latu) + 0.5, 0.5) # 33 36.5 0.5
        m.drawparallels(parallels, labels=[1, 0, 0, 0 ], color='grey',fontsize=18, ax=ax) # 设置纬线
        meridians = np.arange(floor(lonl), ceil(lonr) + 0.5, 0.5) # 104, 108.5 0.5
        m.drawmeridians(meridians, labels=[0, 0, 0, 1], color='grey',fontsize=18, ax=ax) # 设置经线
        
        labels = ["0-20", "20-40", "40-60", "60-80", "80-100", ">=100"]
        sizes = [50, 400, 800, 1200, 1800, 3000]
        # sizes = [3, 6, 9, 12, 15, 18]
        for level, item in tqdm(city_df.groupby(['level'])):
            level += 1
            xs = []
            ys = []
            for _, row in item.iterrows():
                x = row['Longitude']
                y = row['Latitude']
                x, y = m(x, y) # 坐标进行转换
                xs.append(x)
                ys.append(y)
            s = sizes[level - 1]
            l = m.scatter(xs, ys, s, marker='o', color='white', ax=ax, edgecolors='black', lw=0.8, label=labels[level - 1])
        
        labels = ["0-20", "20-40", "40-60", "60-80", "80-100", ">=100"]
        plt.legend(loc = 4, title=r'$Area(KM^{2})$', bbox_to_anchor=(1.25, 0.1), frameon=False, handleheight=4, fontsize=16)
        plt.savefig(path, dpi=200)
    
    base_path = './images/12_终止点'
    if not os.path.exists(base_path):
        os.mkdir(base_path)

    for month in range(6, 9):
        _city_df = city_df[city_df['Month'] == month]
        for (start, end) in [(2, 8), (8, 14), (14, 20)]: # 08-14，14-20,20-02,02-08
            section_city_df = _city_df[(_city_df['Hour'] >= start) & (_city_df['Hour'] < end)]
            _plot2(section_city_df, f'{base_path}/{city}_{month}_{start}_{end}.png')
        start, end = 20, 2
        section_city_df = _city_df[(_city_df['Hour'] >= start) | (_city_df['Hour'] < end)]
        _plot2(section_city_df, f'{base_path}/{city}_{month}_{start}_{end}.png')


if __name__ == '__main__':
	for city in ['tianshui', 'lanzhou', 'zhangye']:
		print(city)
		main(city)
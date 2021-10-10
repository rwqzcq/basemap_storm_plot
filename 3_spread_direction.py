
from pandas.core.indexes import base
from windrose import WindroseAxes
from windrose import plot_windrose
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib.cm as cm
import pandas as pd
import numpy as np
import os
from utils import *

df = read_file()

def get_qujian(num):
    if num >= 0 and num < 20:
        return 0
        return '0 - 20'
    if 20 <= num < 40:
        return 1
        return '20 - 40'
    if 40 <= num < 60:
        return 2
        return '40 - 60'
    if 60 <= num < 80:
        return 3
        return '60 - 80'
    if 80 <= num < 100:
        return 4
        return '80 - 100'
    if 100 <= num < 120:
        return 5
        return '100 - 120'
    if num >= 120:
        return 6
        return '> 120'


def wind_rose_plot(city):
    city_df = df[df[city] == True]
    def _plot(city_df, path):
        data = city_df[['Speed', 'Direction']]
        data.columns = ['speed', 'direction']
        data = data[data['speed'] > 0]
        data = data[data['direction'] > 0]
        data['qujian'] = data['speed'].apply(get_qujian)
        ct0 = np.array(np.arange(0,361, 22.5)) #划分风向的区间，22.5度一个区间
        data['wd'] = pd.cut(data['direction'], ct0) 
        plot_data = data['speed'].groupby([data['qujian'], data['wd']]).count().to_frame().unstack()
        plot_data = plot_data / plot_data.sum().sum()
        plot_data = plot_data.fillna(0)
        n=16 #绘制的扇区的个数，与上面角度的区间划分一致的
        theta=np.linspace(0,2*np.pi,n,endpoint=False) #获取16个方向的角度值
        width=np.pi*1.5/n #设置扇形的宽度
        #设置角度对应的标签
        labels=list(['N','','45','','E','','135','','S','','225','','W','','315',''])
        fig=plt.figure(figsize=(12, 10)) #新建画布
        ax=fig.add_axes([0.1,0.1,0.7,0.7],projection='polar') #在画布添加一个极坐标图，即玫瑰图
        #根据划分的风速段个数来进行颜色配置
        colors = ['#011091', '#0231f5', '#66e0f7', '#75f96d', '#f7d147', '#e73223', '#961d13']
        cmap = mpl.colors.ListedColormap(colors)
        plots = []
        for i in range(0,len(plot_data.index)):
            idx=plot_data.index[i]
            rad=plot_data.loc[idx]
            if i == 0:
            #画玫瑰柱状图，由此类推，可以画雷达图，气泡图等等，只要将bar改成对应的图就可以
                p = ax.bar(theta,rad,width=width,bottom=0,label=idx,tick_label=labels,color=colors[i]) 
            else:
                p = ax.bar(theta,rad,width=width,bottom=np.sum(plot_data.loc[plot_data.index[0: i]]),label=idx,tick_label=labels,color=colors[i])
            plots.append(p)
        ax.set_xticks(theta)
        ax.set_yticks([0.03, 0.06, 0.09, 0.12, 0.15, 0.18, 0.21, 0.24]) #默认的y轴出现的频数，也可设置为空
        ax.set_theta_zero_location('N') #设置0度正北方向
        ax.set_theta_direction(-1) #设置顺时针方向绘图
        # ax.set_title('风玫瑰图',fontsize=16)
        ax.tick_params(labelsize=12) 
        ax.set_xticklabels(labels,fontdict={'weight':'bold','size':12,'color':'k'})
        plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda s, position: '{:.0f}%'.format(100*s))) 
        legend_texts = ['0-20', '20-40', '40-60', '60-80', '80-100', '100-120', '>= 120']
        plots = reversed(plots)
        legend_texts = reversed(legend_texts)
        plt.legend(plots, legend_texts, loc = 4, title='Speed(km/h)', bbox_to_anchor=(1.25, 0.1), frameon=False, fontsize=13)
        plt.savefig(path, dpi=200)

    base_path = './images/3_传播方向'
    if not os.path.exists(base_path):
        os.mkdir(base_path)
    _plot(city_df, f'{base_path}/{city}_all.png')

    for month in range(6, 9):
	    _city_df = city_df[city_df['Month'] == month]
	    _plot(_city_df, f'{base_path}/{city}_{month}.png')
    

if __name__ == '__main__':
	for city in ['tianshui', 'lanzhou', 'zhangye']:
		print(city)
		wind_rose_plot(city)

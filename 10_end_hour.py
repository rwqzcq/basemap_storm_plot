from matplotlib import pyplot as plt
import matplotlib.cm as cm
import pandas as pd
import numpy as np
import seaborn as sns
from utils import *

df = read_file()
df['Hour'] = df['create_at'].apply(lambda x: x.hour)

_config = get_city_config()
area = _config['area']
center = _config['center']

def main(city):
    city_df = df[df[city] == True]
    city_df = get_end(city_df)
    def _plot(city_df, path):
        data = []
        for hour, item in city_df.groupby(city_df['Hour']):
            data.append([hour, item['Hour'].count()])
        data = pd.DataFrame(data=data, columns=['hour', 'count'])
        data['zhanbi'] = data['count'].apply(lambda x: 100 * round(x / data['count'].sum(), 4))
        ax = sns.barplot(x="hour", data=data, y='zhanbi', color='#96bad6')
        plt.figure(figsize=(12, 10))
        ax = sns.barplot(x="hour", data=data, y='zhanbi', color='#96bad6')
        ax.set_xlabel('Termination time (BJT)', fontsize=16) #设置x轴名称
        ax.set_ylabel('Frequency(%)', fontsize=16)
        ax.set_xticks(np.arange(0, 24))
        plt.savefig(path, dpi=200)
    
    base_path = './images/10_终止点'
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

    

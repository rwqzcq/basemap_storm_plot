import pandas as pd
from tqdm import tqdm
from math import radians, sin, cos, asin, sqrt
import os
import datetime
from math import ceil

def read_txt(path):
    """
    读取TXT
    """
    data = []
    # path = './data/titan/201506.txt'
    with open(path) as fp:
        lines = fp.readlines()
        column = [i for i in lines[0].strip().split(' ') if i != '']
        for line in tqdm(lines[1: ]):
            row = [i for i in line.strip().split(' ') if i != '']
            data.append(row)
    df = pd.DataFrame(data=data, columns=column, dtype=float)
    df['Index_stm'] = df['Index_stm'].astype(int)
    df['N_route'] = df['N_route'].astype(int)
    df['Index_route'] = df['Index_route'].astype(int)
    df['Year'] = df['Year'].astype(int)
    df['Month'] = df['Month'].astype(int)
    df['Day'] = df['Day'].astype(int)
    df['Hour'] = df['Hour'].astype(int)
    df['Minute'] = df['Minute'].astype(int)
    return df

def get_city_config():
    """
    设置配置信息
    """
    distance = 150
    area = { # 地图的经纬度范围
        'tianshui': [104.28, 107.00, 33.48, 35.71],
        'lanzhou': [102.48, 105.22, 34.9,37.1],
        'zhangye': [98.91, 101.65, 38.03, 40.13]
    }
    center = { # 中心点
        'tianshui': [105.64, 34.60],
        'lanzhou': [103.851, 36.01],
        'zhangye': [100.28, 39.09]
    }
    
    return {
        'distance': distance, # 150km
        'center': center, # 中心点
        'area': area
    }

def cal_distance(lon1, lat1, lon2, lat2):
    """
    计算地图两点之间的距离
    """
    a = radians(lat1-lat2)
    b = radians(lon1-lon2)
    lat1,lat2 = radians(lat1),radians(lat2)
    t = sin(a/2)**2 + cos(lat1)*cos(lat2)*sin(b/2)**2
    d = 2*asin(sqrt(t))*6378.137
    return round(d, 2)

def read_file():
    """
    读取所有的df
    """
    dfs = []
    base_dir = './data/titan'
    for file in tqdm(os.listdir(base_dir)):
        if file == '.DS_Store':
            continue
        file = base_dir + '/' + file
        df = pd.read_csv(file, sep='\s+')
        filename = file.replace('.txt', '')
        df['Index_stm'] = df['Index_stm'].apply(lambda x: f'{filename}_{x}')
        dfs.append(df)
    df = pd.concat(dfs)
    
    df['N_route'] = df['N_route'].astype(int)
    df['Index_route'] = df['Index_route'].astype(int)
    df['Year'] = df['Year'].astype(int)
    df['Month'] = df['Month'].astype(int)
    df['Day'] = df['Day'].astype(int)
    df['Hour'] = df['Hour'].astype(int)
    df['Minute'] = df['Minute'].astype(int)
    
    # 转换时间
    df['create_at'] = df.apply(lambda row: datetime.datetime(int(row['Year']), int(row['Month']), int(row['Day']), int(row['Hour']), int(row['Minute'])), axis=1)
    # df['create_at'] = df.apply(lambda row: datetime.datetime(int(row['Year']), int(row['Month']), int(row['Day']), int(row['Hour']), int(row['Minute'])).replace(tzinfo=datetime.timezone.utc).astimezone(tz=None), axis=1) # 转化为北京时间
    df['Month'] = df['create_at'].apply(lambda x:x.month)
    df['Hour'] = df['create_at'].apply(lambda x: x.hour)
    # df = df[(df['Month'] >= 6) & (df['Month'] <= 8)]
    print('时间转换完成')

    # 计算距离
    _config = get_city_config()
    distance = _config['distance']
    center = _config['center'] # 中心点
    df['tianshui'] = df.apply(lambda row: cal_distance(row['Longitude'], row['Latitude'], center['tianshui'][0], center['tianshui'][1]) <= distance, axis=1)
    df['lanzhou'] = df.apply(lambda row: cal_distance(row['Longitude'], row['Latitude'], center['lanzhou'][0], center['lanzhou'][1]) <= distance, axis=1)
    df['zhangye'] = df.apply(lambda row: cal_distance(row['Longitude'], row['Latitude'], center['zhangye'][0], center['zhangye'][1]) <= distance, axis=1)
    print('距离计算完成')

    df = df.sort_values(['Index_stm', 'Index_route']) # 排序 , 'Year', 'Month', 'Day', 'Hour', 'Minute'
    df = df.reset_index()
    return df

def get_start(df):
    """
    获取起始点
    """
    dfs = []
    for index, item in df.groupby('Index_stm'):
        start = item[item['Index_route'] == 1]
        dfs.append(start)
    df = pd.concat(dfs)
    df = df.reset_index()
    return df

def get_end(df):
    """
    获取终止点
    """
    dfs = []
    for index, item in df.groupby('Index_stm'):
        end = item[item['Index_route'] == item['Index_route'].max()] # 最大的Index_route
        end = end[end['Index_route'] != 1]
        if end.shape[0] != 0:
            dfs.append(end)
    df = pd.concat(dfs)
    df = df.reset_index()
    return df

def get_qujian(num, max_num=120, step=20):
    """
    获取区间
    max_num: 最大值
    step: 步长
    """
    qujian = range(0, max_num, step)
    i = 0
    for i in range(len(qujian)):
        j = i + 1
        if j == len(qujian):
            break
        start = qujian[i]
        end = qujian[j]
        if start <= num < end:
            return (f'{start}-{end}', i)
    return (f'>= {max_num}', i)

def process_box(value):
    """
    统一刻度到3.0
    """
    value = ceil(value / 30) * 0.5
    if value >= 3.0:
        return 3.0
    return value
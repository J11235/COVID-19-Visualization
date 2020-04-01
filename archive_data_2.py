import pandas as pd
import numpy as np
import os


def data_check():
    if not os.path.exists('../COVID-19'):
        print('开始clone数据仓库COVID-19...')
        from git import Repo
        Repo.clone_from(
            'https: // github.com/CSSEGISandData/COVID-19.git', '../COVID-19')
        print('clone完成')

data_check()


def fix_values( values):
        ans = []
        for value in values:
            if not ans or value > ans[-1]:
                ans.append(value)
            else:
                ans.append(ans[-1])
        return ans

def get_new_confirmed(data):
        values = data['Confirmed'].values
        new_confirmed = values[1:] - values[:-1]
        new_confirmed = [values[0]] + new_confirmed.tolist()
        new_confirmed = [i if i > 0 else 0 for i in new_confirmed]
        return new_confirmed


def get_active(data):
        values = data['Confirmed'] - data['Deaths'] - data['Recovered']
        return values

def fill_data(group, dates):
    try:
        group = group.sort_values('updateDate')
        valid_dates = group['updateDate'].values.tolist()
        begin_date = min(valid_dates)
        group.set_index('updateDate', inplace=True)
        for last_date, date in zip(dates[:-1], dates[1:]):
            try:
                if last_date >= begin_date and date not in group.index:
                    group.loc[date] = group.loc[last_date].values
            except Exception as e:
                print('fill data error', e)
        group.sort_index(inplace=True)
        group.reset_index('updateDate', inplace=True, drop=False)

        #修正这三项数据，保持单调递增
        group.loc[:, 'Confirmed'] = fix_values(
            group['Confirmed'].values)
        group.loc[:, 'Deaths'] = fix_values(group['Deaths'].values)
        group.loc[:, 'Deaths'] = fix_values(group['Deaths'].values)

        # 新增确诊
        group['newConfirmed'] = get_new_confirmed(group)
    except Exception as e:
        print('fill value error', e)

    return group

def archive_data(country='US'):
    path = '../COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/'
    files = os.listdir(path)
    files = [file for file in files if 'csv' in file]
    all_data = []
    for file in files:
        file_path = os.path.join(path, file)
        data = pd.read_csv(file_path)
        data.rename(columns={'Province/State': 'Province_State', 'Country/Region': 'Country_Region', 'Last Update': 'Last_Update'}, inplace=True)
        date = file.split('.')[0]
        date = date[6:]+'-'+date[:5]
        data = data.loc[data['Country_Region'] == country]
        data['updateDate'] = date
        all_data.append(data)

    # 城市数据
    city_data = pd.concat(all_data, axis=0, sort=False)
    city_data['Active'] = get_active(city_data)
    city_data = city_data.sort_values(['Admin2', 'Last_Update'])
    city_data.to_csv(f'data/{country}_city_data.csv', index=None)

    # 所有的日期
    dates = city_data['updateDate'].unique().tolist()
    dates.sort()

    # 各州数据
    state_data = city_data.groupby(['Province_State', 'updateDate'])[
        'Confirmed', 'Deaths', 'Recovered',	'Active'].sum()
    state_data.sort_index(inplace=True)
    state_data.reset_index(inplace=True)
    # state_data = state_data.groupby('Province_State').apply(lambda x: fill_data(x, dates))
    grouped = state_data.groupby('Province_State')

    ans = []
    for name, group in grouped:
        try:
            tmp = fill_data(group, dates)
            ans.append(tmp)
        except Exception as e:
            print(e)
    if ans:
        state_data = pd.concat(ans, axis=0, sort=False)
        state_data.reset_index(inplace=True)
        state_data = state_data.sort_values(['Province_State', 'updateDate'])
        state_data.rename(columns={'Province_State': 'provinceName'}, inplace=True)
        state_data.to_csv(f'data/{country}_province_data.csv', index=None)
    else:
        print('Province_State 为空值，无法提取省/州数据')

if __name__ == '__main__':
    archive_data('US')
    # archive_data('Italy')
    # archive_data('Germany')

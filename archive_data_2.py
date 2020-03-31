import pandas as pd
import numpy as np
import os


def fix_values( values):
        ans = []
        for value in values:
            if not ans or value > ans[-1]:
                ans.append(value)
            else:
                ans.append(ans[-1])
        return ans

def new_confirmed(data):
        values = data['Confirmed'].values
        new_confirmed = values[1:] - values[:-1]
        new_confirmed = [values[0]] + new_confirmed.tolist()
        new_confirmed = [i if i > 0 else 0 for i in new_confirmed]
        return new_confirmed

def fill_data(group, dates):
    try:
        group.sort_values('updateDate', inplace=True)
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
        group['Confirmed'] = fix_values(
            group['Confirmed'].values)
        group['Deaths'] = fix_values(group['Deaths'].values)
        group['Deaths'] = fix_values(group['Deaths'].values)

        # 新增确诊
        group['newConfirmed'] = new_confirmed(group)
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
    city_data = pd.concat(all_data, axis=0)
    city_data.to_csv(f'data/{country}_city_data.csv', index=None)

    # 所有的日期
    dates = city_data['updateDate'].unique().tolist()
    dates.sort()

    # 各州数据
    state_data = city_data.groupby(['Province_State', 'updateDate'])[
        'Confirmed', 'Deaths', 'Recovered',	'Active'].sum()
    state_data.sort_index(inplace=True)
    state_data.reset_index(inplace=True)
    # import pdb;pdb.set_trace()
    # state_data = state_data.groupby('Province_State').apply(lambda x: fill_data(x, dates))
    grouped = state_data.groupby('Province_State')
    print(grouped.size())
    ans = []
    for name, group in grouped:
        try:
            tmp = fill_data(group, dates)
            ans.append(tmp)
        except Exception as e:
            print(e)
    state_data = pd.concat(ans, axis=0)
    state_data.reset_index(inplace=True)
    state_data.sort_values(['Province_State', 'updateDate'], inplace=True)
    state_data.rename(columns={'Province_State': 'provinceName'}, inplace=True)
    state_data.to_csv(f'data/{country}_province_data.csv', index=None)


if __name__ == '__main__':
    # archive_data('US')
    archive_data('Italy')


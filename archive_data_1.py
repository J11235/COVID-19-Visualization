import pandas as pd
import numpy as np
import re
import os


def data_check():
    if not os.path.exists('../DXY-COVID-19-Data'):
        print('开始clone数据仓库DXY-COVID-19-Data...')
        from git import Repo
        Repo.clone_from(
            'https://github.com/BlankerL/DXY-COVID-19-Data.git', '../DXY-COVID-19-Data')
        print('clone完成')

data_check()


class ArchiveData:
    def __init__(self):
        self._init_data()

    def _init_data(self):
        self.data = pd.read_csv('../DXY-COVID-19-Data/csv/DXYArea.csv',
                        parse_dates=['updateTime'])
        self.data['updateDate'] = self.data['updateTime'].apply(lambda x: str(x.date()))
        self.dates = self.data['updateDate'].unique().tolist()
        self.dates.sort()
    
    def _name_adapter(self, data):
        if 'countryEnglishName' in data.columns:
            data['countryEnglishName'].loc[data['countryEnglishName']
                                        == 'United States of America'] = 'United States'
        # countryName表示国家或地区
        if 'countryName' in data.columns:
            data['countryName'].loc[data['countryEnglishName']
                                    == 'Hongkong'] = '香港'
            data['countryName'].loc[data['countryEnglishName']
                                    == 'Macao'] = '澳门'
        if 'provinceName' in data.columns:
            data['provinceName'] = data['provinceName'].apply(lambda x: re.sub('市|省|自治区', '', x))
        return data

    # 填充缺失数据
    def _fill_data(self, group):
        group = group.sort_values('updateDate')
        valid_dates = group['updateDate'].values.tolist()
        begin_date = min(valid_dates)
        group.set_index('updateDate', inplace=True)
        for last_date, date in zip(self.dates[:-1], self.dates[1:]):
            try:
                if last_date >= begin_date and date not in group.index:
                    group.loc[date] = group.loc[last_date].values
            except Exception as e:
                print('fill data error', e)
        group.sort_index(inplace=True)
        group.reset_index('updateDate', inplace=True, drop=False)
        
        #修正这三项数据，保持单调递增
        group['confirmedCount'] = self._fix_values(group['confirmedCount'].values)
        group['deadCount'] = self._fix_values(group['deadCount'].values)
        group['curedCount'] = self._fix_values(group['curedCount'].values)
        
        # 新增确诊
        group['newConfirmed'] = self._new_confirmed(group)

        return group

    # 确保部分数据是单增的
    def _fix_values(self, values):
        ans = []
        for value in values:
            if not ans or value > ans[-1]:
                ans.append(value)
            else:
                ans.append(ans[-1])
        return ans

    # 现存确诊
    def _current_active(self, data):
        current_active = data['confirmedCount'] - \
            data['curedCount'] - \
            data['deadCount']
        current_active = np.where(current_active < 0, 0, current_active)
        return current_active

    # 新增确诊
    def _new_confirmed(self, data):
        values = data['confirmedCount'].values
        new_confirmed = values[1:] - values[:-1]
        new_confirmed = [values[0]] + new_confirmed.tolist()
        new_confirmed = [i if i > 0 else 0 for i in new_confirmed]
        return new_confirmed
        
    def get_china_city_data(self):
        china_data_detail = self.data.loc[(self.data['countryEnglishName'] == 'China') & (
            self.data['provinceEnglishName'] != 'China')]

        # 只保留每天的最后一条数据
        city_grouped = china_data_detail.groupby(
            ['countryName', 'countryEnglishName', 'provinceName', 'cityName', 'updateDate'])
        self.china_city_data = city_grouped[['city_confirmedCount', 'city_suspectedCount',
                                               'city_curedCount', 'city_deadCount', 'updateTime']].apply(lambda x: x.sort_values('updateTime').iloc[-1])
        self.china_city_data.reset_index(inplace=True)
        self.china_city_data.columns = [column.split(
            '_')[-1] for column in self.china_city_data.columns]

        city_grouped = self.china_city_data.groupby(
            ['countryName', 'countryEnglishName', 'provinceName', 'cityName'])
        self.china_city_data = city_grouped.apply(self._fill_data)
        self.china_city_data.reset_index(inplace=True, drop=True)
        
        self.china_city_data['Active'] = self._current_active(self.china_city_data)

        self.china_city_data = self._name_adapter(self.china_city_data)
        self.china_city_data.rename(
            columns={'confirmedCount': 'Confirmed', 'suspectedCount': 'Suspected', 'curedCount': 'Recovered', 'deadCount': 'Deaths'}, inplace=True)
        self.china_city_data.to_csv('data/china_city_data.csv', index=None)

    def get_china_province_data(self):
        province_grouped = self.china_city_data.groupby(['countryName', 'countryEnglishName', 'provinceName', 'updateDate'])
        self.china_province_data = province_grouped[['Confirmed', 'Suspected',
                                                     'Recovered', 'Deaths', 'newConfirmed', 'Active']].sum()
        self.china_province_data.reset_index(inplace=True)
        self.china_province_data.to_csv('data/china_province_data.csv', index=None)

    def get_china_country_data(self):
        grouped = self.china_province_data.groupby(['countryName', 'countryEnglishName', 'updateDate'])
        china_country_data = grouped[['Confirmed', 'Suspected',
                                      'Recovered', 'Deaths', 'newConfirmed', 'Active']].sum()
        china_country_data.reset_index(inplace=True)
        return china_country_data

    def get_other_country_data(self):
        other_country_data = self.data.loc[(self.data['countryEnglishName'] != 'China')]
        grouped = other_country_data.groupby(['countryName', 'countryEnglishName', 'updateDate'])
        other_country_data = grouped[['province_confirmedCount', 'province_suspectedCount',
                            'province_curedCount', 'province_deadCount', 'updateTime']].apply(lambda x: x.sort_values('updateTime').iloc[-1])
        other_country_data.reset_index(inplace=True)
        other_country_data.columns = [column.split('_')[-1] for column in other_country_data.columns]
        other_country_data = other_country_data.groupby('countryEnglishName').apply(self._fill_data)
        other_country_data.reset_index(inplace=True, drop=True)
        
        other_country_data['Active'] = self._current_active(
            other_country_data)

        other_country_data = self._name_adapter(other_country_data)
        other_country_data.rename(
            columns={'confirmedCount': 'Confirmed', 'suspectedCount': 'Suspected', 'curedCount': 'Recovered', 'deadCount': 'Deaths'}, inplace=True)
        return other_country_data

    def get_world_country_data(self):
        china_country_data = self.get_china_country_data()
        other_country_data = self.get_other_country_data()
        world_country_data = pd.concat([china_country_data, other_country_data], axis=0, sort=True)
        world_country_data = world_country_data.sort_values(
            by=['countryEnglishName', 'updateDate'])
        world_country_data.to_csv('data/world_country_data.csv')


if __name__ == '__main__':
     p = ArchiveData()
     p.get_china_city_data()
     p.get_china_province_data()
     p.get_world_country_data()

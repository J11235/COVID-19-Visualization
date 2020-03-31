import time
import sys
from snapshot_phantomjs import snapshot
# from snapshot_selenium import snapshot
# from snapshot_pyppeteer import snapshot
from pyecharts.render import make_snapshot
from pyecharts.datasets import register_url
from pyecharts.faker import Faker
from pyecharts.charts import Map, Bar, Grid
from pyecharts import options as opts
import pandas as pd
import numpy as np
import os

import pyecharts.options as opts
from pyecharts.globals import ThemeType
from pyecharts.commons.utils import JsCode
from pyecharts.charts import Timeline, Grid, Bar, Map, Pie, Line

print(os.listdir('../../'))

class Visualization:
    def __init__(self, datatype='Confirmed', increment_update=True, maptype='world'):
        assert datatype in ['Confirmed', 'Deaths', 'Suspected',
                            'Recovered', 'Active', 'newConfirmed'], 'datatype must in Confirmed, Deaths, Suspected, Recovered, Active, newConfirmed'
        self.datatype = datatype
        self.increment_update = increment_update
        assert maptype in ['world', 'china-cities', 'china', '美国'], 'maptype must be world or china-cities or china'
        self.maptype = maptype

        self.cum_dates = []
        self.cum_values = []

        self._load_data()
        self._init_title()

    def _load_data(self):
        if self.maptype == 'china-cities':
            self.data = pd.read_csv('data/china_city_data.csv')
        elif self.maptype == 'china':
            self.data = pd.read_csv('data/china_province_data.csv')
        elif self.maptype == '美国':
            self.data = pd.read_csv('data/US_province_data.csv')
        else:
            self.data = pd.read_csv('data/world_country_data.csv')
        self.dates = self.data.updateDate.unique().tolist()
        self.dates.sort()

    def _init_title(self):
        en2zh = {}
        en2zh['Confirmed'] = '累计确诊'
        en2zh['Deaths'] = '累计死亡'
        en2zh['Recovered'] = '累计治愈'
        en2zh['Active'] = '现存确诊'
        en2zh['newConfirmed'] = '新增确诊'

        if self.maptype == 'world':
            name1, name2 = '全球', '国家/地区'
        elif self.maptype == 'china-cities':
            name1, name2 = '中国', '城市' 
        elif self.maptype == 'china':
            name1, name2 = '中国', '省份'
        elif self.maptype == '美国':
            name1, name2 = '美国', '州'

        self.map_title = f"COVID-19 {name1}{en2zh.get(self.datatype)}分布情况"
        self.bar_title = f"{en2zh.get(self.datatype)}前十{name2}"
        self.line_title = f"{name1}{en2zh.get(self.datatype)}"
        self.pie_title = f"{en2zh.get(self.datatype)}前十占比"

    def get_one_day_data(self, date):
        subdata = self.data.loc[self.data['updateDate'] == date]
        subdata.sort_values(self.datatype, ascending=False, inplace=True)
        values = subdata[self.datatype].values.tolist()
        english_names = None
        if self.maptype == 'world':
            names = subdata['countryName'].values.tolist()
            english_names = subdata['countryEnglishName'].values.tolist()
        elif self.maptype == 'china-cities':
            names = subdata['cityName'].values.tolist()
        else:
            names = subdata['provinceName'].values.tolist()

        top10_values = values[:10]
        top10_names = names[:10]
        
        if self.increment_update:
            self.cum_dates = [date[5:] for date in self.dates]
            self.cum_values = self.data.groupby('updateDate')[self.datatype].apply(np.sum).loc[self.dates].values
        else:
            self.cum_dates.append(date[5:])
            self.cum_values.append(subdata[self.datatype].sum())

        return names, english_names, values, top10_names, top10_values


    def get_day_chart(self, date: str):
        names, english_names, values, top10_names, top10_values = self.get_one_day_data(
            date)
        if self.maptype == 'world':
            min_data, max_data = 0, max(values)
        elif self.maptype == 'china-cities':
            min_data, max_data = 0, 3000
        else:
            min_data, max_data = 0, 5000
        data_mark = [0]*len(self.dates)

        names_ = english_names if self.maptype == 'world' else names

        if self.maptype == '美国':
            try:
                register_url("https://echarts-maps.github.io/echarts-countries-js/")
            except Exception:
                import ssl
                ssl._create_default_https_context = ssl._create_unverified_context
                register_url("https://echarts-maps.github.io/echarts-countries-js/")
        
        map_chart = (
            Map()
            .add(series_name="",
                 data_pair=[list(z) for z in zip(names_, values)],
                 maptype=self.maptype, is_map_symbol_show=False, zoom=1)
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title=f"{date}: "+self.map_title, pos_left='35%', title_textstyle_opts=opts.TextStyleOpts(color='white')),
            )
        )

        line_chart = (
            Line()
            .add_xaxis(self.cum_dates)
            .add_yaxis(series_name="",
                       y_axis=self.cum_values,
                       markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max")]))
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
                # xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(is_show=False)),
                # yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(is_show=False)),
                title_opts=opts.TitleOpts(
                    title=self.line_title, pos_left="5%", pos_top="5%", title_textstyle_opts=opts.TextStyleOpts(color='white')
                )
            )
        )

        bar_x_data = top10_names[::-1]
        bar_y_data = [{"name": name, "value": value}
                      for name, value in zip(top10_names, top10_values)][::-1]
        bar = (
            Bar()
            .add_xaxis(xaxis_data=bar_x_data)
            .add_yaxis(
                series_name="",
                yaxis_data=bar_y_data,
                label_opts=opts.LabelOpts(
                    is_show=True, position="right", formatter="{b} : {c}"
                ),
            )
            .reversal_axis()
            .set_global_opts(
                # xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(is_show=False)),
                # yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(is_show=False)),
                title_opts=opts.TitleOpts(
                    title=self.bar_title, pos_left="5%", pos_top="50%", title_textstyle_opts=opts.TextStyleOpts(color='white')),
                tooltip_opts=opts.TooltipOpts(is_show=False),
                visualmap_opts=opts.VisualMapOpts(
                    is_calculable=True,
                    dimension=0,
                    pos_right="10%",
                    pos_top="top",
                    range_text=["High", "Low"],
                    range_color=["lightskyblue", "yellow", "orangered"],
                    textstyle_opts=opts.TextStyleOpts(color="#ddd"),
                    min_=min_data,
                    max_=max_data,
                ),
            )
        )

        sum_ = sum(values)
        pie_data = [[name, '%.2f' % (value/sum_)] for name, value in zip(top10_names, top10_values)]
        rest_value = 1-sum(top10_values)/sum_
        pie_data.append(["其他", '%.2f' % rest_value])

        if self.maptype == 'world':
            center = ["68%", "87%"]
            pos_left = "62%"
            pos_top = "67%"
        else:
            center = ["85%", "85%"]
            pos_left = "79%"
            pos_top = "65%"
        pie = (
            Pie()
            .add(
                series_name="",
                data_pair=pie_data,
                radius=["12%", "20%"],
                center=center,
                itemstyle_opts=opts.ItemStyleOpts(
                    border_width=1, border_color="rgba(0,0,0,0.3)"
                ),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title=self.pie_title, pos_left=pos_left, pos_top=pos_top, title_textstyle_opts=opts.TextStyleOpts(
                        color='white')
                ),
                tooltip_opts=opts.TooltipOpts(
                    is_show=True, formatter="{b} {c}%"),
                legend_opts=opts.LegendOpts(is_show=False),
            )
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        )

        grid_chart = (
            Grid(init_opts=opts.InitOpts(page_title=date))
            .add(
                bar,
                grid_opts=opts.GridOpts(
                    pos_left="10", pos_right="80%", pos_top="55%", pos_bottom="1%"
                ),
            )
            .add(
                line_chart,
                grid_opts=opts.GridOpts(
                    pos_left="10", pos_right="80%", pos_top="10%", pos_bottom="55%"
                ),
            )
            .add(pie, grid_opts=opts.GridOpts())
            .add(map_chart, grid_opts=opts.GridOpts(pos_left="50%"))
        )

        return grid_chart


def main(datatype='Confirmed', increment_update=False, maptype='china-cities', save_png=False):
    visual_data = Visualization(datatype=datatype, increment_update=increment_update, maptype=maptype)
    dates = visual_data.dates
    if increment_update:
        date = dates[-1]
        g = visual_data.get_day_chart(date=date)
        if save_png:
            make_snapshot(snapshot, g.render(),
                          f"fig/png/COVID-19_{datatype}_{maptype}_{date}.png")
    else:
        timeline = Timeline(
            init_opts=opts.InitOpts(
                width="1440px", height="800px", theme=ThemeType.DARK)
        )
        for date in dates:
            g = visual_data.get_day_chart(date=date)
            timeline.add(g, time_point=date[6:])
            if save_png:
                make_snapshot(snapshot, g.render(), f"fig/png/COVID-19_{datatype}_{maptype}_{date}.png")

        timeline.add_schema(
            orient="vertical",
            is_auto_play=True,
            is_inverse=True,
            play_interval=5000,
            pos_left="null",
            pos_right="5",
            pos_top="20",
            pos_bottom="20",
            width="60",
            label_opts=opts.LabelOpts(is_show=True, color="#fff"),
        )

        timeline.render(f"fig/html/COVID-19-{maptype}-{datatype}.html")

def main_v2():
    for maptype in ['china', 'world', '美国']:
        for datatype in ['Confirmed', 'newConfirmed', 'Active']:
            main(datatype=datatype, maptype=maptype, save_png=True, increment_update=False)

if __name__ == "__main__":
    # main(datatype='Confirmed', maptype='china-cities')
    # main(datatype='Confirmed', maptype='china')
    # main(datatype='Active', maptype='china')

    # main(datatype='Confirmed', maptype='world')

    # main(datatype='Confirmed', maptype='美国')

    # main(datatype='Deaths')
    # main(datatype='Recovered')
    # main(datatype='Active')
    # main(datatype='newConfirmed')
    main_v2()

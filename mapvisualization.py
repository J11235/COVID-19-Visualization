import sys
import imageio
from snapshot_phantomjs import snapshot
from pyecharts.render import make_snapshot
import pdb
from pyecharts.faker import Faker
from pyecharts.charts import Map, Bar, Grid
from pyecharts import options as opts
import pandas as pd
import numpy as np
import os
print(os.listdir('../../'))

def visualization():
    data = pd.read_csv('../DXY-COVID-19-Data/csv/DXYArea.csv', parse_dates=['updateTime'])
    data['updateDate'] = data['updateTime'].apply(lambda x: str(x.date()))
    import pdb;pdb.set_trace()
    data_ = data.loc[data['countryEnglishName'] == 'China']
    data_[['updateTime', 'province_confirmedCount']]
    data['countryEnglishName'].loc[data['countryEnglishName']
                                == 'United States of America'] = 'United States'
    data = data.groupby(['countryEnglishName', 'updateDate'])[[
        'province_confirmedCount']].max()
    data.reset_index(inplace=True)
    data.to_csv('各国累计确诊.csv')
    data.sort_values(by=['countryEnglishName', 'updateDate'], inplace=True)
    dates = data['updateDate'].unique()

    for date in dates:
        subdata = data.loc[data['updateDate'] == date]
        values = np.sqrt(subdata['province_confirmedCount'].values).tolist()
        max_data = max(values)
        countries = subdata['countryEnglishName'].values.tolist()

        subdata_top10 = subdata.sort_values(
            'province_confirmedCount', ascending=False)
        top10_country = subdata_top10['countryEnglishName'].values.tolist()
        top10_value = subdata_top10['province_confirmedCount'].values.tolist()

        map_chart = (
            Map()
            .add("全球疫情趋势", [list(z) for z in zip(countries, values)], "world", is_map_symbol_show=False)
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
                title_opts=opts.TitleOpts(title=f"日期: {date}"),
                visualmap_opts=opts.VisualMapOpts(max_=max_data),
            )
        )


        bar_chart = (
            Bar()
            .add_xaxis(xaxis_data=top10_country)
            .add_yaxis(
                series_name="",
                yaxis_data=top10_value,
                label_opts=opts.LabelOpts(
                    is_show=True, position="right", formatter="{b} : {c}"
                ),
            )
            .reversal_axis()
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(
                    max_=10000, axislabel_opts=opts.LabelOpts(is_show=False)
                ),
                yaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(is_show=False)),
                tooltip_opts=opts.TooltipOpts(is_show=False),
                visualmap_opts=opts.VisualMapOpts(
                    is_calculable=True,
                    dimension=0,
                    pos_left="10",
                    pos_top="top",
                    range_text=["High", "Low"],
                    range_color=["lightskyblue", "yellow", "orangered"],
                    textstyle_opts=opts.TextStyleOpts(color="#ddd"),
                    min_=0,
                    max_=max_data,
                ),
            )
        )


        grid_chart = (
            Grid()
            .add(map_chart, grid_opts=opts.GridOpts())
            .add(bar_chart, grid_opts=opts.GridOpts())
        )
        make_snapshot(snapshot, grid_chart.render(),
                      f"fig/png/全球疫情趋势{date}.png")
        grid_chart.render(f"fig/html/全球疫情{date}.html")

        print('%s数据可视化完成' % date)


def png2gif():
    frames = []
    imgs = os.listdir('fig/png/')
    imgs.sort()
    for img in imgs:
        frames.append(imageio.imread('fig/png/'+img))
    imageio.mimsave('fig/全球疫情.gif', frames, 'GIF', duration=0.5)

if __name__ == '__main__':
    visualization()
    # png2gif()

#\38 8cf8a7de3bc4f199d6d6ad432aadbe7 > div:nth-child(1) > canvas
#\38 8cf8a7de3bc4f199d6d6ad432aadbe7 > div:nth-child(1) > canvas
#\38 8cf8a7de3bc4f199d6d6ad432aadbe7 > div:nth-child(1) > canvas
document.querySelector(
    "#\\38 8cf8a7de3bc4f199d6d6ad432aadbe7 > div:nth-child(1) > canvas")

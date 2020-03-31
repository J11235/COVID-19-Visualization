from pyecharts.globals import ChartType
from pyecharts.faker import Faker
from pyecharts.charts import Geo
from pyecharts import options as opts
from pyecharts.charts import Geo, Map
from pyecharts.datasets import register_url

# try:
#     register_url("https://echarts-maps.github.io/echarts-countries-js/")
# except Exception:
#     import ssl

#     ssl._create_default_https_context = ssl._create_unverified_context
#     register_url("https://echarts-maps.github.io/echarts-countries-js/")

# geo = (
#     Geo()
#     .add_schema(maptype="美国")
#     .add(series_name="",
#                      data_pair=[list(z) for z in zip(['South Carolina', 'South Carolina'], [100, 200])])
#     .set_global_opts(title_opts=opts.TitleOpts(title="美国"))
#     .render("geo_chart_countries_js.html")
# )


# c = (
#     Geo()
#     .add_schema(maptype="美国")
#     .add(
#         "geo",
#         [list(z) for z in zip(['纽约州'], [100])],
#         type_=ChartType.HEATMAP,
#     )
#     .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
#     .set_global_opts(
#         visualmap_opts=opts.VisualMapOpts(), title_opts=opts.TitleOpts(title="Geo-广东地图")
#     )
#     .render("geo_guangdong.html")
# )

from pyecharts import options as opts
from pyecharts.charts import Geo
from pyecharts.datasets import register_url

try:
    register_url("https://echarts-maps.github.io/echarts-countries-js/")
except Exception:
    import ssl

    ssl._create_default_https_context = ssl._create_unverified_context
    register_url("https://echarts-maps.github.io/echarts-countries-js/")

geo = (
    Map()
    .add(series_name="",
        maptype="美国",
        data_pair=[list(z) for z in zip(['Texas'], [100])],
        # type_=ChartType.HEATMAP,
    )
    .set_global_opts(title_opts=opts.TitleOpts(title="瑞士"))
    .render("geo_chart_countries_js.html")
)


# import pdb;pdb.set_trace()

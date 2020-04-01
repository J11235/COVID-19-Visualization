# COVID-19疫情地图可视化

## 项目介绍
本项目为2019新型冠状病毒（COVID-19）疫情数据可视化项目,数据来源为基于[丁香园](https://3g.dxy.cn/newh5/view/pneumonia)的爬虫数据[DXY-COVID-19-Data](https://github.com/BlankerL/DXY-COVID-19-Data),还有约翰霍普金斯大学整理的数据[COVID-19](https://github.com/CSSEGISandData/COVID-19).

## 准备
将本项目以及前面两个数据项目clone到本地, 且三个项目在同一级目录.如果数据项目不存在,运行代码时会自动clone.

## 文件介绍
DXY-COVID-19-Data和COVID-19存在一天多次采集数据、某些天没有数据的情况. 

1. [archive_data_1.py](archive_data_1.py)整理了DXY-COVID-19-Data, 将数据归档为中国各城市数据、中国各省数据以及各国数据.

2. [archive_data_2.py](archive_data_2.py)整理了COVID-19, 将数据归档为美国各州数据.

整理后的数据放在[data](data/)目录下.

3. [visualization.py](visualization.py)是可视化脚本,可视化结果为html文件,放在了[fig/html](fig/html)目录下; 也可将html依赖的js通过phantomjs将渲染成图片,放在[fig/png](fig/png)目录下.

4. [png2video.py](png2video.py)将多张图片转化成视频, 放在[video](video)目录下. 

## 其它
我发现phantomjs渲染的图片质量不如chome浏览器打开html后的图片质量, 因此又采用了先录屏html文件、再剪辑视频. 这个方法比png2video.py产生的视频质量高,但不够自动化.
如果大家有更好的办法，可以告诉我一声.

## 最后
感谢原数据的提供者.

祝大家平安.
# -*- coding: UTF-8 -*-
import os
import cv2
import time
 
# 图片合成视频
def target_file(file, maptype, datetype):
    if datetype in file and maptype in file:
        return True
    else:
        return False

def png2video(maptype='world', datetype='Confirmed'):
    filelist = os.listdir('fig/png')
    filelist = [file for file in filelist if target_file(
        file, datetype, maptype)]
    filelist.sort()
    
    filelist = filelist[2:] + filelist[-1:]*5  #最后一张图片出现6次，停留2秒

    fps = 3  #每秒3张图片
    size = (1800, 1000)
    file_path = f"video/{datetype}_{maptype}.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video = cv2.VideoWriter(file_path, fourcc, fps, size)
 
    for file in filelist:
        if file.endswith('.png'):
            file = os.path.join('fig/png/', file)
            img = cv2.imread(file)
            video.write(img)
    video.release()
 

def all_videos():
    datatypes = ['Confirmed', 'Deaths', 'Recovered', 'Active', 'newConfirmed']
    maptypes = ['world', 'china', 'china-cities', '美国']
    for datatype in datatypes:
        for maptype in maptypes:
            try:
                png2video(datetype=datatype, maptype=maptype)
            except Exception as e:
                print(e)

if __name__ == '__main__':
    png2video(datetype='Confirmed', maptype='美国')
    png2video(datetype='Active', maptype='world')

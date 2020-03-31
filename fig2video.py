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

def picvideo(maptype='world', datetype='confirmedCount'):
    filelist = os.listdir('fig/png')
    filelist = [file for file in filelist if target_file(
        file, datetype, maptype)]
    filelist.sort()
    filelist = filelist[2:] + filelist[-1:]*5

    fps = 3
    size = (1800, 1000)
    file_path = f"video/world_{datetype}_{maptype}.mp4"
    # fourcc = cv2.VideoWriter_fourcc('I', '4', '2', '0')
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video = cv2.VideoWriter(file_path, fourcc, fps, size)
 
    for item in filelist:
        if item.endswith('.png'):
            item = os.path.join('fig/png/', item)
            img = cv2.imread(item)
            video.write(img)
    video.release()
 

def all_videos():
    datatypes = ['confirmedCount','deadCount','curedCount','nowExistCount','newCount']
    maptypes = ['world', 'china', 'china-cities']
    for datatype in datatypes:
        for maptype in maptypes:
            picvideo(datetype=datatype, maptype=maptype)

if __name__ == '__main__':
    picvideo(datetype='confirmedCount', maptype='china-cities')

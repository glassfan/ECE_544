# -*- coding: utf-8 -*-
"""
# Created on Fri Jun  9 15:52:59 2017
# pull_urls.py
# @author: Dakota Ward
# USAGE: Requires:  python 3+
#                   Opencv 3.2 ["import cv2"]
#                   internet connection 
#                   python urllib lib ["import urllib"]
#                   python numpy lib  ["import numpy" ]
#                   python os lib     ["import os"    ]
# Description:
# Python script pulls urls from http://www.image-net.org/.
# used to build training data fro custom built OpenCV Haar-classifiers.
# 
# File structure:
#    -positive_samples:  destination folder of positive training data
#    -negative samples:  destination folder of negative training data
#    -rejects:           destination folder of bad url downloads
# 
# USAGE:
#    Navigate to Image net and in search box enter the images desired. 
#    In the preceding page click on the "Downloads" link.
#    In the preceding page click on the "URLS" link
#    copy and past the sysnet # i.e n04255586", this is the link to your image category
#    In line # 74 replace the sysnet # with the contents of your clipboard
#    Run the script, making sure to comment out Line # 75
#    Bad urls will fill a portion of your destination folder, once script has finished running,
#    Copy and paste each type of bad URL into the "rejects" destination folder
#    Rerun the script uncommenting line #75 and commenting out Line # 74. This will remove all bad URL downloads.
"""

import urllib.request
import cv2
import numpy as np
import os

def pull_samples(url_link, filename, url_num, height):
    images_link = url_link   #replace the wnid="<insert synset #>"
    image_urls = urllib.request.urlopen(images_link).read().decode()
    pic_num = url_num  # hardcoded placeholder, for appending further images
    
    for i in image_urls.split('\n'):
        try:
            print(i)
            urllib.request.urlretrieve(i, filename+str(pic_num)+".jpg")
            img = cv2.imread(filename+str(pic_num)+".jpg",cv2.IMREAD_GRAYSCALE) #relative path to destination folder
            # negative samples should be larger than postive sample images
            
            #to preserve aspect ratio (use if needed)
            r = 100.0 / img.shape[1]
            dim = (height, int(img.shape[0] * r))
            resized_image = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
            cv2.imwrite(filename+str(pic_num)+".jpg",resized_image)
            pic_num += 1
            
        except Exception as e:
            print(str(e))
            
            
def find_errors(filename):
    for file_type in [filename]:
        for img in os.listdir(file_type):
            for badPic in os.listdir('rejects'): #'rejects' is src folder of error jpgs copy and pasted from dst folder of pulled images
                try:
                    current_image_path = str(file_type)+'/'+str(img)
                    badPic = cv2.imread('rejects/'+str(badPic))
                    question = cv2.imread(current_image_path)
                    if badPic.shape == question.shape and not(np.bitwise_xor(badPic,question).any()):
                        print('Deleting jpg error')
                        print(current_image_path)
                        os.remove(current_image_path)
                except Exception as e:
                    print(str(e))



pull_samples("http://image-net.org/api/text/imagenet.synset.geturls?wnid=n04255586", "resized_positives/", 1, 75)
find_errors("resized_positives/")
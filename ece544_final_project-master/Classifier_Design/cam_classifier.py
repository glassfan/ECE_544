# -*- coding: utf-8 -*-
"""
# Created on Mon Jun  5 22:05:00 2017
# cam_classifier.py
# @author: Dakota
# USAGE: Requires:  python 3+
#                   Opencv 3.2 ["import cv2"]
#                   usb web camera 
#                   python imutils lib ["import imutils"]
# Description:
# Python script runs in a main loop capturing frames from webcamera for image recognition.
# A Haar-cascade classifier is used in a sliding detection window. Postive identification produces
# a green bounding box around the reconized "soda can"
"""

import cv2
import imutils


def detect(img, cascade):
    # scans input image with classifier
    # path to image can be relative
    
    rects = cascade.detectMultiScale(img, scaleFactor=1.06, minNeighbors=3, minSize=(30, 30),
                                     flags=cv2.CASCADE_SCALE_IMAGE)
    if len(rects) == 0:
        return []
    rects[:,2:] += rects[:,:2]
    return rects


def draw_rects(img, rects, color):
    # Draw bounding rectangle on image
    
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)


cascade = cv2.CascadeClassifier('cascade.xml')      #path to classifier


cap = cv2.VideoCapture(0)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    
    frame = imutils.resize(frame,width=500)         #resixe frame for performance boost
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  #convert frame to gray scale
    gray = cv2.equalizeHist(gray)                   # smoothing operation
    
    rects = detect(gray, cascade)                   #run classifier against input image
    vis = frame.copy()
    draw_rects(vis, rects, (0, 255, 0))             #display bounding box around ROI

    # Display the resulting frame
    cv2.imshow('Video', vis)
    #cv2.imshow('Video', gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
cap.release()
cv2.destroyAllWindows()

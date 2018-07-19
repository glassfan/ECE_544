# -*- coding: utf-8 -*-
"""
# Created on Mon Jun  5 22:20:23 2017
# webcam_test.py
# @author: Dakota
# USAGE: Requires:  python 3+
#                   Opencv 3.2 ["import cv2"]
#                   usb web camera 
#                  
# Description:
# Python script runs in a main loop capturing frames from webcamera.
# Used to test the functionality of the web camera
# 
# USAGE:
    plug in USB webcamera, run script
    *Depending on configuration Line # 22 cv2.VideoCapture(0) needs to be changed
    * cv2.VideoCapture(<Insert Correct value here>)
"""


import cv2

cap = cv2.VideoCapture(0)

while(True):

    # Capture frame-by-frame

    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    cv2.imshow('frame',gray)
    
    # break if q is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
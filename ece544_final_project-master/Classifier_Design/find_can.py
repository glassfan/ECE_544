"""# -*- coding: utf-8 -*-
# find.can.py
# Created on Tue Jun  6 12:19:28 2017
# @author: Dakota
# USAGE: Requires:  python 3+
#                   Opencv 3.2 ["import cv2"]
#                   usb web camera 
#                   python numpy lib ["import numpy"]
#
# Description:
# Python script runs in a main loop capturing frames from webcamera for image processing.
# If red soda can object or blue paper square (hung vertically) is present in image,
# then positive identification of image will be confirmed by a red bounding box around the target ROI
#
# Robot motor control functions are commented out, as this script is meant to test the object detection
# separately from motor control 
"""

import numpy as np
import cv2

'''
used to grab actual camera frame dimensions
#fWidth = cap.get(3)
#fHeight = cap.get(4)
'''
def update_shape(contours):
    # from contour data ,approximate the shape with the arc lengths of the contours 
    approx = cv2.approxPolyDP(contours,0.01*cv2.arcLength(contours,True),True) 
    if len(approx) == 4:
        return "square"
            
    elif len(approx) > 8 and len(approx) < 12:
        return "cylinder"        
    else:
        return "invalid"
   
def update_box_points(contours):
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    box = np.array(box, dtype="int")
    return box
    
    
def order_points(pts):
    # initialzie a list of coordinates that will be ordered
    # first entry in the list is the top-left,
    # second entry is the top-right, the third is the
    # bottom-right, and the fourth is the bottom-left
    rect = np.zeros((4, 2), dtype = "float32")
    
    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    
    # compute the difference between the points
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    # return the ordered coordinates
    return rect
 
def get_dimensions(pts,known_width):
    dimensions = {"height_px":None, "width_px":None, "w_In":None}
    
    # obtain a consistent order of the points and unpack them
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    # compute the width of the bounding box, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordiates or the top-right and top-left x-coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    dimensions["width_px"] = maxWidth
    dimensions["w_In"] = maxWidth/known_width
              
    # compute the height of the bounding box, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    dimensions["height_px"] = maxHeight
    return dimensions

       
def find_object_x_offset(centerX):
    # Find the x offset by taking the frame center (width/2) and subtract the current object's x-center.
    # This means that an object to the left of center will have a positive value and an object to the right
    # of center will have a negative value.  The offset should be at most abs(frame_in_w/2)
    return (frame_in_w/2) - centerX

'''
def center_to_object(xOffset):
    absX = abs(xOffset)
    if absX > 20:
        if xOffset < 0:
            my_robot.left()
            print(xOffset)
        else:
            my_robot.right()
            print(xOffset)
    elif absX <= 20:
        centered = True
'''        
def distance_to_camera(knownWidth, focalLength, percieved_width):
    # compute and return the distance from the maker to the camera
    return (knownWidth * focalLength) / percieved_width

def update_distance(known_width,focalLength, perWidth):
    inches = distance_to_camera(known_width, focalLength, perWidth)
    return inches

'''
def approach_object(distance):
    my_robot.release()
    for i in range(0,math.floor(distance)):
        my_robot.forward(0.05)
    
    my_robot.grip()
'''

'''
def get_can(position, distance):
    if not centered:
        center_to_object(position)
    else:
        approach_object(distance)
'''
        
#Camera Calibration Constants
#Known width of coke can/ drop off target
KNOWN_CAN_WIDTH          = 2.598    #inches
KNOWN_TARGET_WIDTH       = 13.937   #inches
KNOWN_CAN_PIXEL_WIDTH    = 133      #pixels
KNOWN_TARGET_PIXEL_WIDTH = 344      #pixels
KNOWN_CAN_DISTANCE       = 12       #inches
KNOWN_TARGET_DISTANCE    = 26       #inches
focalLength_can = (KNOWN_CAN_PIXEL_WIDTH * KNOWN_CAN_DISTANCE) / KNOWN_CAN_WIDTH
focalLength_target = (KNOWN_TARGET_PIXEL_WIDTH * KNOWN_TARGET_DISTANCE) / KNOWN_TARGET_WIDTH
frame_in_w               = 640      #pixels

#Global variables                     
cap = cv2.VideoCapture(0)
shape =' '
results ={}
position=' '
distance = 0
cnt_length = 0
centered = False


# define range of red color in HSV
lower_red = np.array([17, 15, 100], dtype=np.uint8)
upper_red = np.array([50, 56, 200], dtype=np.uint8)

# define range of blue color in HSV
lower_blue = np.array([92, 0, 0], dtype=np.uint8)
upper_blue = np.array([124, 255, 255], dtype=np.uint8)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    
    # Our operations on the frame come here
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # Threshold the HSV image to get only red colors
    mask_red = cv2.inRange(hsv, lower_red, upper_red)
    mask_blue  = cv2.inRange(hsv, lower_blue, upper_blue)
    mask_zero = np.zeros(hsv.shape[:2],np.uint8)
  
    # Filter Image
    # RGB to Gray scale conversion
    img_gray = cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)
    #cv2.imshow("Grayscale", img_gray)
    # Noise removal with iterative bilateral filter(removes noise while preserving edges)
    noise_removal = cv2.bilateralFilter(img_gray,9,75,75)
    # Thresholding the image
    ret,thresh_image = cv2.threshold(noise_removal,0,255,cv2.THRESH_OTSU)
    
    # Applying Canny Edge detection
    canny_image = cv2.Canny(thresh_image,250,255)
    canny_image = cv2.convertScaleAbs(canny_image)
    # dilation to strengthen the edges
    kernel = np.ones((3,3), np.uint8)
    # Creating the kernel for dilation
    dilated_image = cv2.dilate(canny_image,kernel,iterations=1)
    
    #find contour data
    __,contours,__ = cv2.findContours(dilated_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contours= sorted(contours, key = cv2.contourArea, reverse = True)[:1]
    
    for cnt in contours:
        	# if the contour is not sufficiently large, ignore it
            if cv2.contourArea(cnt) < 100:
                continue
            
            shape = update_shape(cnt)
            if (shape == "square"):             #Drop off target detected
                rect = cv2.minAreaRect(cnt)
                box = cv2.boxPoints(rect)
                box = np.array(box, dtype="int")
                cX = np.average(box[:, 0])      # compute the center of the bounding box
                
                # object identified, center and approach                
                results = get_dimensions(box, KNOWN_TARGET_WIDTH)
                position = find_object_x_offset(cX)
                #center_to_object(position)
                distance = update_distance(KNOWN_TARGET_WIDTH, focalLength_can, results["width_px"]) 
                #approach_object(distance)
                
                if cv2.countNonZero(mask_blue): # Drop off target is blue, only draw contours if blue detected
                    print("Blue detected")
                    mask_green = mask_zero
                    mask_red = mask_zero
                    cv2.drawContours(frame,[box],0,(0,0,255),2)
                else:                           #Blue not found, do nothing
                    continue
                
            elif (shape == "cylinder"):         #Soda can detected
                rect = cv2.minAreaRect(cnt)
                box = cv2.boxPoints(rect)
                box = np.array(box, dtype="int")
                cX = np.average(box[:, 0])      # compute the center of the bounding box
                
                # object identified, center and approach 
                results = get_dimensions(box, KNOWN_TARGET_WIDTH)
                position = find_object_x_offset(cX)
                #center_to_object(position)
                distance = update_distance(KNOWN_TARGET_WIDTH, focalLength_can, results["width_px"]) 
                #approach_object(distance)
                 
                if cv2.countNonZero(mask_red): # soda can target is red, only draw contours if red detected
                    print("Red detected")
                    mask_green = mask_zero
                    mask_blue = mask_zero
                    cv2.drawContours(frame,[box],0,(0,0,255),2)
                else:                          #Red not found, do nothing 
                    continue
            
          
    cv2.imshow("Soda Can", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
##### FOLLOWER CODE for ME35 Viennese Waltz
##### April 21st, 2021
##### references: https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/

##### THIS VERSION INCLUDES #####
## USB Serial Connection to SPIKE Prime
# sets up serial connection
# sends motor commands based on image detection directly to REPL over serial
## Image Detection
# detecting green using an image processing mask, dilations, erosions, and a Gaussian blur 
# traces a yellow circle over the pi camera image and indicates center with a red dot
# returns x values and radius
## Proportional Controller 
# 1. Controller to keep green dot in the center of the camera frame
    # takes the center x value of the green dot and compares it to the center x value of the image frame
    # if camera loses sight of the green dot, will check which side of the frame it disappeared off of
        # will spin in that direction (CW or CCW) until finds green dot again
        # will also gently honk
# 2. Controller to keep robot at a reasonable distance from the leader robot
    # takes the radius value of the green dot
    # if > threshold, will slow down 
    # if < threshold, will speed up
    # if = threshold, will stop

### IMPORTING MODULES + SERIAL ###  

from imutils.video import VideoStream
import numpy as np
import cv2
import imutils
import time
import math
import serial 
import os

# set up SERIAL connection 
os.chdir("/")
ser = serial.Serial(
    port = '/dev/ttyACM0',
    baudrate = 115200,
    parity = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    bytesize = serial.EIGHTBITS,
    timeout = 1
)

### WHAT IS GREEN ###

# define the lower and upper boundaries of the "green" based off of green_detection.py code
# values are in the HSV color space
greenLower = (36, 25, 25)
greenUpper = (70, 255, 255)

### VARIABLES ###

# for following center of ball
prev_x = 1
center_x = 320
kp = 0.04
ki = 0.01
integral = 0
error = 0
# for following distance 
kp_rad = 0.4
ki_rad = 0.01
integral_rad = 0
error_rad = 0
speed_base = 15
target_rad = 85
prev_rad = 1

### SET UP WEBCAM ###

# to the webcam
# using 'videoStream' allows for threading + faster processing 
vs = VideoStream(src=0).start()  
# allow the camera or video file to warm up
time.sleep(2.0)

### MAIN WHILE LOOP ###
while True:
    # grab the current frame
    frame = vs.read()
    frame = imutils.rotate(frame, angle=180)
    frame = cv2.flip(frame, 1, -1) 

    # resize the frame, blur it, and convert it to HSV
    frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None
    
    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
    
        cv2.circle(frame, (int(x), int(y)), int(radius),
            (0, 255, 255), 2)
        cv2.circle(frame, center, 5, (0, 0, 255), -1)
        
        # round radius
        rad = math.floor(radius)
        
        ## PROPORTIONAL CONTROL FOR DISTANCE 
        # find difference so that it only proceeds if new value is 5 more than 
        # previous value 
        diff_rad = abs(rad-prev_rad)
        if diff_rad > 5:
            # implement proportional controller 
            error_rad = target_rad - rad               # error 
            delta_rad = (math.floor(kp_rad*error_rad)) # value to +/- onto motor speeds
            # print robot direction to terminal
            if delta_rad < 0:
                print("backwards!")
            if delta_rad >= 0:
                print("forwards!")
            new_speed = 18 + delta_rad  # base speed for center p controller
            prev_rad = rad
 
        ## PROPORTIONAL CONTROL FOR TURNING (keeping dot in center)
        x_val = int(x)
        diff = abs(x_val-prev_x)
        # only proceed if difference is greater than 15- helps w/ lag
        if diff > 15:
            error = center_x-x_val
            delta = (-1*math.floor(kp*error))
            speed_abs = new_speed
    
            # this is the main line to send to repl!!! 
            ser.write(('motors.pwm(+%d+%d, -%d+%d)\r\n'%(speed_abs,delta,speed_abs,delta)).encode())
         
            prev_x = x_val 
    else:
    # NOTE: THIS LAGS UP THE SPIKE A LOT 
        ser.write(('hub.sound.beep(391,200,2)\r\n').encode())
        if prev_x < center_x:
            # rotate to the right, so CW
            ser.write(('motors.pwm(0,-30)\r\n').encode())
            print("turn right!")
            # if larger than rotate to the left so CCW
        elif prev_x > center_x:
            print("turn left!")
            ser.write(('motors.pwm(30,0)\r\n').encode())
        else:
            print("backwards quickly!")
            ser.write(('motors.pwm(-20,20)\r\n').encode())
            
    # show the frame to our screen
    cv2.imshow("Frame", frame)    
    
 
    key = cv2.waitKey(1) & 0xFF
    
    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break
        # otherwise, release the camera

vs.release()
        
# close all windows
cv2.destroyAllWindows()

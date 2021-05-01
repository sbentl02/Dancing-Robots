#Stephanie Bentley
#4/21/2021

#File on Raspberry Pi to send on/off values to spike from user input

import time
import numpy as np
import serial

#Initialize serial connection
ser = serial.Serial(
  port='/dev/ttyAMA1',
  baudrate = 115200,
  parity=serial.PARITY_NONE,
  stopbits=serial.STOPBITS_ONE,
  bytesize=serial.EIGHTBITS,
  timeout=1
)

input('Press enter to start')

#Run continuously
try:
    while True:
        #Wait for user input 0 (stop) or 1 (start)
        val = input('Start or stop')
        if val == '0' or val == '1':
            #Send value over serial
            ser.write((val).encode())
            #print(val) #Debug print to check state
except KeyboardInterrupt:
    print("Press Ctrl-C to terminate while statement")
    pass


#Stephanie Bentley
#4/21/2021

#File runs on Raspberry Pi to continuously receive data from a microphone, determine
#if music is playing or not based on threshold for standard deviation of data chunks
#and if music has changed send value to SPIKE
#Get threshold by first running audiothresh.py


import pyaudio, array, time
import numpy as np
import serial


#Audio parameters
form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 1 # 1 channel
samp_rate = 44100 # 44.1kHz sampling rate
chunk = 4096*20 # 2^12 samples for buffer
dev_index = 1 # device index found by p.get_device_info_by_index(ii)

#Value to set based on audiothresh.py
thresh = 70

#Initialize audio stream
audio = pyaudio.PyAudio() # create pyaudio instantiation
# create pyaudio stream
stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                input_device_index = dev_index,input = True, \
                frames_per_buffer=chunk)

#Initialize serial connection
ser = serial.Serial(
  port='/dev/ttyAMA1',
  baudrate = 115200,
  parity=serial.PARITY_NONE,
  stopbits=serial.STOPBITS_ONE,
  bytesize=serial.EIGHTBITS,
  timeout=1
)

prev_val = 0
frames = []

#Wait for user input to start
input('Press enter to start')
stream.start_stream()
try:
    while True:
        #print('Trying read') #Debug print to check state
        #Read in data from microphone and get standard deviation
        sds =[]
        raw = stream.read(chunk, exception_on_overflow = False)
        data = array.array('h',raw).tolist()
        sds = np.std(data)

        #print(sds) #Debug print to check state
        music = int(sds > thresh) #Check if music greater than threshold
        #If music boolean has changed, send over serial
        if prev_val != music:
            ser.write((str(music)).encode())
            #print(music) #Debug print to check state
        if music:
            #print('Music is playing') #Debug print to check state
        else:
            #print('No music') #Debug print to check state
        prev_val = music
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Press Ctrl-C to terminate while statement")
    #Keep robot going if possible if there is an error on Raspberry Pi side
    ser.write((str(1)).encode())
    ser.write((str(1)).encode())
    ser.write((str(1)).encode())
    pass
 
#Stop the stream, close it, and terminate the pyaudio instantiation
stream.stop_stream()
stream.close()
audio.terminate()

#Stephanie Bentley
#4/21/2021

#File runs on Raspberry Pi to receive data from a microphone under two conditions 
#and plot metrics of each chunk (standard deviations is best)
#Use to visualize and threshold music on vs music off audio conditions to set threshold value in audio.py

import pyaudio, array, time
import numpy as np
import matplotlib.pyplot as plt

#Initialize audio paramters
form_1 = pyaudio.paInt16 #16-bit resolution
chans = 1 #1 channel
samp_rate = 44100 #44.1kHz sampling rate
chunk = 4096*20 #(2^12)*20 samples for buffer
dev_index = 1 #device index found by p.get_device_info_by_index(ii)
record_secs = 20 #Time to record over for each class

#Initialize audio stream
audio = pyaudio.PyAudio() # create pyaudio instantiation
# # create pyaudio stream
stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                input_device_index = dev_index,input = True, \
                frames_per_buffer=chunk)

frames = [] #Store full chunk
sds=[] #Store standard deviations of chunk
rms=[] #Store rms of chunk
y=[] #Store data class corresponding to data points
tvec=[] #Store time

#Start training
stream.start_stream()
for i in range(2):
    #Wait for user to start class input
    print('Training Data Class %i' % i)
    input('Press enter to record')
    for ii in range(0,int((samp_rate/chunk)*record_secs)):
        #tvec.append(ii / (samp_rate/chunk)) #Use to see data over time
        #Read data in chunk from microphone and add to list
        raw = stream.read(chunk, exception_on_overflow = False)
        data = array.array('h',raw).tolist()
        frames.append(data)

        #Calculate metrics
        rms.append(np.sqrt(np.mean(np.square(data))))
        sds.append(np.std(data))
        y.append(i) #Class value for chunk
    time.sleep(2)

#Stop the stream, close it, and terminate the pyaudio instantiation
stream.stop_stream()
stream.close()
audio.terminate()

#Plot data
#plt.plot(data)
plt.plot(y, sds, 'o') #Best visualization: standard deviation
#plt.plot(y, rms, 'o') #Visualize rms of chunks
#plt.plot(tvec, frames) #Visualize data over time
plt.show()



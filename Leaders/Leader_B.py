#Stephanie Bentley
#This code is run on a SPIKE PRIME leader for the Waltz project
#This code receives on/off status from a raspberry pi over serial, line follows with
#periodic spins, and turns off or on to the line with a red trigger.


#The code line follows on the left side of line with a white line and 
#on the right side for a black line

#Calibrate ONLINE and OFFLINE with light readings, adjust kp, speed, 
#motor values, and counter max as necessary for desired behavior in environment

import hub,utime,math


#Initializes devices
light = hub.port.D.device #color sensor on front center of car
motorB = hub.port.B.motor #Left motor
motorPair = hub.port.A.motor.pair(motorB) #Right motor

pi = hub.port.C #Raspberry pi connected over serial to port
pi.mode(hub.port.MODE_FULL_DUPLEX)
pi.baud(115200)

#Initialize start/stop conditions
go = 1 #if 0 starts line following immediately, if 1 waits until it hits a red trigger to run
music = 0 #if using serial connection, start at 0 so it waits for signal, 
#otherwise 1 to run immediately

#Initialize values for line following
ONLINE = 97
OFFLINE = 11
threshold = (ONLINE + OFFLINE) / 2;

#Set proportional control constant and default speed values
kp = 0.4
speed = 30
error = 0
counter = 0

#Run continuously
while True: 
    #Read value from serial connection and use to set music condition
    reply_bytes = pi.read(1)
    utime.sleep(0.1)
    try:
        if reply_bytes:
            #print('Running') #Debug print to check state
            reply = reply_bytes.decode('utf-8')
            #Only react to 0 or 1 characters received (off or on)
            if reply == '0' or reply == '1':
                music = int(reply)
                #print(music) #Debug print to check received value
            utime.sleep(0.1)
            #print(reply) #Debug print to check received value
    except Exception as e:
        print('Error:')
        print(e)
        continue
    
    #Get reading from light sensor or skip loop if no value read
    lightsens = light.get()
    if lightsens is None:
        utime.sleep(0.005)
        continue  
       
    #Trigger turning on or off line if red detected
    if lightsens[1] == 9: #9 is value for red
        #print('red') #Debug print to check state
        go = not go #Reverse current state
        #print(go) #Debug print to check state

        motorPair.pwm(60, -60) #go straight
        utime.sleep(1)
        motorPair.pwm(20,-60) #turn right
        utime.sleep(0.8)
        motorPair.pwm(60,-60) #go straight again
        utime.sleep(0.8)
        
    #If either stop condition triggered, car stops
    if not music or go:
        #print('Stop') #Debug print to check state
        motorPair.pwm(0,0)
        continue

    #Typical line following behavior
    if counter < 50: #Controls time between spins
        #print('line follow') #Debug print to check state
        counter += 1

        #Read light sensor value and use proportional control to line follow
        lightdiff = lightsens[0]
        error = threshold - lightdiff
        turn = math.floor(kp * error)
        speedA = speed - turn
        speedB = speed + turn
        motorPair.pwm(speedA, -speedB)
        utime.sleep(0.1)
    
    #Periodic spin
    else:
        #print('spin') #Debug print to check state
        motorPair.pwm(50, -30)
        utime.sleep(14)
        #print('done with spin') #Debug print to check state
        counter = 0

#Stop motors when done
motorPair.pwm(0,0)


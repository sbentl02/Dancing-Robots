#ME_35 Leader A Code 2021
# Allison Moore
#
#This code uses line following to allow a LEGO SPIKE "leader" robot to track a line with
# proportional control and color sensing while making periodic spins
#
# Alongside this, the "leader" communicates with a Raspberry Pi 4 to start and stop to the sound of music 
# When the color sensor detects "Red" for this code, this robot will turn switch with Leader B



import hub,utime,math
#Initializes sensors
light = hub.port.F.device #color sensor in center of car
pi = hub.port.C
pi.mode(hub.port.MODE_FULL_DUPLEX)
pi.baud(115200)
music = 0 #0 starts off, 1 for no music
#us = hub.port.F.device #ultrasonic sensor on front of car
#greenSense = hub.port.E.device #color sensor in front right and centered on line
hub.port.A.motor.mode(1)
hub.port.B.motor.mode(1)
motorB = hub.port.B.motor
motorPair = hub.port.A.motor.pair(motorB)

# #color values(index 0) for black and white
ONLINE = 60
OFFLINE = 6

#red setting 
go = 0

threshold = (ONLINE + OFFLINE)/2
#setPoint = 10 #distance of obstacle in front for car to stop (in cm)
#set proportional control constant and default speed values
kp = 0.8
speed = 30
error = 0
counter = 0

#Line Following 
second_bot = True

while True:
    #get reading from main color sensor and ultrasonic
    #distance = us.get()[0]
    reply_bytes = pi.read(20)
    print(reply_bytes)
    utime.sleep(0.1)
    try:
        if reply_bytes:
            print('Running')
            reply = reply_bytes.decode('utf-8')
            print(reply)
            if reply == '0' or reply == '1':
                music = int(reply)
                #print(music)x
            utime.sleep(0.1)
            print(reply)
    except Exception as e:
        print('Error:')
        print(e)
        continue
        
    light_col = light.get()
    if light_col is  None:
        utime.sleep(0.005)
        continue
    
    if light_col[1] == 9:
        print("sensed")
        go = not go
        motorPair.pwm(60,-60)
        utime.sleep(.6)
        motorPair.pwm(80,-30)
        utime.sleep(.7)
        motorPair.pwm(40,-40)
        utime.sleep(1.5)
        continue
        
    if not music or go:
        motorPair.pwm(0,0)
        continue
    if counter < 150:
        counter += 1
        lightdiff = light.get()[0]
        print('line follow')
        #avoid sensor error
        if lightdiff is None:
            utime.sleep(0.005)
            continue
        #if distance is not None and distance < 10:
        #motorPair.pwm(0,0) #Pause if obstacle closer than 10cm
        else:
            error = threshold - lightdiff
            #print(error)
            turn = math.floor(kp * error)
            speedA = speed - turn
            speedB = speed + turn
            motorPair.pwm(speedA, -speedB)
            utime.sleep(0.1)
        if counter % 11 == 0:
            print("line follow")
            print(counter)
    else:
        counter = 0
        print('Spin ENTER')
        first = light.get()[0]
        while first > 40 or counter < 3:
            motorPair.run_for_time(500, 35, -20)
            first = light.get()[0]
            utime.sleep(.3) 
            counter = counter +1
        second = light.get()[0]   
        while second < 11:
            motorPair.run_for_time(300, 30, -20)
            second = light.get()[0]
            utime.sleep(.13)
        print('done with spin')
        utime.sleep(.2)
motorPair.pwm(0,0)

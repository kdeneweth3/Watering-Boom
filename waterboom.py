## SETUP:
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(35, GPIO.OUT) ## motorA FWD
GPIO.setup(33, GPIO.OUT) ## motorB REV
GPIO.setup(12, GPIO.OUT) ## LED_red motor fwd (green) or rev (red)
GPIO.setup(10, GPIO.OUT) ## LED_green motor fwd (green) or rev (red)
GPIO.setup(8, GPIO.OUT) ## LED_blue motor fwd (green) or rev (red)
GPIO.setup(37, GPIO.OUT) ## LED valve 1 FWD
GPIO.setup(38, GPIO.OUT) ## LED valve 2 REV
GPIO.setup(13, GPIO.IN) ## fwd magnet sensor
GPIO.setup(15, GPIO.IN) ## rev magnet sensor
GPIO.setup(11, GPIO.IN) ## home magnet sensor
GPIO.setup(40, GPIO.IN) ## end magnet sensor
GPIO.setup(16, GPIO.IN) ## start button

pwmA = GPIO.PWM(35, 500) ##fwd motor pin
pwmB = GPIO.PWM(33, 500) ##rev motor pin
pwmA.start(0) ##duty cycle value is 0-100
pwmB.start(0) ##duty cycle value is 0-100



## GENERAL SETTINGS:
class MagSetting(object):
    """Stands for boom settings.
    Attributes: speed (1-10; or 15), cropname."""

magnetfwd = MagSetting ()
magnetrev = MagSetting ()
magnet1 = MagSetting ()
magnet2 = MagSetting ()
magnet11 = MagSetting ()
magnet12 = MagSetting ()


## INPUT FROM USER:
def speedSettings():
    magnetfwd.speed = input("Forward speed: ")
    magnetrev.speed = input("Reverse speed: ")
    magnet1.speed = input("Magnet 1 speed: ")
    magnet2.speed = input("Magnet 2 speed: ")
    magnet11.speed = input("Magnet 3 speed: ")
    magnet12.speed = input("Magnet 4 speed: ")

def cropnameSettings():
    magnetfwd.cropname = input("Forward crop: ")
    magnetrev.cropname = input("Reverse crop: ")
    magnet1.cropname = input("Magnet 1 crop: ")
    magnet2.cropname = input("Magnet 2 crop: ")
    magnet11.cropname = input("Magnet 3 crop: ")
    magnet12.cropname = input("Magnet 4 crop: ")

def passSettings():
    global passSet
    passSet = int(input("# of passes: "))
    
def userSettings():
    passSettings()
    speedSettings()

magnetDict = {0:magnetfwd, 1:magnet1, 2:magnet2, 10:magnetrev, 11:magnet11, 12:magnet12}


## MAGNET SENSORS:
def mag_increment():
    global endmag
    global homemag
    global boom_dir
    global mag_num
    global passes
    global transID
    global passSet
    if fwd_magnet_sensor == False and boom_dir == 1: ## 1 equals fwd main mag sensor increments
        mag_num = mag_num + 1
    if rev_magnet_sensor == False and boom_dir == 0: ## 0 = rev
        mag_num = mag_num + 1
    if home_magnet_sensor == False:  ## home mag sensor: when the home magnet is passed it increments
        homemag = homemag + 1
        if homemag == 1:
            passes = passes + 1
            if passes > passSet:
                pass
            else:
                transID = 0
                mag_num = 0
                homemag = 0
    if end_magnet_sensor == False:  ## end mag sensor: when the end magnet is passed it increments
        endmag = endmag + 1
        if endmag == 1:
            transID = 0
            mag_num = 10
            endmag = 0    


## SPEED FUNCTIONS:
def speed0():
    pwmA.ChangeDutyCycle(0)
    pwmB.ChangeDutyCycle(0)
def speed5():
    if boom_dir == 1:
        pwmA.ChangeDutyCycle(50)
        pwmB.ChangeDutyCycle(0)
    elif boom_dir == 0:
        pwmA.ChangeDutyCycle(0)
        pwmB.ChangeDutyCycle(50)
def speed10():
    if boom_dir == 1:
        pwmA.ChangeDutyCycle(100)
        pwmB.ChangeDutyCycle(0)
    elif boom_dir == 0:
        pwmA.ChangeDutyCycle(0)
        pwmB.ChangeDutyCycle(100)
        
speedsDict = {'0':speed0, '5':speed5, '10':speed10, '15':speed10}


## BOOM DIRECTION LED (for prototype only):
def dir_led():
    if boom_dir == 1:
        GPIO.output(12, False) ## Red pin: LED green for fwd
        GPIO.output(10, True) ## Green
        GPIO.output(8, False) ## Blue
    elif boom_dir == 0:
        GPIO.output(12, True) ## Red pin: LED red for rev
        GPIO.output(10, False) ## Green
        GPIO.output(8, False) ## Blue
    elif boom_dir == 2:
        GPIO.output(12, False) ## Red pin: LED red for rev
        GPIO.output(10, False) ## Green
        GPIO.output(8, False) ## Blue


## BOOM RUN:
def fwdBoom():
    global boom_dir
    boom_dir = 1                    ## gives direction to boom, 1=fwd
    i = magnetDict[mag_num].speed   ##depending on the magnet number, finds the user input speed
    j = int(magnetDict[mag_num].speed)
    speedsDict[i]()                 ## uses the input speed to call the proper speed function
    if j < 15:                      ## if input speed is less than 15 turns the appropriate boom on
        GPIO.output(37, True)     ## LED for Valve 1 on
        GPIO.output(38, False)    ## LED for Valve 2 off
    else:                           ## if speed = 15 turns both valves off, boom still moves forward
        GPIO.output(37, False)   ## LED for Valve 1 off
        GPIO.output(38, False)   ## LED for Valve 2 off

def revBoom():
    global boom_dir
    boom_dir = 0         ## 0 = rev
    i = magnetDict[mag_num].speed
    j = int(magnetDict[mag_num].speed)
    speedsDict[i]()
    if j < 15:
        GPIO.output(37, False)  ## LED for Valve 1 off
        GPIO.output(38, True)   ## LED for Valve 2 on
    else:
        GPIO.output(37, False)  ## LED for Valve 1 off
        GPIO.output(38, False)  ## LED for Valve 2 off

def boom_trans():
    global transID
    global boom_dir
    boom_dir = 2
    speed0()
    GPIO.output(37, False)   ## LED for Valve 1 off
    GPIO.output(38, False)   ## LED for Valve 2 off
    transID = transID + 1
    dir_led()
    time.sleep(3)

def runFwdRev():
    global mag_num
    global transID
    if mag_num < 10 and mag_num > 0:   ##assuming always starting from home position 
        fwdBoom()
    elif mag_num == 10:  ## transition to stop the boom and shut both valves off
        if transID == 0:
            boom_trans()
            revBoom()
        else:
            revBoom() 
    elif mag_num > 10:
        revBoom()
    elif mag_num == 0:
        if transID == 0:
            boom_trans()
            fwdBoom()
        else:
            fwdBoom()

def runBoom():
    mag_increment()
    runFwdRev()
    dir_led()
    for x in sensorDict:
        if x == False and passes <= passSet:
            time.sleep(5)

def mag_Reset():
    global passes
    global mag_num
    global homemag
    global endmag
    passes = 1 
    mag_num = 0 
    homemag = 0  
    endmag = 0
    transID = 0

def stopBoom():
    speed0()
    GPIO.output(37, False)   ## LED for Valve 1 off
    GPIO.output(38, False)   ## LED for Valve 2 off
    GPIO.output(12, False) ## Red pin: LED red for rev
    GPIO.output(10, False) ## Green
    GPIO.output(8, False) ## Blue

## clear leds before start
passes = 1 
mag_num = 0 
homemag = 0  
endmag = 0
transID = 0

GPIO.output(37, False)  ## LED for Valve 1 off
GPIO.output(38, False)   ## LED for Valve 2 off
GPIO.output(12, False) ## Red pin: LED green for fwd
GPIO.output(10, False) ## Green
GPIO.output(8, False) ## Blue



## BOOM START:

mag_Reset() ## resets the magnets variables
#boom_trans() ##stops the boom and shuts the valves off
userSettings() ## calls for user input

try:
    while True:
        start_button = GPIO.input(16)
        if start_button == False:
            while passes <= passSet:
                fwd_magnet_sensor = GPIO.input(13)
                rev_magnet_sensor = GPIO.input(15)
                home_magnet_sensor = GPIO.input(11)
                end_magnet_sensor = GPIO.input(40)
                sensorDict = [fwd_magnet_sensor, rev_magnet_sensor, home_magnet_sensor, end_magnet_sensor]
                runBoom()
            stopBoom()
except KeyboardInterrupt:
    GPIO.cleanup()



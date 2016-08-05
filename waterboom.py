## SETUP:
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(29, GPIO.OUT) ## motorA FWD
GPIO.setup(31, GPIO.OUT) ## motorB REV
GPIO.setup(33, GPIO.OUT) ## motorEnable
GPIO.setup(8, GPIO.OUT) ## LED_red motor fwd (green) or rev (red)
GPIO.setup(10, GPIO.OUT) ## LED_green motor fwd (green) or rev (red)
GPIO.setup(12, GPIO.OUT) ## LED_blue motor fwd (green) or rev (red)
GPIO.setup(38, GPIO.OUT) ## LED valve 1 FWD
GPIO.setup(37, GPIO.OUT) ## LED valve 2 REV
#GPIO.setup(pin, GPIO.IN) ## fwd magnet sensor
#GPIO.setup(pin, GPIO.IN) ## rev magnet sensor
#GPIO.setup(pin, GPIO.IN) ## home magnet sensor
#GPIO.setup(pin, GPIO.IN) ## end magnet sensor
GPIO.setup(3, GPIO.IN, pull_up_down = GPIO.PUD_UP) ## start button

pwmA = GPIO.PWM(29, 500) ##fwd motor pin
pwmB = GPIO.PWM(31, 500) ##rev motor pin
pwmA.start(0) ##duty cycle value is 0-100
pwmB.start(0) ##duty cycle value is 0-100

#fwd_magnet_sensor = GPIO.input(pin)
#rev_magnet_sensor = GPIO.input(pin)
#home_magnet_sensor = GPIO.input(pin)
#end_magnet_sensor = GPIO.input(pin)


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

while True:

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
        passSet = int(input("# of passes: "))
    
    def userSettings():
        passSettings()
        speedSettings()

    magnetDict = {0:magnetfwd, 1:magnet1, 2:magnet2, 10:magnetrev, 11:magnet11, 12:magnet12}


    ## MAGNET SENSORS:
    def mag_increment():
        if fwd_magnet_sensor == False and boom_dir == 1: ## 1 equals fwd main mag sensor increments
            mag_num = mag_num + 1
        if rev_magnet_sensor == False and boom_dir == 0: ## 0 = rev
            mag_num = mag_num + 1
        if home_magnet_sensor == False:  ## home mag sensor: when the home magnet is passed it increments
            homemag = homemag + 1
        if end_magnet_sensor == False:  ## end mag sensor: when the end magnet is passed it increments
            endmag = endmag + 1
        if endmag == 1:
            mag_num = 10
            endmag = 0
        if homemag == 1:
            mag_num = 0
            homemag = 0
            passes = passes +1


    ## SPEED FUNCTIONS:
    def speed0():
        pwmA.ChangeDutyCycle(0)
        pwmB.ChangeDutyCycle(0)
        GPIO.output(33, False) ## Controls the enable pin
    def speed1():
        GPIO.output(33, True) ## Controls the enable pin  
        if boom_dir == 1:
            pwmA.ChangeDutyCycle(10)
            pwmB.ChangeDutyCycle(0)
        elif boom_dir == 0:
            pwmA.ChangeDutyCycle(0)
            pwmB.ChangeDutyCycle(10)
    def speed10():
        GPIO.output(33, True) ## Controls the enable pin  
        if boom_dir == 1:
            pwmA.ChangeDutyCycle(100)
            pwmB.ChangeDutyCycle(0)
        elif boom_dir == 0:
            pwmA.ChangeDutyCycle(0)
            pwmB.ChangeDutyCycle(100)
        
    speedsDict = {'0':speed0, '1':speed1, '10':speed10, '15':speed10}


    ## BOOM DIRECTION LED (for prototype only):
    def dir_led():
        if boom_dir == 1:
            GPIO.output(8, False) ## Red pin: LED green for fwd
            GPIO.output(10, True) ## Green
            GPIO.output(12, False) ## Blue
        elif boom_dir == 0:
            GPIO.output(8, True) ## Red pin: LED red for rev
            GPIO.output(10, False) ## Green
            GPIO.output(12, False) ## Blue


    ## BOOM RUN:
    def fwdBoom():
        boom_dir = 1                    ## gives direction to boom, 1=fwd
        i = magnetDict[mag_num].speed   ##depending on the magnet number, finds the user input speed
        speedsDict[i]()                 ## uses the input speed to call the proper speed function
        if i < 15:                      ## if input speed is less than 15 turns the appropriate boom on
            GPIO.output(38, True)     ## LED for Valve 1 on
            GPIO.output(37, False)    ## LED for Valve 2 off
        else:                           ## if speed = 15 turns both valves off, boom still moves forward
            GPIO.output(38, False)   ## LED for Valve 1 off
            GPIO.output(37, False)   ## LED for Valve 2 off

    def revBoom():
        boom_dir = 0         ## 0 = rev
        i = magnetDict[mag_num].speed
        speedsDict[i]()
        if i < 15:
            GPIO.output(38, False)  ## LED for Valve 1 off
            GPIO.output(37, True)   ## LED for Valve 2 on
        else:
            GPIO.output(38, False)  ## LED for Valve 1 off
            GPIO.output(37, False)  ## LED for Valve 2 off

    def boom_trans():
        speed0()
        GPIO.output(38, False)   ## LED for Valve 1 off
        GPIO.output(37, False)   ## LED for Valve 2 off
        time.sleep(5)

    def runFwdRev():
        if mag_num < 10 and mag_num > 0:   ##assuming always starting from home position 
            fwdBoom()
        elif mag_num == 10:  ## transition to stop the boom and shut both valves off
            boom_trans()
            revBoom() 
        elif mag_num > 10:
            revBoom()
        elif mag_num == 0:
            boom_trans()
            fwdBoom()

    def runBoom():
        runFwdRev()
        #mag_increment()
        dir_led()

    def mag_Reset():
        passes = 1 
        mag_num = 0 
        homemag = 0  
        endmag = 0


    ## BOOM START:

    mag_Reset() ## resets the magnets variables
    boom_trans() ##stops the boom and shuts the valves off
    userSettings() ## calls for user input

    start_button = GPIO.input(3)

    GPIO.wait_for_edge(3, GPIO.FALLING)
    
    while passes <= passSet:
        runBoom()

    GPIO.cleanup()


## SETUP:
import RPi.GPIO as GPIO
import time
from tkinter import *

#def boomSetup():
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



## MAGNET SENSORS:
def mag_increment():
    global endmag
    global homemag
    global boom_dir
    global mag_num
    global passes
    global transID
    global passSet
    fwd_magnet_sensor = GPIO.input(13)
    rev_magnet_sensor = GPIO.input(15)
    home_magnet_sensor = GPIO.input(11)
    end_magnet_sensor = GPIO.input(40)
    sensorDict = [fwd_magnet_sensor, rev_magnet_sensor, home_magnet_sensor, end_magnet_sensor]
    if fwd_magnet_sensor == False and boom_dir == 1: ## 1 equals fwd main mag sensor increments
        mag_num = mag_num + 1
    if rev_magnet_sensor == False and boom_dir == 0: ## 0 = rev
        mag_num = mag_num + 1
    if home_magnet_sensor == False:  ## home mag sensor: when the home magnet is passed it increments
        homemag = homemag + 1
        if homemag == 1:
            passes = passes + 1
            if passes > passSet.get():
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
        
speedsDict = {0:speed0, 5:speed5, 10:speed10, 15:speed10}


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
    i = speedSetDict[mag_num].get()   ##depending on the magnet number, finds the user input speed
    speedsDict[i]()                 ## uses the input speed to call the proper speed function
    if i < 15:                      ## if input speed is less than 15 turns the appropriate boom on
        GPIO.output(37, True)     ## LED for Valve 1 on
        GPIO.output(38, False)    ## LED for Valve 2 off
    else:                           ## if speed = 15 turns both valves off, boom still moves forward
        GPIO.output(37, False)   ## LED for Valve 1 off
        GPIO.output(38, False)   ## LED for Valve 2 off

def revBoom():
    global boom_dir
    boom_dir = 0         ## 0 = rev
    i = speedSetDict[mag_num].get()
    speedsDict[i]()
    if i < 15:
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
    fwd_magnet_sensor = GPIO.input(13)
    rev_magnet_sensor = GPIO.input(15)
    home_magnet_sensor = GPIO.input(11)
    end_magnet_sensor = GPIO.input(40)
    sensorDict = [fwd_magnet_sensor, rev_magnet_sensor, home_magnet_sensor, end_magnet_sensor]
    mag_increment()
    runFwdRev()
    dir_led()
    for x in sensorDict:
        if x == False and passes <= passSet.get():
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


def startLoop():
#    boomSetup()
    mag_Reset() ## resets the magnets variables
    try:
        while passes <= passSet.get():
            runBoom()
        stopBoom()
        mag_Reset()
    except KeyboardInterrupt:
        GPIO.cleanup()
    GPIO.cleanup()



## GUI ------------------------------------------

window = Tk()

window.title("Boom Settings")

## Setup pass label and entry box
passlbl = Label(window, text="Passes:")
passlbl.grid(row=0, column=0, pady=10)

passSet = IntVar()
passEntry = Entry(textvariable=passSet, relief=SUNKEN, width=10)
passEntry.grid(row = 0, column = 1)

## Setup crop and speed title labels
Label(window, text="Crop").grid(row=1, column = 0)
Label(window, text="Speed").grid(row=1, column = 1)
Label(window, text="Crop").grid(row=1, column = 5)
Label(window, text="Speed").grid(row=1, column = 4)


## Setup speed settings entry boxes
speedSet0 = IntVar()
speedSet1 = IntVar()
speedSet2 = IntVar()
speedSet3 = IntVar()
speedSet4 = IntVar()
speedSet5 = IntVar()
speedSet6 = IntVar()
speedSet7 = IntVar()
speedSet8 = IntVar()
speedSet9 = IntVar()
speedSet10 = IntVar()
speedSet11 = IntVar()
speedSet12 = IntVar()
speedSet13 = IntVar()
speedSet14 = IntVar()
speedSet15 = IntVar()
speedSet16 = IntVar()
speedSet17 = IntVar()
speedSet18 = IntVar()
speedSet19 = IntVar()

speedSetDict = {0:speedSet0, 1:speedSet1, 2:speedSet2, 3:speedSet3, 4:speedSet4,
                5:speedSet5, 6:speedSet6, 7:speedSet7, 8:speedSet8, 9:speedSet9,
                10:speedSet10, 11:speedSet11, 12:speedSet12, 13:speedSet13, 14:speedSet14,
                15:speedSet15, 16:speedSet16, 17:speedSet17, 18:speedSet18, 19:speedSet19}

speedEntry0 = Entry(textvariable = speedSet0, relief=SUNKEN, width=10)
speedEntry0.grid(row=2, column=4, padx=4)
speedEntry1 = Entry(textvariable = speedSet1, relief=SUNKEN, width=10)
speedEntry1.grid(row=3, column=4, padx=4)
speedEntry2 = Entry(textvariable = speedSet2, relief=SUNKEN, width=10)
speedEntry2.grid(row=4, column=4, padx=4)
speedEntry3 = Entry(textvariable = speedSet3, relief=SUNKEN, width=10)
speedEntry3.grid(row=5, column=4, padx=4)
speedEntry4 = Entry(textvariable = speedSet4, relief=SUNKEN, width=10)
speedEntry4.grid(row=6, column=4, padx=4)
speedEntry5 = Entry(textvariable = speedSet5, relief=SUNKEN, width=10)
speedEntry5.grid(row=7, column=4, padx=4)
speedEntry6 = Entry(textvariable = speedSet6, relief=SUNKEN, width=10)
speedEntry6.grid(row=8, column=4, padx=4)
speedEntry7 = Entry(textvariable = speedSet7, relief=SUNKEN, width=10)
speedEntry7.grid(row=9, column=4, padx=4)
speedEntry8 = Entry(textvariable = speedSet8, relief=SUNKEN, width=10)
speedEntry8.grid(row=10, column=4, padx=4)
speedEntry9 = Entry(textvariable = speedSet9, relief=SUNKEN, width=10)
speedEntry9.grid(row=11, column=4, padx=4)
speedEntry10 = Entry(textvariable = speedSet10, relief=SUNKEN, width=10)
speedEntry10.grid(row=11, column=1, padx=4)
speedEntry11 = Entry(textvariable = speedSet11, relief=SUNKEN, width=10)
speedEntry11.grid(row=10, column=1, padx=4)
speedEntry12 = Entry(textvariable = speedSet12, relief=SUNKEN, width=10)
speedEntry12.grid(row=9, column=1, padx=4)
speedEntry13 = Entry(textvariable = speedSet13, relief=SUNKEN, width=10)
speedEntry13.grid(row=8, column=1, padx=4)
speedEntry14 = Entry(textvariable = speedSet14, relief=SUNKEN, width=10)
speedEntry14.grid(row=7, column=1, padx=4)
speedEntry15 = Entry(textvariable = speedSet15, relief=SUNKEN, width=10)
speedEntry15.grid(row=6, column=1, padx=4)
speedEntry16 = Entry(textvariable = speedSet16, relief=SUNKEN, width=10)
speedEntry16.grid(row=5, column=1, padx=4)
speedEntry17 = Entry(textvariable = speedSet17, relief=SUNKEN, width=10)
speedEntry17.grid(row=4, column=1, padx=4)
speedEntry18 = Entry(textvariable = speedSet18, relief=SUNKEN, width=10)
speedEntry18.grid(row=3, column=1, padx=4)
speedEntry19 = Entry(textvariable = speedSet19, relief=SUNKEN, width=10)
speedEntry19.grid(row=2, column=1, padx=4)


## Setup fwd labels and crop name entry

row=2

fwd_lbls = (["Fwd", "Fwd 1", "Fwd 2", "Fwd 3",
               "Fwd 4", "Fwd 5", "Fwd 6", "Fwd 7",
               "Fwd 8", "Fwd 9"])

f_entry = dict()

for f in fwd_lbls:
    fwd = Label(window, text=f, relief = RIDGE, width=10)
    fwd.grid(row=row, column=3)
    Entry(window, relief=SUNKEN, width = 10).grid(row=row, column=5, padx=4)
    row=row+1
    if row == len(fwd_lbls)+2:
        row=2

## Setup rev labels and crop name entry

rev_lbls = (["Rev 9", "Rev 8", "Rev 7", "Rev 6",
             "Rev 5", "Rev 4", "Rev 3", "Rev 2",
             "Rev 1", "Rev"])

r_entry = dict()

for r in rev_lbls:
    Entry(window, relief=SUNKEN, width = 10).grid(row=row, column=0, padx=4)
    rev = Label(window, text=r, relief = RIDGE, width=10)
    rev.grid(row=row, column=2)
    row=row+1
    if row == len(rev_lbls)+2:
        row=2

def startLoopPractice():
    for n in range(0, 20):
        print("speedSet: %s" % (speedSetDict[n].get()))


## Start button
Button(window, text='Start', command=
       startLoop).grid(row=13,column=1, pady=4)


window.mainloop()






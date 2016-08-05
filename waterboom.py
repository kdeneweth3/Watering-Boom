### SETUP:
import RPi.GPIO as GPIO
import time
import Tkinter as tk

# Setup
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


### Functions
def run_speed(speed, direction):
    speedsDict = speedsDict = {0:0,3:3, 5:50, 10:100, 15:100}
    if direction == 'fwd':
        pwmA.ChangeDutyCycle(speedsDict[speed])
        pwmB.ChangeDutyCycle(0)
    elif direction == 'rev':
        pwmA.ChangeDutyCycle(0)
        pwmB.ChangeDutyCycle(speedsDict[speed])
    elif direction == 'none':
        pwmA.ChangeDutyCycle(0)
        pwmB.ChangeDutyCycle(0)        


def valve_position(valve1, valve2):
    GPIO.output(37, valve1)     ## True = on
    GPIO.output(38, valve2)     ## False = off


def transition():
    speed = 0
    direction = 'none'
    run_speed(speed, direction)
    valve1 = False
    valve2 = False
    valve_position(valve1, valve2)
    time.sleep(3)
    return valve1, valve2


def speed_fnc(mag_num):
    speed = speedSetDict[mag_num].get()
    if speed == 15:
        valve = False
    else:
        valve = True
    return speed, valve



### MAIN LOOP
def mainLoop(): 
    
    # define all starting variables
    mag_num = 0
    passes = 1
    direction = 'fwd'
    valve1 = False
    valve2 = False

    GPIO.output(37, False)  ## LED for Valve 1 off
    GPIO.output(38, False)   ## LED for Valve 2 off
    GPIO.output(12, False) ## Red pin: LED green for fwd
    GPIO.output(10, False) ## Green
    GPIO.output(8, False) ## Blue

    # run boom fwd speed
    speed, valve1 = speed_fnc(mag_num)
    run_speed(speed, direction)
    valve_position(valve1, valve2)
    
    try:
        while passes <= passSet.get():
            # watch for magnets

            fwd_magnet_sensor = GPIO.input(13)
            rev_magnet_sensor = GPIO.input(15)
            home_magnet_sensor = GPIO.input(11)
            end_magnet_sensor = GPIO.input(40)
            
            if fwd_magnet_sensor == False and direction == 'fwd':
                mag_num = mag_num + 1
                speed, valve1 = speed_fnc(mag_num)
                run_speed(speed, direction)
                valve_position(valve1, valve2)
                time.sleep(4)  ## sleep 4 seconds to prevent reading magnet multiple times
            elif rev_magnet_sensor == False and direction == 'rev':
                mag_num = mag_num + 1
                speed, valve2 = speed_fnc(mag_num)
                run_speed(speed, direction)
                valve_position(valve1, valve2)
                time.sleep(4)
            elif end_magnet_sensor == False:
                valve1, valve2 = transition()
                mag_num = 10 # rev crop
                direction = 'rev'
                speed, valve2 = speed_fnc(mag_num)
                run_speed(speed, direction)
                valve_position(valve1, valve2)
                time.sleep(4)
            elif home_magnet_sensor == False:
                valve1, valve2 = transition()
                passes = passes + 1
                if passes > passSet.get():
                    continue
                mag_num = 0
                direction = 'fwd'
                speed, valve1 = speed_fnc(mag_num)
                run_speed(speed, direction)
                valve_position(valve1, valve2)
                time.sleep(4)
            
            # actions happen here
            #run_speed(speed, direction)
            #valve_position(valve1, valve2)
            

    except KeyboardInterrupt:
        GPIO.cleanup()



### GUI ------------------------------------------

window = tk.Tk()

window.title("Boom Settings")

## Setup pass label and entry box
passlbl = tk.Label(window, text="Passes:")
passlbl.grid(row=0, column=0, pady=10)

passSet = tk.IntVar()
passEntry = tk.Entry(textvariable=passSet, relief=tk.SUNKEN, width=10)
passEntry.grid(row = 0, column = 1)

## Setup crop and speed title labels
tk.Label(window, text="Crop").grid(row=1, column = 0)
tk.Label(window, text="Speed").grid(row=1, column = 1)
tk.Label(window, text="Crop").grid(row=1, column = 5)
tk.Label(window, text="Speed").grid(row=1, column = 4)


## Setup speed settings entry boxes
speedSet0 = tk.IntVar()
speedSet1 = tk.IntVar()
speedSet2 = tk.IntVar()
speedSet3 = tk.IntVar()
speedSet4 = tk.IntVar()
speedSet5 = tk.IntVar()
speedSet6 = tk.IntVar()
speedSet7 = tk.IntVar()
speedSet8 = tk.IntVar()
speedSet9 = tk.IntVar()
speedSet10 = tk.IntVar()
speedSet11 = tk.IntVar()
speedSet12 = tk.IntVar()
speedSet13 = tk.IntVar()
speedSet14 = tk.IntVar()
speedSet15 = tk.IntVar()
speedSet16 = tk.IntVar()
speedSet17 = tk.IntVar()
speedSet18 = tk.IntVar()
speedSet19 = tk.IntVar()

speedSetDict = {0:speedSet0, 1:speedSet1, 2:speedSet2, 3:speedSet3, 4:speedSet4,
                5:speedSet5, 6:speedSet6, 7:speedSet7, 8:speedSet8, 9:speedSet9,
                10:speedSet10, 11:speedSet11, 12:speedSet12, 13:speedSet13, 14:speedSet14,
                15:speedSet15, 16:speedSet16, 17:speedSet17, 18:speedSet18, 19:speedSet19}

speedEntry0 = tk.Entry(textvariable = speedSet0, relief=tk.SUNKEN, width=10)
speedEntry0.grid(row=2, column=4, padx=4)
speedEntry1 = tk.Entry(textvariable = speedSet1, relief=tk.SUNKEN, width=10)
speedEntry1.grid(row=3, column=4, padx=4)
speedEntry2 = tk.Entry(textvariable = speedSet2, relief=tk.SUNKEN, width=10)
speedEntry2.grid(row=4, column=4, padx=4)
speedEntry3 = tk.Entry(textvariable = speedSet3, relief=tk.SUNKEN, width=10)
speedEntry3.grid(row=5, column=4, padx=4)
speedEntry4 = tk.Entry(textvariable = speedSet4, relief=tk.SUNKEN, width=10)
speedEntry4.grid(row=6, column=4, padx=4)
speedEntry5 = tk.Entry(textvariable = speedSet5, relief=tk.SUNKEN, width=10)
speedEntry5.grid(row=7, column=4, padx=4)
speedEntry6 = tk.Entry(textvariable = speedSet6, relief=tk.SUNKEN, width=10)
speedEntry6.grid(row=8, column=4, padx=4)
speedEntry7 = tk.Entry(textvariable = speedSet7, relief=tk.SUNKEN, width=10)
speedEntry7.grid(row=9, column=4, padx=4)
speedEntry8 = tk.Entry(textvariable = speedSet8, relief=tk.SUNKEN, width=10)
speedEntry8.grid(row=10, column=4, padx=4)
speedEntry9 = tk.Entry(textvariable = speedSet9, relief=tk.SUNKEN, width=10)
speedEntry9.grid(row=11, column=4, padx=4)
speedEntry10 = tk.Entry(textvariable = speedSet10, relief=tk.SUNKEN, width=10)
speedEntry10.grid(row=11, column=1, padx=4)
speedEntry11 = tk.Entry(textvariable = speedSet11, relief=tk.SUNKEN, width=10)
speedEntry11.grid(row=10, column=1, padx=4)
speedEntry12 = tk.Entry(textvariable = speedSet12, relief=tk.SUNKEN, width=10)
speedEntry12.grid(row=9, column=1, padx=4)
speedEntry13 = tk.Entry(textvariable = speedSet13, relief=tk.SUNKEN, width=10)
speedEntry13.grid(row=8, column=1, padx=4)
speedEntry14 = tk.Entry(textvariable = speedSet14, relief=tk.SUNKEN, width=10)
speedEntry14.grid(row=7, column=1, padx=4)
speedEntry15 = tk.Entry(textvariable = speedSet15, relief=tk.SUNKEN, width=10)
speedEntry15.grid(row=6, column=1, padx=4)
speedEntry16 = tk.Entry(textvariable = speedSet16, relief=tk.SUNKEN, width=10)
speedEntry16.grid(row=5, column=1, padx=4)
speedEntry17 = tk.Entry(textvariable = speedSet17, relief=tk.SUNKEN, width=10)
speedEntry17.grid(row=4, column=1, padx=4)
speedEntry18 = tk.Entry(textvariable = speedSet18, relief=tk.SUNKEN, width=10)
speedEntry18.grid(row=3, column=1, padx=4)
speedEntry19 = tk.Entry(textvariable = speedSet19, relief=tk.SUNKEN, width=10)
speedEntry19.grid(row=2, column=1, padx=4)


## Setup fwd labels and crop name entry

row=2

fwd_lbls = (["Fwd", "Fwd 1", "Fwd 2", "Fwd 3",
               "Fwd 4", "Fwd 5", "Fwd 6", "Fwd 7",
               "Fwd 8", "Fwd 9"])

f_entry = dict()

for f in fwd_lbls:
    fwd = tk.Label(window, text=f, relief = tk.RIDGE, width=10)
    fwd.grid(row=row, column=3)
    tk.Entry(window, relief=tk.SUNKEN, width = 10).grid(row=row, column=5, padx=4)
    row=row+1
    if row == len(fwd_lbls)+2:
        row=2

## Setup rev labels and crop name entry

rev_lbls = (["Rev 9", "Rev 8", "Rev 7", "Rev 6",
             "Rev 5", "Rev 4", "Rev 3", "Rev 2",
             "Rev 1", "Rev"])

r_entry = dict()

for r in rev_lbls:
    tk.Entry(window, relief=tk.SUNKEN, width = 10).grid(row=row, column=0, padx=4)
    rev = tk.Label(window, text=r, relief = tk.RIDGE, width=10)
    rev.grid(row=row, column=2)
    row=row+1
    if row == len(rev_lbls)+2:
        row=2

def startLoopPractice():
    for n in range(0, 20):
        print("speedSet: %s" % (speedSetDict[n].get()))


## Start button
tk.Button(window, text='Start', command=
       mainLoop).grid(row=13,column=1, pady=4)


window.mainloop()

GPIO.cleanup()






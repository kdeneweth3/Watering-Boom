# Watering Boom README

The "Pi Boom," as I called it, was a project that had a total savings of about 83% versus commercial products on the market. The Pi Boom was meant to reduce cost while increasing functionality and efficiency. It was faster to program crop watering speeds compared to other options on the market due to it's simple graphical interface. It was also an IoT device that could be programmed and run from a smart phone or computer on the same network. This is a video demonstration of my "Pi Boom"... https://youtu.be/3wBGWbtR-vk

Pi Boom code is the waterboom.py file.

This is a video of what a fully functioning watering boom does and what I was trying to improve. The one in the video moves based on programmed distances, mine adjusts speeds based on where magnets are placed in relation to crops. It puts on more or less water to the crop by speeding up or slowing down. Here is the link to the 'old' boom... https://youtu.be/ybX9QwgMrn8

The solenoidValveControl.ino code is used to control a 12 volt solenoid valve with an Arduino. This was to test if my circuit was setup correctly. The circuit was built using a transistor as a switch, not a relay, for effiency and reliability. This code will be very easy to replicate in python for the raspberry pi pins.

See solenoid demonstration video here... https://youtu.be/UQgq7MOaxyc

The only 2 things that still need to be done is 1)a motor driver for the 90 VDC motors that I was retrofitting this build for. There are several options available online. And 2)power supply for the motor driver and raspberry pi. Since the motor driver takes in 120 AC, hook up for the power supply will not be complicated.

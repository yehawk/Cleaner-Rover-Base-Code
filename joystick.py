# Updated code to make content below applicable

import machine
from machine import Pin, ADC
import time
import math
from math import sin, cos, radians

def sleep_ms(ms):
    time.sleep(ms / 1000.0)

# Implement OLED display to simulation
class MockOLED:
    def __init__ (self):
        pass
    def rotate(self, value): pass
    def fill(self, color): pass
    def text(self, string, x, y): pass
    def rect(self, x, y, w, h, c): pass

    def circ(self, x, y, r, c=0): pass
    def line(self, x1, y1, x2, y2, c=1): pass
    def show(self): pass

WIDTH = 128
HEIGHT = 64

def create_PiicoDev_SSD1306():
    return MockOLED()

# Implement transceiver
class MockTransceiver:
    def __init__(self):
        print("transmission booted...")

    def send(self, *args):
        if len(args) == 1 and isinstance(args[0], tuple):
            packet = args[0]
        else:
            packet = args
        print(f"transmitting packet: {packet}")

def PiicoDev_Transceiver():
    return MockTransceiver()

# Original joystick code from core.electronics, modified by me with the help of Gemini 

oled = create_PiicoDev_SSD1306()
oled.rotate(0)

# Start sequence
oled.fill(0)
oled.text("Starting...", 0, 0)
oled.show()
sleep_ms(300)

oled.fill(0)
oled.rect(24,14,80,36,1)
oled.circ(45,28,4,0)
oled.circ(80,27,7,0)
oled.rect(50,40,10,5,1)
oled.line(88,14,88,8,1)
oled.circ(88,4,4,0)
oled.text("RC Rover",0,0)
oled.show()
sleep_ms(2000)

# Pins for Joystick Module
xAxis = ADC(Pin(27))
yAxis = ADC(Pin(26))
button = Pin(17, Pin.IN, Pin.PULL_UP)

radio = PiicoDev_Transceiver()

centreX = int(WIDTH/2)
centreY = int(HEIGHT/2)

# Custom map function - converting the joystick readings to a specified range
def map(input, in_min, in_max, out_min, out_max):
    return (input - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def drawCompass(heading, vel):
    rads = radians(heading + 180)
    length = map(vel, -95, 95, -25, 25)
    if length < 0:
        rads = radians(180 - heading)
    x = int( length * sin(rads) + WIDTH/2 )
    y = int( length * cos(rads) + HEIGHT/2 )

    oled.fill(0)
    oled.line(centreX, centreY, x, y, 1)
    oled.circ(x,y,4)
    oled.text(str(heading),100,57)
    oled.text(str(vel),0,57)
    oled.show()

while True:
    oled.fill(0)

    # Read Joystick potentiometer values
    xValue = xAxis.read_u16()
    yValue = yAxis.read_u16()
    buttonValue = button.value()

    # Getting an angle and speed based on how far forward / backward and left / right the stick is, respectively
    # 65 degrees to 115 degrees was chosen since there are only 2 steering wheels and the chassis is relatively long
    Angle = map(yValue, 0, 65535, 65, 115)
    Speed = int(map(xValue, 0, 65535, -95,95))

    # Buffer zone for noise
    if -10 <= Speed and Speed <= 10:
        Speed = 0

    Heading = 90 - round(Angle)
    drawCompass(Heading, Speed)

    radio.send(("Speed", Speed))
    sleep_ms(25)
    radio.send(("Angle", int(Angle)))
    sleep_ms(25)

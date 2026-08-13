# Updated code to make content below applicable

import machine
import math
import time

def sleep_ms(ms):
    time.sleep(ms / 1000.0)

# Replicate makerverse

class MockMakerverseMotor:
    def __init__(self, pwmPin, dirPin):
        self.pwm = machine.PWM(machine.Pin(pwmPin))
        self.pwm.freq(1000)
        self.dir = machine.Pin(dirPin, machine.Pin.OUT)

    def speed(self, value):
        value = max(-100, min(100, value))
        if value < 0:
            self.dir.value(1) # Reverse
            duty = int((abs(value) / 100.0) * 65535) # Max for 16 bits
        else:
            self.dir.value(0) # Forward
            duty = int((value / 100.0) * 65535)
        self.pwm.duty_u16(duty)

    def stop(self):
        self.pwm.duty_u16(0)
        self.dir.value(0)

def motor(pwmPin, dirPin):
    return MockMakerverseMotor(pwmPin, dirPin)

# Replicate servo

class MockServo:
    def __init__(self, pin_id):
        self.pwm = machine.PWM(machine.Pin(pin_id))
        self.pwm.freq(50)

    def write(self, angle):
        angle = max(0, min(180, angle))
        duty = int(1638 + (angle / 180.0) * (8192 - 1638)) # 12.5% of max, 5% of max
        self.pwm.duty_u16(duty)

def Servo(pin_id):
    return MockServo(pin_id)

# Replicate transceiver

class MockTransceiver:
    def __init__(self):
        self.message = None
        self.step = 0

    def receive(self):
        self.step += 1
        if self.step % 50 == 0:
            self.message = ["Speed", 80]
            return True
        elif self.step % 50 == 10:
            self.message = ["Angle", 73]
            return True
        elif self.step % 50 == 20:
            self.message = ["Angle", 113]
            return True
        elif self.step % 50 == 30:
            self.message = ["Speed", -60] # Reverse
            return True
        elif self.step % 50 == 40:
            self.message = ["Angle", 93] # Return to original angel
            return True
        return False

def PiicoDev_Transceiver():
    return MockTransceiver()

# Imported code form core.electronics, modified by me with the help of Gemini to allow simulation

radio = PiicoDev_Transceiver()

left_servo = Servo(pin_id = 27)
right_servo = Servo(pin_id = 21)

mleft1 = motor(pwmPin = 12, dirPin = 13)
mleft2 = motor(pwmPin = 10, dirPin = 11)
mright1 = motor(pwmPin = 2, dirPin = 3)
mright2 = motor(pwmPin = 0, dirPin = 1)

# # Grouping motors
left_side = [mleft1, mleft2]
right_side = [mright1, mright2]
steering = [left_servo, right_servo]

old_angle = 90
new_angle = 90
speed = 0

# Driving function
def drive(left_speed, right_speed):
    if abs(left_speed) <= 15:
        for left in left_side:
            left.stop()
    else:
        for left in left_side:
            left.speed(left_speed)

    if abs(right_speed) <= 15:
        for right in right_side:
            right.stop()
    else:
        for right in right_side:
            right.speed(right_speed)

while True:
    # Receiving and sorting data
    if radio.receive():
        message = radio.message
        if message[0] == "Speed":
            speed = message[1]
        if message[0] == "Angle":
            new_angle = message[1] - 3

    # Setting Steering angle

    new_angle = max(65, min(115, int(new_angle))) # Trying to avoid incorrect overshoots from servos

    # Gradually moving servos according to direction, adding +step since last value is excluded in range
    if abs(new_angle - old_angle) >= 2:
        for servo in steering:
            servo.write(new_angle)
    else:
        for servo in steering:
            servo.write(old_angle)

    old_angle = new_angle

    # Driving Block:
    # Due to the width of the rover, the wheel speeds have to be changed to avoid slipping and allow turning
    inside_speed = int(0.60*speed)
    outside_speed = int(0.90*speed)

    if 65 <= new_angle and new_angle <= 80:
        drive(inside_speed, outside_speed)
    elif 100 <= new_angle and new_angle <= 115:
        drive(outside_speed, inside_speed)
    else:
        drive(speed, speed)

    sleep_ms(25)

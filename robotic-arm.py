import machine
import time

# Map out pin for each servo
PIN_BASE = 12
PIN_SHOULDER = 13
PIN_ELBOW = 14
PIN_CLAW = 15

# Color sensor values
mock_red_intensity = 240
mock_green_intensity = 240
mock_blue_intensity = 240

# Set up PicoServo
class PicoServo:
  def __init__(self, pin_num):
    self.pwm = machine.PWM(machine.Pin(pin_num))
    self.pwm.freq(50)

  def write_angle(self, angle):
    min_duty = 1638 # 0.5
    max_duty = 8192 # 2.5
    duty = int(min_duty + (angle / 180.0) * (max_duty - min_duty))
    self.pwm.duty_u16(duty)

# Arm joints

base_servo = PicoServo(PIN_BASE)
shoulder_servo = PicoServo(PIN_SHOULDER)
elbow_servo = PicoServo(PIN_ELBOW)
claw_servo = PicoServo(PIN_CLAW)

# Joint constraints (angles, etc.)

CLAW_OPEN = 20
CLAW_CLOSE = 110
HOME_ELBOW = 90
HOME_SHOULDER = 90
DROP_BASE_ANGLE = 160

# Sets "home" status of arm

def reset_arm_back_home():
  claw_servo.write_angle(CLAW_OPEN)
  elbow_servo.write_angle(HOME_ELBOW)
  shoulder_servo.write_angle(HOME_SHOULDER)
  base_servo.write_angle(10)
  time.sleep(0.8)

# If statement: White detected

def if_object_white():
  if mock_red_intensity > 200 and mock_green_intensity > 200 and mock_blue_intensity > 200:
    return True
  return False

# Sweep & grab sequence of arm

def grab_sequence(target_angle):
  print("Target object found, finding path...")
  base_servo.write_angle(target_angle)
  time.sleep(1.2)

  print("Dropping down arm...")
  shoulder_servo.write_angle(45)
  elbow_servo.write_angle(120)
  time.sleep(1.0)

  print("Grip activated...")
  claw_servo.write_angle(CLAW_CLOSE)
  time.sleep(0.8)

  print("Lifting object...")
  shoulder_servo.write_angle(HOME_SHOULDER)
  elbow_servo.write_angle(HOME_ELBOW)
  time.sleep(1.0)

  print("Panning to dispoal area...")
  base_servo.write_angle(DROP_BASE_ANGLE)
  time.sleep(1.2)

  print("Releasing object...")
  claw_servo.write_angle(CLAW_OPEN)
  time.sleep(0.8)

# Execute!
print("Initializing...")
reset_arm_back_home()

while True:
  for angle in range(10, 130, 15):
    base_servo.write_angle(angle)
    time.sleep(0.4)

    if if_object_white():
      print("ALERT: System detected target match!")
      grab_sequence(angle)
      reset_arm_back_home()

    else:
      print("Searching for target match...")

  time.sleep(3.0)

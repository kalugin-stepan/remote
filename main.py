import time
from threading import Thread
import serial
import paho.mqtt.client as mqtt
import numpy as np
import RPi.GPIO as GPIO

ROBOT_ID = 'robot1'

ser = serial.Serial()
ser.baudrate = 115200
ser.port = '/dev/ttyACM0'
# ser.port = '/dev/ttyAMA0'
ser.open()
ser.timeout = 1
ser.write(b'\r\r')
data = ser.read_until()
ser.write(b'les\n')
ser.write(b'\r\r')
ser.write(b'les\n')

def read_coords() -> list[float]:
    data = ser.readline().decode('ascii')
    while len(data) <= 10:
        data = ser.readline().decode('ascii')

    while True:
        try:
            return list(map(float, data.split()[-1].replace('est', '').replace('[', '').replace(']', '').split(',')))
        except:
            data = ser.readline().decode('ascii')

# Set the type of GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Motor drive interface definition
ENA = 13  # L298 Enable A
ENB = 20  # L298 Enable B
IN1 = 19  # Motor interface 1
IN2 = 16  # Motor interface 2
IN3 = 21  # Motor interface 3
IN4 = 26  # Motor interface 4

# Motor initialized to LOW
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(IN2, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(ENB, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(IN4, GPIO.OUT, initial=GPIO.LOW)
pwmA = GPIO.PWM(ENA, 100)
pwmB = GPIO.PWM(ENB, 100)
pwmA.start(0)
pwmB.start(0)

client = mqtt.Client()
client.connect('10.23.202.66')

client.subscribe(ROBOT_ID)

def on_message(client, userdata, message):
    dir = np.frombuffer(message.payload, dtype=np.int8)

    v = float(dir[1])
    s = float(dir[0])

    m1 = v + s
    m2 = v - s

    if abs(m1) > 100 and m1 > 0:
        m1 = 100
    if abs(m1) > 1 and m1 < 0:
        m1 = -100

    if abs(m2) > 100 and m2 > 0:
        m2 = 100
    if abs(m2) > 100 and m2 < 0:
        m2 = -100

    pwmA.ChangeDutyCycle(100 if abs(m1) > 100 else abs(m1))
    pwmB.ChangeDutyCycle(100 if abs(m2) > 100 else abs(m2))

    if m1 > 0:
        GPIO.output(IN3, True)
        GPIO.output(IN4, False)
    elif m1 < 0:
        GPIO.output(IN3, False)
        GPIO.output(IN4, True)
    else:
        pwmA.ChangeDutyCycle(0)
        GPIO.output(IN3, False)
        GPIO.output(IN4, False)

    if m2 > 0:
        GPIO.output(IN1, True)
        GPIO.output(IN2, False)
    elif m2 < 0:
        GPIO.output(IN1, False)
        GPIO.output(IN2, True)
    else:
        pwmB.ChangeDutyCycle(0)
        GPIO.output(IN1, False)
        GPIO.output(IN2, False)


client.on_message = on_message

Thread(target=client.loop_forever).start()

pos_topic = ROBOT_ID + ':pos'

print(pos_topic)

last_msg_time = time.time()

while True:
    data = read_coords()
    if time.time() - last_msg_time > 4:
        client.publish(pos_topic, np.array(data, dtype=np.float32).tobytes())
        last_msg_time = time.time()
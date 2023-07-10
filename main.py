import paho.mqtt.client as mqtt
import json
import RPi.GPIO as GPIO

ROBOT_ID = 'robot1'

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
client.connect('broker.emqx.io')

client.subscribe(ROBOT_ID)

def on_message(client, userdata, message):
    data = message.payload.decode()
    dir = json.loads(data)

    v = 0
    s = 0

    if dir['F']:
        v += 1
    if dir['B']:
        v -= 1
    if dir['L']:
        s -= 1
    if dir['R']:
        s += 1

    GPIO.output(ENA, True)
    GPIO.output(ENB, True)

    m1 = v + s
    m2 = v - s

    if abs(m1) > 1 and m1 > 0:
        m1 = 1
    if abs(m1) > 1 and m1 < 0:
        m1 = -1

    if abs(m2) > 1 and m2 > 0:
        m2 = 1
    if abs(m2) > 1 and m2 < 0:
        m2 = -1

    pwmA.ChangeDutyCycle(abs(m1) * 100)
    pwmB.ChangeDutyCycle(abs(m2) * 100)

    if m1 > 0:
        GPIO.output(IN1, True)
        GPIO.output(IN2, False)
    elif m1 < 0:
        GPIO.output(IN1, False)
        GPIO.output(IN2, True)
    else:
        pwmA.ChangeDutyCycle(0)
        GPIO.output(IN1, False)
        GPIO.output(IN2, False)

    if m2 > 0:
        GPIO.output(IN3, True)
        GPIO.output(IN4, False)
    elif m2 < 0:
        GPIO.output(IN3, False)
        GPIO.output(IN4, True)
    else:
        pwmB.ChangeDutyCycle(0)
        GPIO.output(IN3, False)
        GPIO.output(IN4, False)


client.on_message = on_message

while True:
    client.loop()
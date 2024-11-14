import time
import json
from queue import Queue
from i2c_itg3205 import i2c_itg3205
import RPi.GPIO as GPIO
import serial
from math import atan2, degrees
import paho.mqtt.client as mqtt
from threading import Thread
import numpy as np
from simple_pid import PID
from filter import KalmanFilter



with open('config.json') as json_file:
    config = json.load(json_file)


ROBOT_ID = config['ROBOT_ID']

RULER_ID = config['RULER_ID']

GYRO_ERROR = float(config['GYRO_ERROR'])

MQTT_HOST = config['MQTT_HOST']

INIT_ANG = float(config['INIT_ANG'])

P_ANGLE = float(config['P_ANGLE'])

P_DIST = float(config['P_DIST'])

T = float(config['T'])

points = Queue()

client = mqtt.Client()
client.connect(MQTT_HOST)

client.subscribe(RULER_ID + ':pos')

ser = serial.Serial()
ser.baudrate = 115200
ser.port = '/dev/ttyACM0'
ser.open()
ser.timeout = 1
ser.write(b'\r\r')
data = ser.readline()
ser.write(b'les\n')
ser.write(b'\r\r')
ser.write(b'les\n')

def read_coords() -> list[float]:
    data = ser.readline().decode('ascii')
    while len(data) <= 10:
        data = ser.readline().decode('ascii')
    #print(data)
    while True:
        try:
            coords = list(map(float, data.split()[-1].replace('est', '').replace('[', '').replace(']', '').split(',')))
            client.publish(ROBOT_ID + ':pos', np.array([coords[0], coords[1]], dtype=np.float32).tobytes())
            return coords
        except:
            data = ser.readline().decode('ascii')

def read_coords_kal() -> list[float]:
    global kfilter_self
    data = ser.readline().decode('ascii')
    while len(data) <= 10:
        data = ser.readline().decode('ascii')

    while True:
        try:
            coords = list(map(float, data.split()[-1].replace('est', '').replace('[', '').replace(']', '').split(',')))
            data = np.array([coords[0], coords[1]], dtype=np.float32)
            client.publish(ROBOT_ID + ':pos', data.tobytes())
            return kfilter_self(data)
        except:
            data = ser.readline().decode('ascii')

global a, target_a, x, y, kfilter_fwd, kfilter_self
a = INIT_ANG
target_a = a
p_ang = P_ANGLE
[x, y, _, _] = read_coords()
target_x, target_y = x, y
p_dist = P_DIST

VECTOR_SIZE = 2
D_n = np.diag([0.1, 0.1])
D_ksi = np.diag([0.01, 0.01])

F = np.array([[1, 0],
              [0, 1]])

G = np.array([[T, 0],
              [0, T]])

H = np.array([[1, 0],
              [0, 1]])

kfilter_fwd = KalmanFilter(VECTOR_SIZE, T, D_n, D_ksi, F, G, H, np.array([x, y]), 20)
kfilter_self = KalmanFilter(VECTOR_SIZE, T, D_n, D_ksi, F, G, H, np.array([x, y]), 20)

print(RULER_ID + ':pos')

def on_message(clinet, userdata, data):
    global kfilter_fwd
    point = np.frombuffer(data.payload, dtype=np.float32)
    pos = kfilter_fwd(point)
    points.put(pos)

client.on_message = on_message

Thread(target=client.loop_forever).start()

gyro = i2c_itg3205(1)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

ENA = 13
ENB = 20
IN1 = 19
IN2 = 16
IN3 = 21
IN4 = 26

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

pid = PID(1, 1, 0.05)
pid.output_limits = (-70, 70)

def diff(a: float, b: float) -> float:
    if abs(a - b) < abs(a + b - 360):
        return a - b
    return a + b - 360

def rotate():
    global a, target_a
    pid_output = pid(diff(target_a, a))

    m1 = pid_output
    m2 = -pid_output 

    if m1 > 0:
        GPIO.output(IN1, True)
        GPIO.output(IN2, False)
    elif m1 < 0:
        GPIO.output(IN1, False)
        GPIO.output(IN2, True)
    else:
        GPIO.output(IN1, False)
        GPIO.output(IN2, False)
    if m2 > 0:
        GPIO.output(IN3, True)
        GPIO.output(IN4, False)
    elif m2 < 0:
        GPIO.output(IN3, False)
        GPIO.output(IN4, True)
    else:
        GPIO.output(IN3, False)
        GPIO.output(IN4, False)

    pwmA.ChangeDutyCycle(abs(m1))
    pwmB.ChangeDutyCycle(abs(m2))
    target_a %= 360

try:
    while True:
        start_time = time.time()
        if not points.empty():
            point = points.get()

            target_x = float(point[0])
            target_y = float(point[1])

            target_a = degrees(atan2(target_y - y, target_x - x))
            if target_a < 0: target_a += 360
            #print(target_a)

        [x, y, _, _] = read_coords()
        #[x, y] = read_coords_kal()

        x = float(x)
        y = float(y)

        _, _, z = gyro.getDegPerSecAxes()
        end_time = time.time()
        dt = end_time - start_time
        a += (z - GYRO_ERROR) * dt
        a %= 360

        dx = target_x - x
        dy = target_y - y
        # print(target_x, target_y, x, y, sqrt(dx*dx + dy*dy))
        if abs(diff(target_a, a)) > p_ang:
            pid.sample_time = dt
            rotate()
        elif dx*dx + dy*dy > p_dist*p_dist:
            GPIO.output(IN1, True)
            GPIO.output(IN2, False)
            GPIO.output(IN3, True)
            GPIO.output(IN4, False)
            pwmA.ChangeDutyCycle(60)
            pwmB.ChangeDutyCycle(60)
            target_a = degrees(atan2(target_y - y, target_x - x))
            if target_a < 0: target_a += 360
        else:
            GPIO.output(IN1, False)
            GPIO.output(IN2, False)
            GPIO.output(IN3, False)
            GPIO.output(IN4, False)
            pwmA.ChangeDutyCycle(0)
            pwmB.ChangeDutyCycle(0)
finally:
    GPIO.output(IN1, False)
    GPIO.output(IN2, False)
    GPIO.output(IN3, False)
    GPIO.output(IN4, False)
    pwmA.ChangeDutyCycle(0)
    pwmB.ChangeDutyCycle(0)

    ser.close()
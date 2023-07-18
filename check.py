import paho.mqtt.client as mqtt
import numpy as np

ROBOT_ID = 'robot1:pos'

client = mqtt.Client()

client.connect('10.23.202.223')

def on_message(client, userdata, data):
    pos = np.frombuffer(data.payload, dtype=np.float32)
    print(pos)

client.on_message = on_message

client.subscribe(ROBOT_ID)

while True:
    client.loop()
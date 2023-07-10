import paho.mqtt.client as mqtt
import numpy as np

ROBOT_ID = 'robot1'

client = mqtt.Client()

client.connect('10.23.202.198')

def on_message(client, userdata, data):
    if len(data.payload) != 2: return
    pos = np.frombuffer(data.payload, dtype=np.int8)
    print(pos[0], pos[1])

client.on_message = on_message

client.subscribe(ROBOT_ID)

while True:
    client.loop()
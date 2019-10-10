import sys
import json
import paho.mqtt.client as mqtt

current_state = None
    
def on_connect(mqttc, obj, flags, rc):
    print("rc: "+str(rc))

def on_message(mqttc, obj, msg):

    print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))

    if mg.topic == "v1/devices/43de2329-8808-57bc-af5b-ea01bd6a6d11/status/reply":
        parsed = json.loads(msg.payload)
        current_state = parsed
    
def on_publish(mqttc, obj, mid):
    print("mid: "+str(mid))

def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_log(mqttc, obj, level, string):
    print(string)

def is_on(identifier, elementIdentifier):
    if current_state is None:
        return false

    return current_state[identifier][status][elementIdentifier][state] == 1

def turnOn(identifier, elementIdentifier):

    data = {}

    status = {}
    status["state"] = 1

    element = {}
    element[elementIdentifier] = status

    device = {}
    device["status"] = element

    data[identifier] = device

    json_data = json.dumps(data)

    print(json_data)

    mqttc.publish("v1/devices/43de2329-8808-57bc-af5b-ea01bd6a6d11/control", payload="{}", qos=0, retain=false)

def turnOff(identifier, elementIdentifier):

    data = {}

    status = {}
    status["state"] = 0

    element = {}
    element[elementIdentifier] = status

    device = {}
    device["status"] = element

    data[identifier] = device

    json_data = json.dumps(data)

    print(json_data)

    mqttc.publish("v1/devices/43de2329-8808-57bc-af5b-ea01bd6a6d11/control", payload="{}", qos=0, retain=false)

def connect(host, username, password):
    mqttc = mqtt.Client(client_id="HASS", transport="websockets")   
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe

    mqttc.username_pw_set(username, password=password)

    mqttc.connect(host, 1884, 60)

    mqttc.subscribe("#", 0)
    mqttc.subscribe("$SYS/#", 0)

    mqttc.loop_start()

def disconnect():
    mqttc.loop_stop()
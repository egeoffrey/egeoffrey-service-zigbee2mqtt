### service/zigbee2mqtt: Integrate with Zigbee2mqtt by connecting to the same mqtt broker Zigbee2mqtt is publishing devices data
## HOW IT WORKS: 
## DEPENDENCIES:
# OS: 
# Python: paho-mqtt
## CONFIGURATION:
# required: hostname, port, base_topic
# optional: username, password
## COMMUNICATION:
# INBOUND: 
# - controller/hub OUT: 
#   required: device_id, key, value
#   optional: 
# OUTBOUND:
# - controller/hub IN: 
#   required: device_id, key
#   optional: filter

import json

import paho.mqtt.client as mqtt

from sdk.python.module.service import Service
from sdk.python.module.helpers.message import Message

import sdk.python.utils.exceptions as exception

class Zigbee2mqtt(Service):
    # What to do when initializing
    def on_init(self):
        # configuration
        self.config = {}
        # track the topics subscribed
        self.topics_to_subscribe = []
        self.topics_subscribed = []
        # mqtt object
        self.client = mqtt.Client()
        self.mqtt_connected = False
        # require configuration before starting up
        self.config_schema = 1
        self.add_configuration_listener(self.fullname, "+", True)
        
    # What to do when running
    def on_start(self):
        # receive callback when connecting
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                self.log_debug("Connected to the MQTT gateway ("+str(rc)+")")
                # subscribe to previously queued topics
                for topic in self.topics_to_subscribe:
                    self.subscribe_topic(topic)
                self.topics_to_subscribe = []
                self.mqtt_connected = True
            
        # receive a callback when receiving a message
        def on_message(client, userdata, msg):
            self.log_debug("received on "+str(msg.topic)+": "+str(msg.payload))
            # find the sensor matching the topic
            for sensor_id in self.sensors:
                configuration = self.sensors[sensor_id]
                # if the message is for this sensor
                if msg.topic.endswith("/"+str(configuration["device_id"])):
                    # parse the payload
                    try:
                        data = json.loads(msg.payload)
                    except Exception,e:
                        self.log_warning("Unable to parse payload "+str(msg.payload)+": "+exception.get(e))
                        return
                    # skip if key is missing from the payload
                    if configuration["key"] not in data: 
                        continue
                    # apply the filter if any
                    if "filter" in configuration:
                        search = {}
                        if "&" in configuration["filter"]: key_values = configuration["filter"].split("&")
                        else: key_values = [configuration["filter"]]
                        for key_value in key_values:
                            if "=" not in key_value: continue
                            key, value = key_value.split("=")
                            search[key] = value
                        # check if the output matches the search string
                        found = True
                        for key, value in search.iteritems():
                            # check every key/value pair
                            if key not in data: found = False
                            if key in data and str(value).lower() != str(data[key]).lower(): found = False
                        # not matching, skip to the next sensor
                        if not found: continue
                    value = data[configuration["key"]]
                    # ignore empty values (when homeassistant is true, zigbee2mqtt will report an empty value just after a value
                    if value == "": continue
                    self.log_debug("reporting "+sensor_id+" with value "+str(value))
                    # prepare the message
                    message = Message(self)
                    message.recipient = "controller/hub"
                    message.command = "IN"
                    message.args = sensor_id
                    message.set("value", value)
                    # send the measure to the controller
                    self.send(message)
            
        # connect to the gateway
        try: 
            self.log_info("Connecting to MQTT gateway on "+self.config["hostname"]+":"+str(self.config["port"]))
            password = self.config["password"] if "password" in self.config else ""
            if "username" in self.config: self.client.username_pw_set(self.config["username"], password=password)
            self.client.connect(self.config["hostname"], self.config["port"], 60)
        except Exception,e:
            self.log_warning("Unable to connect to the MQTT gateway "+self.config["hostname"]+":"+str(self.config["port"])+": "+exception.get(e))
            return
        # set callbacks
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        # start loop (in the background)
        try: 
            self.client.loop_start()
        except Exception,e: 
            self.log_error("Unexpected runtime error: "+exception.get(e))
    
    # What to do when shutting down
    def on_stop(self):
        self.client.loop_stop()
        self.client.disconnect()
        
    # What to do when receiving a request for this module
    def on_message(self, message):
        sensor_id = message.args
        if message.command == "OUT":
            if not self.mqtt_connected: return
            if not self.is_valid_configuration(["device_id", "key", "value"], message.get_data()): return
            topic = self.config["base_topic"]+"/"+message.get("device_id")+"/set"
            data = {}
            data[message.get("key")] = message.get("value")
            data = json.dumps(data)
            # send the message
            self.log_info("sending message "+data+" to "+topic)
            self.client.publish(topic, data)
        
    # subscribe to a mqtt topic
    def subscribe_topic(self, device_id):
        topic = self.config["base_topic"]+"/"+str(device_id)
        self.log_debug("Subscribing to the MQTT topic "+topic)
        self.topics_subscribed.append(topic)
        self.client.subscribe(topic)

    # What to do when receiving a new/updated configuration for this module    
    def on_configuration(self,message):
        # module's configuration
        if message.args == self.fullname and not message.is_null:
            if message.config_schema != self.config_schema: 
                return False
            if not self.is_valid_configuration(["hostname", "port", "base_topic"], message.get_data()): return False
            self.config = message.get_data()
        # register/unregister the sensor
        if message.args.startswith("sensors/"):
            if message.is_null: 
                sensor_id = message.args.replace("sensors/","")
                self.unregister_sensor(message)
            else: 
                # TODO: certificate, client_id, ssl
                sensor_id = self.register_sensor(message, ["device_id", "key"])
                # subscribe to the topic if connected, otherwise queue the request
                if sensor_id is not None and message.get("service")["mode"] != "actuator":
                    configuration = self.sensors[sensor_id]
                    if self.mqtt_connected: 
                        self.subscribe_topic(configuration["device_id"])
                    else: 
                        self.topics_to_subscribe.append(configuration["device_id"])

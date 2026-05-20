import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime, timezone

# Baca dari config.json
with open("config.json") as f:
    config = json.load(f)

BROKER_HOST = config["BROKER_HOST"]
BROKER_PORT = config["BROKER_PORT"]
TOPIC       = config["TOPIC"]
DEVICE_ID   = "sensor-001"
INTERVAL    = 2

def generate_sensor_data() -> dict:
    return {
        "device_id":   DEVICE_ID,
        "timestamp":   datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "temperature": round(random.uniform(24.0, 35.0), 2),
        "humidity":    round(random.uniform(40.0, 90.0), 2),
        "unit": {
            "temperature": "Celsius",
            "humidity":    "Percent"
        }
    }

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Terhubung ke broker MQTT: {BROKER_HOST}:{BROKER_PORT}")
        print(f"Publish ke topik: '{TOPIC}' setiap {INTERVAL} detik\n")
    else:
        print(f"Gagal terhubung, kode: {rc}")

def on_disconnect(client, userdata, rc):
    print("Terputus dari broker MQTT")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=DEVICE_ID)
client.on_connect    = on_connect
client.on_disconnect = on_disconnect

print(f"Menghubungkan ke {BROKER_HOST}:{BROKER_PORT}...")
client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
client.loop_start()

try:
    while True:
        payload = generate_sensor_data()
        result  = client.publish(TOPIC, json.dumps(payload), qos=1)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"[{payload['timestamp']}] TEMP: {payload['temperature']}C | HUM: {payload['humidity']}%")
        else:
            print(f"Gagal publish, kode: {result.rc}")
        time.sleep(INTERVAL)

except KeyboardInterrupt:
    print("\nGenerator dihentikan.")
    client.loop_stop()
    client.disconnect()
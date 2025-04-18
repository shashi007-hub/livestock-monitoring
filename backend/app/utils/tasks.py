from mqtt.client import mqtt_client

def publish_task(task_data: dict):
    import json
    mqtt_client.publish("inference/tasks", json.dumps(task_data))

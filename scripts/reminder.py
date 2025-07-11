from datetime import datetime
import json
import pytz
import consul
from confluent_kafka import Producer

# Kafka configuration
producer_conf = {
    'bootstrap.servers': 'IP.IP51.14:6667,',
    'log.connection.close': False
}
producer = Producer(producer_conf)
KAFKA_TOPIC = "abcDLK_MONITOR"

def delivery_report(err, msg):
    if err is not None:
        print(f"❌ Delivery failed for record {msg.key()}: {err}")
    else:
        print(f"✅ Reminder delivered to {msg.topic()} [{msg.partition()}]")

# Read JSON from Consul
def read_json_from_consul(json_key_name):
    c = consul.Consul(host='IP.IP.37.163', port=8500, token='4eb5bd5e-5500-9b1f-af41-1da254f11bfa')
    index, data = c.kv.get(f'abcdlk/reminder/{json_key_name}')
    if data is None:
        raise ValueError(f"Key '{json_key_name}' not found in Consul")
    
    value = data["Value"]
    try:
        json_data = json.loads(value)
    except Exception:
        json_data = json.loads(json.loads(value))

    return json_data

# Process SSL certificate entry
def process_certificate(cert):
    expiry_date = datetime.strptime(cert["expiry"], "%Y-%m-%d")
    today = datetime.now()
    days_remaining = (expiry_date - today).days
    threshold = cert.get("alert_before_days", 30)

    if days_remaining < 0:
        state = "critical"
    elif days_remaining < threshold:
        state = "critical"
    elif days_remaining == threshold:
        state = "warning"
    else:
        return None

    hostname = cert["message"].split()[-1]

    return {
        "service_group": "External-Comp",
        "service": "SSL cert",
        "primary_component": hostname,
        "event_time": datetime.now(pytz.UTC).isoformat(),
        "state": state,
        "message": cert["add_details"]
    }

if __name__ == "__main__":
    data = read_json_from_consul("reminder.json")
    print(json.dumps(data, indent=2))
    #print(data)
    for cert in data.get("reminders", []):
        result = process_certificate(cert)
        if result:
            json_payload = json.dumps(result)
            print("Generated Reminder:", json_payload)
            try:
                producer.produce(
                    KAFKA_TOPIC,
                    key=result["primary_component"],
                    value=json_payload,
                    callback=delivery_report
                )
            except BufferError:
                print("⚠️ Kafka buffer full, flushing...")
                producer.flush()
                producer.produce(KAFKA_TOPIC, key=result["primary_component"], value=json_payload, callback=delivery_report)

    # Flush remaining messages
    producer.flush()

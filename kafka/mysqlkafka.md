## Stream MySQL Data to Kafka and Persist Kafka Messages as JSON Files

???-  "Import statement"
    ```bash
    import mysql.connector
    import mysql.connector as connection
    import random
    import time
    from datetime import datetime, timedelta
    import os
    ```
???- "Create mysql table"
    ```bash
 
    db = mysql.connector.connect(
    host='hostname',
    user='manish',
    passwd='Dlkadmin#2024',
    database='manish'
    )

    cursor = db.cursor()

    query = """
    CREATE TABLE API_product_updates_new (
        id INT PRIMARY KEY,
        name VARCHAR(255),
        category VARCHAR(255),
        price FLOAT,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """

    cursor.execute(query)
    print("Table has been created successfully.")

    cursor.close()
    db.close()
    ```
???-  "Import data in table"
    ```bash
    # Connect to DB
    db = mysql.connector.connect(
        host='hostname',
        user='manish',
        passwd='Dlkadmin#2024',
        database='manish'
    )

    cursor = db.cursor()

    # Sample data lists
    names = ['Phone', 'Tablet', 'Laptop', 'Monitor', 'Mouse', 'Keyboard', 'Speaker']
    categories = ['Electronics', 'Accessories', 'Audio', 'Computing']

    # Generate 300 fake product records
    products = []
    for i in range(1, 301):
        name = random.choice(names) + f" {random.randint(1, 100)}"
        category = random.choice(categories)
        price = round(random.uniform(10.0, 5000.0), 2)
        random_days = random.randint(0, 6)
        random_seconds = random.randint(0, 86400)  # seconds in a day
        last_updated = datetime.now() - timedelta(days=random_days, seconds=random_seconds)
        products.append((i, name, category, price,last_updated))
        

    # Insert query
    insert_query = """
    INSERT INTO API_product_updates_new (id, name, category, price,last_updated)
    VALUES (%s, %s, %s, %s,%s)
    """

    # Execute batch insert
    cursor.executemany(insert_query, products)
    db.commit()

    print(f"{cursor.rowcount} records inserted successfully.")

    cursor.close()
    db.close()
    ```

???-  "push data to topic from table"
    ```bash
    # === CONFIG ===
    bootstrap_servers = [
        "hostname1.abc.com:6667",
        "hostname2.abc.com:6667",
        "hostname3.abc.com:6667"
    ]
    topic_name = "API_product_updates"
    timestamp_file = "last_read_timestamp.txt"

    # === Step 1: Get last read timestamp ===
    def get_last_read_timestamp():
        if os.path.exists(timestamp_file):
            with open(timestamp_file, "r") as f:
                return f.read().strip()
        else:
            return "2000-01-01 00:00:00"  # default start

    # === Step 2: Save last read timestamp ===
    def update_last_read_timestamp(ts):
        with open(timestamp_file, "w") as f:
            f.write(ts)

    # === Step 3: Setup Kafka producer ===
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        security_protocol="SASL_SSL",
        sasl_mechanism="SCRAM-SHA-512",
        sasl_plain_username="developer",
        sasl_plain_password="developer#123",
        ssl_cafile="/home/manishkumar2.c/devtruststore_combined.pem",
        value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
        key_serializer=lambda k: str(k).encode("utf-8")
    )

    # === Step 4: Connect to MySQL and fetch new records ===
    last_ts = get_last_read_timestamp()
    max_ts = datetime.fromisoformat(last_ts)  # Convert to datetime object


    db = mysql.connector.connect(
        host='hostname',
        user='manish',
        passwd='Dlkadmin#2024',
        database='manish'
    )
    cursor = db.cursor()

    query = "SELECT * FROM API_product_updates_new WHERE last_updated > %s ORDER BY last_updated ASC"
    cursor.execute(query, (last_ts,))
    records = cursor.fetchall()

    # If no records, exit early
    if not records:
        print("No new records found.")
        cursor.close()
        db.close()
        exit(0)

    # === Step 5: Produce messages to Kafka ===
    for row in records:
        data = {
            "id": row[0],
            "name": row[1],
            "category": row[2],
            "price": row[3],
            "lastupdated": row[4]
        }
        key = row[0]  # product ID as key
        producer.send(topic_name, value=data, key=key)
        # Update max_ts to latest lastupdated
        if row[4] > max_ts:
            max_ts = row[4]

    producer.flush()
    print(f"{len(records)} messages sent to Kafka.")

    # === Step 6: Save last timestamp ===
    update_last_read_timestamp(max_ts.isoformat())

    # Clean up
    cursor.close()
    db.close()
    ```
???-  "Consume data from topic and write to json"
    ```bash
    from kafka import KafkaConsumer
    import json
    import os

    # Kafka config
    bootstrap_servers = [
        "hostname1.abc.com:6667",
        "hostname2.abc.com:6667",
        "hostname3.abc.com:6667"
    ]

    topic_name = "API_product_updates"

    # Create output directory if it doesn't exist
    output_dir = "./kafka_output"
    os.makedirs(output_dir, exist_ok=True)

    # Set up Kafka consumer
    consumer = KafkaConsumer(
        topic_name,
        bootstrap_servers=bootstrap_servers,
        security_protocol="SASL_SSL",
        sasl_mechanism="SCRAM-SHA-512",
        sasl_plain_username="developer",
        sasl_plain_password="developer#123",
        ssl_cafile="/home/manishkumar2.c/devtruststore_combined.pem",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id="developer"
    )

    # Read messages and write to JSON files
    print("Consuming messages and writing to files...")

    for idx, message in enumerate(consumer):
        file_path = os.path.join(output_dir, f"message_{idx+1}.json")
        with open(file_path, "w") as f:
            json.dump(message.value, f, indent=2)
        print(f"Saved: {file_path}")

        # Stop after 300 messages
        if idx + 1 >= 300:
            break

    consumer.close()
    print("Done! 300 files written.")
    ```

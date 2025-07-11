#!/usr/bin/env python3

import socket
from contextlib import closing
from datetime import datetime
import os
import logging
from confluent_kafka import Producer
import sys

# Configure logger to show everything in Airflow UI
logger = logging.getLogger("port_check_logger")
logger.setLevel(logging.INFO)

# Stream handler for stdout (Airflow UI captures stdout)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Timestamp
date_N_days_ago = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Counters
up_count = 0
down_count = 0

# JSON output
jsonfile = "kafkaproduce_daily.json"

# Kafka producer config
producer_conf = {
    'bootstrap.servers': 'IP.IP51.13:6667,IP.IP51.14:6667,IP.IP51.15:6667',
    'log.connection.close': False
}
p = Producer(producer_conf)


def delivery_report(err, msg):
    if err is not None:
        logger.error('Kafka delivery failed: %s', err)
    else:
        logger.info('Kafka message delivered to %s [%s]', msg.topic(), msg.partition())


def check_socket(host, port, app):
    global up_count, down_count

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        state = 'SUCCESS' if result == 0 else 'FAILED'
        color = 'blue' if result == 0 else 'red'
        status = 'WORKING' if result == 0 else 'CLOSED'

        log_message = f"[{state}] {host}:{port} ({app}) is {status}"
        logger.info(log_message)

        json_message = '{{"service_group":"External-Comp","service":"{app}","primary_component":"{host}:{port}","event_time":"{date}","state":"{state}","message":"External-Component-{state}"}}'.format(
            app=app, host=host, port=port, date=date_N_days_ago, state=state
        )

        # Save to file
        with open(jsonfile, "a") as f:
            print(json_message, file=f)

        if result == 0:
            up_count += 1
        else:
            down_count += 1
            # Only send failed messages to Kafka
            try:
                p.produce("ABCDLK_MONITOR", json_message.encode('utf-8'), callback=delivery_report)
                p.poll(0)
            except Exception as e:
                logger.error("Error producing to Kafka: %s", e)

        return (port, color, status, host, app)


def main():
    logger.info("===== Starting Port Health Check at %s =====", date_N_days_ago)

    checks = [
        ('srdcb1653prmdm.abc.com', 6667, 'KAFKA|kafka'),
        ('sidcABCdlkkfk01.abc.com', 6667, 'IP.IP131.158|ABC-KAFKA-1'),
        ('sidcABCdlkkfk02.abc.com', 6667, 'IP.IP131.159|ABC-KAFKA-2'),
        ('sidcABCdlkkfk03.abc.com', 6667, 'IP.IP131.160|ABC-KAFKA-3'),
        ('sidcABCdlkkfkz1.abc.com', 2181, 'IP.IP131.161|ABC-ZK-1'),
        ('sidcABCdlkkfkz2.abc.com', 2181, 'IP.IP131.162|ABC-ZK-2'),
        ('sidcABCdlkkfkz3.abc.com', 2181, 'IP.IP131.163|ABC-ZK-3'),
        ('sidcrdssign01.abc.com', 10800, 'IP.IP109.41|ABC-IGNITE-1'),
        ('sidcrdssign02.abc.com', 10800, 'IP.IP109.42|ABC-IGNITE-2'),
        ('sidcrdssign03.abc.com', 10800, 'IP.IP109.43|ABC-IGNITE-3'),
        ('sidcprodvmdm', 8793, 'IP.IP42.11|ADMIN-AIRFLOW-WORKER'),
        ('sidcprodvmdm', 8081, 'IP.IP42.11|ADMIN-AIRFLOW-WEBSERVER'),
        ('sidcprodvmdm', 15672, 'IP.IP42.11|ADMIN-AIRFLOW-RABBITMQ'),
        ('sidcprodvmdm', 5555, 'IP.IP42.11|ADMIN-AIRFLOW-FLOWER'),
        ('sidcprodvmdm', 3306, 'IP.IP42.11|ADMIN-AIRFLOW-DB'),
        ('srdcb1636prled.abc.com', 2181, 'ZOOKEEPER|zookeeper'),
        ('srdcABChdmn05.abc.com', 9090, 'NIFI|nifi'),
        ('srdcABChdmn08.abc.com', 8090, 'TOMCAT|apache tomcat'),
        ('srdcABChdmn06.abc.com', 5555, 'AIRFLOW|airflow flower'),
        ('sidcprdABCkfk01.abc.com', 6667, 'kafka-sap'),
        ('sidcABCdlkkfk01.abc.com', 6667, 'KAFKA|ABCkafka'),
        ('srdcABChdes01.abc.com', 9200, 'elasticsearch')
    ]

    for host, port, app in checks:
        check_socket(host, port, app)

    p.flush()

    logger.info("===== Port Check Finished: %d UP, %d DOWN =====", up_count, down_count)

    if os.path.exists(jsonfile):
        os.remove(jsonfile)


if __name__ == "__main__":
    main()

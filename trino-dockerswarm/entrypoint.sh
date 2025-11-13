#!/bin/bash

# Populate node.id from uuidgen by replacing template with the node uuid
nodeid() {
 #sed -i "s/\$(uuid-generated-nodeid)/$(uuidgen)/g" /usr/lib/trino-server-397/etc/node.properties
 sed -i "s/HOSTNAME/$(uuidgen)/g" /usr/lib/trino-server-418/etc/node.properties
}


worker_config() {
(
echo "coordinator=false"
echo "query.max-memory=${TRINO_MAX_MEMORY}GB"
echo "query.max-memory-per-node=${TRINO_MAX_MEMORY_PER_NODE}GB"
echo "query.max-total-memory=${TRINO_MAX_TOTAL_MEMORY}GB"
echo "query.hash-partition-count=10"
echo "discovery.uri=https://${COORDINATOR}:${HTTP_SERVER_PORT}"
echo "internal-communication.https.required=true"
echo "internal-communication.shared-secret=iAzZ1WiMJgL4FZeAuKnsxrlWkiU="
echo "node.internal-address=${HOSTNAME}"
echo "internal-communication.https.keystore.path=/etc/trino/trustore.jks"
echo "internal-communication.https.keystore.key=ba2115520c27e8"
echo "http-server.authentication.type=PASSWORD"
echo "http-server.https.keystore.path=/etc/trino/keystore.jks"
echo "http-server.https.keystore.key=ba2115520c27e8"
echo "http-server.https.enabled=true"
echo "http-server.https.port=${HTTP_SERVER_PORT}"
echo "http-server.http.enabled=false"
echo "protocol.v1.alternate-header-name=Presto"
echo "query_max_execution_time=1800s"
) >/usr/lib/trino-server-418/etc/config.properties
}

coordinator_config() {
(
echo "coordinator=true"
echo "node-scheduler.include-coordinator=false"
echo "query.max-memory=${TRINO_MAX_MEMORY}GB"
echo "query.max-memory-per-node=${TRINO_MAX_MEMORY_PER_NODE}GB"
echo "query.max-total-memory=${TRINO_MAX_TOTAL_MEMORY}GB"
echo "query.hash-partition-count=10"
echo "discovery.uri=https://${HOSTNAME}:${HTTP_SERVER_PORT}"
echo "internal-communication.https.required=true"
echo "internal-communication.shared-secret=iAzZ1WiMJgL4FZeAuKnsxrlWkiU="
echo "node.internal-address=${HOSTNAME}"
echo "internal-communication.https.keystore.path=/etc/trino/trustore.jks"
echo "internal-communication.https.keystore.key=ba2115520c27e8"
echo "http-server.authentication.type=PASSWORD"
echo "http-server.https.keystore.path=/etc/trino/keystore.jks"
echo "http-server.https.keystore.key=ba2115520c27e8"
echo "http-server.https.enabled=true"
echo "http-server.https.port=${HTTP_SERVER_PORT}"
echo "http-server.http.enabled=false"
echo "protocol.v1.alternate-header-name=Presto"
echo "event-listener.config-files=/etc/trino/http-event-listener.properties"
echo "query_max_execution_time=1800s"
) >/usr/lib/trino-server-418/etc/config.properties



}



jvm_config() {
  sed -i "s/-Xmx.*G/-Xmx${TRINO_JVM_HEAP_SIZE}G/" /usr/lib/trino-server-418/etc/jvm.config
}


nodeid

# Update the Presto config.properties file with values for the coordinator and
# workers. Only if the following 3 parameters are set.
[[ -n "${HTTP_SERVER_PORT}" && -n "${TRINO_MAX_MEMORY}" && -n "${TRINO_MAX_MEMORY_PER_NODE}" ]] && \
if [[ -z "${COORDINATOR}" ]]; then coordinator_config; else worker_config; fi

# Update the JVM configuration for any node. Only if the PRESTO_JVM_HEAP_SIZE
# parameter is set.
[[ -n "${TRINO_JVM_HEAP_SIZE}" ]] && jvm_config


exec $@

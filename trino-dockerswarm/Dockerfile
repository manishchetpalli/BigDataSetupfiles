FROM registry.hub.docker.com/library/ubuntu:20.04

ENV HADOOP_CONF_DIR=/etc/hadoop/conf
ENV JAVA_HOME=/opt/java
ENV PATH=$PATH:$JAVA_HOME/bin
ENV http_proxy=
ENV https_proxy=
ENV no_proxy=


COPY ./trino-server-418 /usr/lib/trino-server-418
COPY ./entrypoint.sh /opt/entrypoint.sh
COPY ./run-trino.sh /opt/run-trino.sh
COPY ./health-check.sh /opt/health-check.sh
COPY ./myCA.crt /usr/local/share/ca-certificates/myCA.crt

RUN apt-get -qq update \
        && apt-get install uuid-runtime wget curl krb5-kdc krb5-config krb5-user python-dev -y \
        && mkdir -p /etc/trino /data/trino \
        && groupadd trino --gid 1000 \
        && useradd trino --uid 1000 --gid 1000 --create-home \
        &&  chown -R trino:trino /usr/lib/trino-server-418 /etc/trino /data/trino \
        && apt-get -qq -y autoremove \
        && apt-get autoclean \
        && rm -rf /var/lib/apt/lists/* /var/log/dpkg.log


ENV http_proxy=
ENV https_proxy=
ENV no_proxy=

EXPOSE 8084

USER trino:trino
ENTRYPOINT [ "/opt/entrypoint.sh" ]
CMD ["/opt/run-trino.sh"]

HEALTHCHECK --interval=10s --timeout=5s --start-period=10s \
  CMD /opt/health-check.sh


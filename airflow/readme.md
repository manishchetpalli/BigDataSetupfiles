# Apache Airflow Setup (On-Premise)

We will be using MySQL as backend database, RabbitMQ as message broker, Celery as task queuing system and Flower UI for monitoring celery cluster.

- **Operating System:** RHEL/CENTOS/UBUNTU
- **Python Version:** 3.8  
- **Backend Database:** MySQL  
- **Executor:** Celery as task queing system
- **Celery Backend (Broker):** RabbitMQ as message broker
- **Flower UI:** To monitor celery cluster.

> **Note:** All commands are executed from the home directory (`~/`).

---

More details and step-by-step instructions will follow in the next sections.
Make sure you install the following packages before starting installation

!!!-  "Required Python Packages"
    ```
    yum install libmysqlclient-dev python3 python3-dev build-essential libssl-dev libffi-dev libxml2-dev libxslt1-dev zlib1g-dev freetds-bin krb5-user ldap-utils libsasl2-2 libsasl2-modules libssl1.1 locales lsb-release sasl2-bin sqlite3 unixodbc
    ```

!!!-  "Database Setup"
    ```
    yum -y install @mysql

    # Start MySQL service and create symlink
    systemctl status mysqld
    systemctl start mysqld
    systemctl enable --now mysqld
    systemctl status mysqld

    # Change root password and configure MySQL
    mysql_secure_installation  # {password:-root}

    # Create airflow user and grant privileges
    mysql -u"root" -p"root"

    # Inside MySQL prompt
    CREATE DATABASE airflow;
    CREATE USER 'airflowuser'@'%' IDENTIFIED BY 'airflowuser';
    GRANT ALL PRIVILEGES ON airflow.* TO 'airflowuser'@'%';
    CREATE USER 'airflowuser'@'localhost' IDENTIFIED BY 'airflowuser';
    GRANT ALL PRIVILEGES ON airflow.* TO 'airflowuser'@'localhost';
    FLUSH PRIVILEGES;
    ```

!!!-  "Rabbitmq Setup"

    ```
    # Extract the RabbitMQ setup file
    Download the setup file before installing rabbitmq install erlang package first

    # Download the rabbitmq.conf file
    wget https://github.com/manish-chet/BigDataSetupfiles/tree/main/airflow
    copy the file in rabbitmq/etc/conf directory
    edit the rabbitmq.conf with IP and details

    #Set environment variables in rc
    export RABBITMQ_LOG_BASE=/data/rabbitmq/rabbitmq/logs
    export PATH=$PATH:/data/rabbitmq/rabbitmq/rabbitmq_server-3.13.7/sbin

    #Enable rabbitmq plugins
    rabbitmq-plugins enable rabbitmq_management  

    #Shutdown rabbitmq
    sbin/rabbitmqctl shutdown

    #Rabbitmq status
    rabbitmqctl status

    #Start rabbitmq in detached mdoe
    rabbitmq-server -detached

    #Create user
    rabbitmqctl add_user airflow airflow
    rabbitmqctl set_user_tags airflow administrator
    rabbitmqctl set_permissions -p / airflow ".*" ".*" ".*"
    rabbitmqctl eval 'application:set_env(rabbit, consumer_timeout, undefined).'
    ```

!!!-  "Airflow configuration"

    ```
    # Create virtualenv 
    pip install virtualenv
    python3.8 -m pip install --upgrade pip
    virtualenv -p python3.8 airflow_env
    source airflow_env/bin/activate

    # Install necessary packages
    pip install "apache-airflow==2.10.2" --constraint constraints.txt
    pip install 'apache-airflow[mysql]'
    pip install 'apache-airflow[celery]'
    pip install 'apache-airflow[rabbitmq]'
    pip install 'apache-airflow[crypto]'
    pip install 'apache-airflow[password]'

    # Check airflow version
    airflow version

    # Download the airflow.cfg and edit the hostname and IP details
    wget https://github.com/manish-chet/BigDataSetupfiles/tree/main/airflow


    # Create users
    airflow create_user -r Admin -u airflow -e your_email@domain.com -f Airflow -l Admin -p password
    airflow users create -r Admin -u manishkumar2.c -f manishkumar -l chetpalli -e manishkumar2.c@email.com -p manish123

    #Initialize DB
    airflow db migrate

    #Initialize Webserver
    airflow webserver -D

    #Initialize Scheduler
    airflow scheduler -D

    #Initialize Flower
    airflow celery worker -D

    #Initialize Celery
    airflow celery flower -D

    #Initialize Trigger
    airflow triggerer -D
    ```

!!!-  "Worker Node Addition"

    ```
    # Create virtualenv 
    pip install virtualenv
    python3.8 -m pip install --upgrade pip
    virtualenv -p python3.8 airflow_env
    source airflow_env/bin/activate

    # Install necessary packages
    pip install "apache-airflow==2.10.2" --constraint constraints.txt
    pip install 'apache-airflow[mysql]'
    pip install 'apache-airflow[celery]'
    pip install 'apache-airflow[rabbitmq]'
    pip install 'apache-airflow[crypto]'
    pip install 'apache-airflow[password]'

    # Check airflow version
    airflow version

    # Download the airflow.cfg and edit the hostname and IP details
    wget https://github.com/manish-chet/BigDataSetupfiles/tree/main/airflow


    After this you need to go to master node and run below MySQL command so that user from worker node can connect to the database on master node.
    # replace hostname here with your remote worker ip address
    sudo mysql -e "CREATE USER 'airflow'@'hostname' IDENTIFIED BY 'password'; GRANT ALL PRIVILEGES ON airflowdb.* TO 'airflow'@'hostname';"

    # Initialize the airflow database on worker node 
    airflow initdb

    # Start the worker
    airflow celery worker -D

    You should be able to see the worker node coming up on Flower interface at YOUR_MASTER_IP_ADDRESS:5555
    ```

!!!-  "Airflow DB Cleanup DAG"
    ```
    wget https://github.com/manish-chet/BigDataSetupfiles/tree/main/airflow
    ```


!!!-  "Airflow Log Cleanup DAG"
    ```
    wget https://github.com/manish-chet/BigDataSetupfiles/tree/main/airflow
    ```

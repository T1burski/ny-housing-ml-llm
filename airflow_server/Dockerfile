# Dockerfile that builds the image that will be used to run Airflow

FROM apache/airflow:2.10.2

USER airflow

ENV AIRFLOW_HOME=/opt/airflow/airflow_server

WORKDIR /opt/airflow/airflow_server

COPY requirements.txt /opt/airflow/airflow_server/requirements.txt

RUN pip install --upgrade pip
RUN pip install apache-airflow==${AIRFLOW_VERSION} -r requirements.txt

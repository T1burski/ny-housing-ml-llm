# Definition of the DAG that runs the whole ETL & Training Pipeline

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import timedelta
from etl_train_pipeline_modules.pipeline_etl import load_csv_to_postgresql
from etl_train_pipeline_modules.pipeline_train import train_and_version_mlflow
from pendulum import today

defaultArguments = {
    "owner": "Artur Tiburski",
    "start_date": today("America/Sao_Paulo"),
    "depends_on_past": True
}

dag = DAG(
    "NY_Pipeline_ETL_and_ML_Training",
    default_args=defaultArguments,
    schedule_interval="0 0 * * *",
    catchup=False,
    max_active_runs=1,
    description="Executes ETL and mlflow training processes"
)

dag_pipeline_etl = PythonOperator(
    
    # =============================
    # Step that runs the ETL process  
    # =============================

    task_id="step_create_original_table",
    python_callable=load_csv_to_postgresql,
    dag=dag
)

dag_pipeline_mlflow = PythonOperator(

    # =============================
    # Step that runs training and
    # model versioning in mlflow  
    # =============================

    task_id="step_train_version_mlflow",
    python_callable=train_and_version_mlflow,
    dag=dag
)

# Defining steps execution logic

dag_pipeline_etl >> dag_pipeline_mlflow
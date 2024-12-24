# Importa o módulo DAG do Airflow para criar e gerenciar DAGs (fluxos de trabalho)
from airflow import DAG

from airflow.operators.python import PythonOperator

from datetime import timedelta

from airflow_server.dags.etl_train_pipeline_modules.pipeline_etl import load_csv_to_postgresql

from airflow_server.dags.etl_train_pipeline_modules.pipeline_train import train_and_version_mlflow

from pendulum import today

defaultArguments = {
    "owner": "Artur Tiburski",
    "start_date": today("America/Sao_Paulo"),
    "depends_on_past": True,
    "wait_for_downstream": True
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
    task_id="step_create_original_table",
    python_callable=load_csv_to_postgresql,
    dag=dag
)

dag_pipeline_mlflow = PythonOperator(
    task_id="step_train_version_mlflow",
    python_callable=train_and_version_mlflow,
    dag=dag
)

# # Define a tarefa para carregar dados CSV, usando a função 'dsa_insere_dados_csv'
# dsa_tarefa_carrega_csv = PythonOperator(
#     task_id="tarefa_carrega_csv",          # Identificador único da tarefa
#     python_callable=dsa_insere_dados_csv,  # Função Python a ser executada
#     dag=dag                                # DAG a qual a tarefa pertence
# )

# # Define a tarefa para criar o índice, usando a função 'dsa_cria_indice'
# dsa_tarefa_cria_indice = PythonOperator(
#     task_id="tarefa_cria_indice",     # Identificador único da tarefa
#     python_callable=dsa_cria_indice,  # Função Python a ser executada
#     dag=dag                           # DAG a qual a tarefa pertence
# )

dag_pipeline_etl >> dag_pipeline_mlflow #>> dsa_tarefa_carrega_csv >> dsa_tarefa_cria_indice





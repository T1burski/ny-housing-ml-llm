# Projeto 4 - Pipeline de MLOps Para Operacionalização e Monitoramento de IA Generativa com LLM e RAG

# Importa o módulo DAG do Airflow para criar e gerenciar DAGs (fluxos de trabalho)
from airflow import DAG

# Importa o operador PythonOperator para executar funções Python como tarefas
from airflow.operators.python import PythonOperator

# Importa timedelta para definir intervalos de tempo para tentativas de reexecução
from datetime import timedelta

# Importa funções personalizadas para manipulação de dados do módulo 'modulodsadados'
from etl_train_pipeline_modules.dsa_carrega_dados import load_csv_to_postgresql

from pendulum import today

# Define argumentos padrão para as tarefas do DAG
defaultArguments = {
    "owner": "Artur Tiburski",
    "start_date": today("America/Sao_Paulo"),
    "depends_on_past": True,
    "wait_for_downstream": True
}

# Cria a DAG com o nome 'DSA_Carrega_Dados_LLM'
dag = DAG(
    "NY_Pipeline_ETL_and_ML_Training",
    default_args=defaultArguments,
    schedule_interval="0 0 * * *",
    catchup=False,
    max_active_runs=1,
    description="Executes ETL and mlflow training processes"
)

# Define a tarefa para criar a tabela, usando a função 'dsa_cria_tabela' do módulo
dsa_tarefa_cria_tabela = PythonOperator(
    task_id="step_create_original_table",
    python_callable=load_csv_to_postgresql,
    dag=dag
)

# # Define a tarefa para carregar dados JSON, usando a função 'dsa_insere_dados_json'
# dsa_tarefa_carrega_json = PythonOperator(
#     task_id="tarefa_carrega_json",          # Identificador único da tarefa
#     python_callable=dsa_insere_dados_json,  # Função Python a ser executada
#     dag=dag                                 # DAG a qual a tarefa pertence
# )

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

# Define a ordem de execução das tarefas na DAG
# Primeiro cria a tabela, depois carrega os dados JSON, seguido pelos dados CSV, e por último cria o índice no ElasticSearch
# Isso define a estratégia de RAG
dsa_tarefa_cria_tabela #>> dsa_tarefa_carrega_json >> dsa_tarefa_carrega_csv >> dsa_tarefa_cria_indice





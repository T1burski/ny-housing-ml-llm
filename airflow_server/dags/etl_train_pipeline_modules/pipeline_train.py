# Importa a função postgre_connection para estabelecer conexão com o banco de dados PostgreSQL
import mlflow
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
from etl_train_pipeline_modules.auxiliary_functions import extract_data_postgresql, create_scatter_plot, train_and_optimize_model, evaluate_model

def train_and_version_mlflow():

    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment("regression_models_ny_housing")

    target = 'price'
    features = ["bath", "beds", "propertysqft", "latitude", "longitude"]

    all_columns = features
    all_columns.append(target)

    select_query = f"""
        SELECT
            BROKERTITLE,
            TYPE,
            PRICE,
            BEDS,
            BATH,
            PROPERTYSQFT,
            ADDRESS,
            STATE,
            MAIN_ADDRESS,
            ADMINISTRATIVE_AREA_LEVEL_2,
            LOCALITY,
            SUBLOCALITY,
            STREET_NAME,
            LONG_NAME,
            FORMATTED_ADDRESS,
            LATITUDE,
            LONGITUDE
        FROM ny_datasets.original_data
    """

    df = extract_data_postgresql(select_query)

    for c in all_columns:
        df[c] = pd.to_numeric(df[c], errors='coerce')

    df = df.loc[df[target] <= np.percentile(df[target], 99)]

    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.1, random_state=42
    )

    param_grids = {
        "xgboost": {
            "n_estimators": [100, 200, 300],
            "learning_rate": [0.01, 0.1, 0.3]
        },
        "random_forest": {
            "n_estimators": [100, 200, 300],
            "max_depth": [10, 20, 30]
        }
    }
    
    best_mse = float('inf')
    best_model_info = None
    
    for model_type in ["xgboost", "random_forest"]:
        with mlflow.start_run() as run:

            mlflow.log_param("model_type", model_type)
            
            model, best_params = train_and_optimize_model(
                model_type,
                X_train,
                y_train,
                param_grids[model_type]
            )
            
            for param_name, param_value in best_params.items():
                mlflow.log_param(param_name, param_value)
            
            eval_results = evaluate_model(model, X_test, y_test)
            
            mlflow.log_metric("mse", eval_results["mse"])
            mlflow.log_metric("mae", eval_results["mae"])
            
            fig = create_scatter_plot(y_test, eval_results["y_pred"], model_type)
            mlflow.log_figure(fig, f"{model_type}_scatter_plot.png")
            plt.close(fig)
            
            if model_type == "xgboost":
                mlflow.xgboost.log_model(model, "model")
            else:
                mlflow.sklearn.log_model(model, "model")
            
            if eval_results["mse"] < best_mse:
                best_mse = eval_results["mse"]
                best_model_info = {
                    "run_id": run.info.run_id,
                    "model_type": model_type,
                    "mse": eval_results["mse"]
                }
    
    client = mlflow.tracking.MlflowClient()
    
    try:
        production_model = mlflow.pyfunc.load_model("models:/regression_model/Production")
        y_pred_prod = production_model.predict(X_test)
        prod_mse = mean_squared_error(y_test, y_pred_prod)
    except:
        prod_mse = float('inf')
    
    if best_mse < prod_mse:
        print(f"New best model ({best_model_info['model_type']}) "
              f"outperforms production model. Updating production deployment...")
        
        model_uri = f"runs:/{best_model_info['run_id']}/model"
        try:
            client.create_registered_model("regression_model")
        except:
            pass
        
        model_version = mlflow.register_model(model_uri, "regression_model")
        
        client.transition_model_version_stage(
            name="regression_model",
            version=model_version.version,
            stage="Production"
        )
        
        for model_version in client.search_model_versions("name='regression_model'"):
            if model_version.current_stage == "Production" and \
               model_version.version != model_version.version:
                client.transition_model_version_stage(
                    name="regression_model",
                    version=model_version.version,
                    stage="Archived"
                )
        
        print("Production model updated successfully!")
    else:
        print("Current production model performs better. No updates needed.")
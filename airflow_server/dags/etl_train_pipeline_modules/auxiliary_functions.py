
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
import xgboost as xgb


def extract_data_postgresql(select_query):

    try:
        url = URL.create(
            drivername="postgresql",
            username=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME")
        )

        # Create engine
        engine = create_engine(url)

        with engine.begin() as connection:
            result = connection.execute(text(select_query))
            
            rows = result.fetchall()
            
            df = pd.DataFrame(rows, columns=result.keys())

        engine.dispose()
        print("Database connection closed.")

        return df
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
    finally:
        engine.dispose()
        print("Database connection closed.")

def create_scatter_plot(y_true, y_pred, model_name):


    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(y_true, y_pred, alpha=0.5)
    ax.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
    ax.set_xlabel('Actual Values')
    ax.set_ylabel('Predicted Values')
    ax.set_title(f'{model_name}: Actual vs Predicted Values')
    return fig

def train_and_optimize_model(model_type, X_train, y_train, param_grid):


    if model_type == "xgboost":
        model = xgb.XGBRegressor(random_state=42)
    else:
        model = RandomForestRegressor(random_state=42)
    
    grid_search = GridSearchCV(
        model,
        param_grid,
        cv=3,
        scoring='neg_mean_squared_error',
        n_jobs=-1
    )
    
    grid_search.fit(X_train, y_train)

    return grid_search.best_estimator_, grid_search.best_params_


def evaluate_model(model, X_test, y_test):

    y_pred = model.predict(X_test)

    return {
        "mse": mean_squared_error(y_test, y_pred),
        "mae": mean_absolute_error(y_test, y_pred),
        "y_pred": y_pred
    }
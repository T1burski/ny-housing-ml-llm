# New York House Pricing: ML Web App with LLM & RAG system to create AI Reports


![image](https://github.com/user-attachments/assets/36829338-e211-403b-a630-21274e601813)

### 1) Project's Goal:
This project aims to build a system provides a Web App (front-end) in which the user can input the desired information regarding the features of the house they are willing to buy in New York. As an output, the predicted house price is shown, giving the user an insight of how much is the cost of the house they desire. Along with the predicted house price, is USD, a Report is also outputted for the user explaining and analyzing how the predicted price is compared with other houses of the same characteristics (location, area in sqft and others), providing more information for the user's decision making. This report is built by an AI.

![image](https://github.com/user-attachments/assets/de8d0c61-57ba-4a17-b951-f1917aae9123)


### 2) Strategy and Tools Used:
In order to guarantee a robust project, every module and sub-system was containerized using Docker, using a shared network through Docker Compose. The simplified diagram in the start of this readme file represents the architecture chosen. In practice, four containers were built and connected to each other:

### airflow:
Provides the airflow webserver, scheduler and other functionalities to orchestrate ETL and Model Training and Versioning pipelines. Image was built on customized Dockerfile.

### mlflow:
Provides the mlflow server, making model storage and versioning possible. Available image on Docker Hub was used (version can be checked on the docker-compose file).

### app:
Provides the streamlit webapp, building the front-end and the connection between the system and the LLM API using HuggingFace. Image was built on customized Dockerfile.

### fast_api:
Provides the REST API ready to be used for predictions, always using the model in Production available in mlflow. Image was built on customized Dockerfile.

In order to store data used to train the models and the data returned from every API call (features chosen, predicted price, user feedback), a simple PostgreSQL database was built in the cloud using Render. The ETL process can be checked out in the airflow_server\dags\etl_train_pipeline_modules\pipeline_etl.py script.

Example of the data generated and stored in the database regarding the users' inputs, predictions and feedbacks:

![image](https://github.com/user-attachments/assets/90ba2f76-39e3-4d12-be39-ebff968ba9c1)

Modularization was applied to make the project organized, facilitating maintenance.


### 3) Prediction Models and Data Understanding:
A simplified EDA was used and can be checked out in the eda.ipynb file. Since the main objective of this project was to build the system as a whole and focus on the LLM-RAG application, a simpler approach was used in this feature engineering and EDA process.

As for the ML approach, two models were trained and compared everytime the training pipeline was triggered: Random Forest Regressor and XGBoost Regressor. The model training, comparison and versioning can be checked out in the airflow_server\dags\etl_train_pipeline_modules\pipeline_train.py script. Again, for simplicity reasons, the hyperparameter optimization used only two hyperparameters: n_estimators and learning_rate.

The error metric used to compare models was Mean Square Error (MSE).


### 4) AI: The LLM and RAG Approaches:
The LLM used was the Mistral AI's Mistral-7B-Instruct-v0.2.

The LLM's access is made using HugginFace's API, along with its application with Langchain to build the prompts and apply (in a simple way) the RAG system. The RAG system fetches in the original database characteristics of the houses that are in the same location of the one selected by the user, providing a Report that compares the predicted price with data available in the database.

![image](https://github.com/user-attachments/assets/c85fa3d1-fbbe-40ce-8ecc-d5b5ee2d2bc4)

After showing the user the report, they can give a feedback whether the report was satisfactory (Yes or No answers).


### 5) The Web App (Front-End):
The Web App was built using Streamlit.

When the user accesses the page, they see the following:

### -> Here, they input the house's features. When they are all filled correctly, the user can finally call the prediction by clicking Submit.
![image](https://github.com/user-attachments/assets/06c79074-f74f-496b-9950-64d013620fa7)

### -> After clicking Submit, the predicted price is shown and, after 1 or 2 seconds, the AI Report, along with the feedback options for the user to choose.
![image](https://github.com/user-attachments/assets/13633066-aff3-467b-b35b-459a980b1034)

### -> After the user chooses a feedback option, the chosen feedback is displayed, along with a message telling the user to refresh the page if they want to make new predictions.
![image](https://github.com/user-attachments/assets/0277f274-2336-42e1-9f01-53bc1faba100)


### 6) Conclusions and Running the Project:

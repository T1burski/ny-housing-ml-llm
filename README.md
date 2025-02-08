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

In order to store data used to train the models and the data returned from every API call (features chosen, predicted price, user feedback), a simple PostgreSQL database was built in the cloud using Render.

Modularization was applied to make the project organized, facilitating maintenance.

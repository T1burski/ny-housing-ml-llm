from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import HuggingFaceHub
from app_functions.database_functions import extract_data_postgresql


def llm_and_rag_application(pred_price, propsqft, sublocality):

    try:

        select_query = f"""
        SELECT
            SUBLOCALITY,
            percentile_cont(0.5) WITHIN GROUP (
            ORDER BY PRICE
            ) AS MED_PRICE,
            percentile_cont(0.5) WITHIN GROUP (
            ORDER BY PROPERTYSQFT
            ) AS MED_PROPERTYSQFT,
            COUNT(*) AS N_HOUSES
        FROM ny_datasets.original_data
        WHERE SUBLOCALITY = '{sublocality}'
        GROUP BY SUBLOCALITY
        """

        df = extract_data_postgresql(select_query)

        med_price = float(df["med_price"].values[0])
        med_propertysqft = float(df["med_propertysqft"].values[0])
        n_houses = int(df["n_houses"].values[0])
    
    except Exception as e:
        print(f"An error occurred during data extraction for RAG: {str(e)}")

    try:
    
        output_parser = StrOutputParser()
        
        llm = HuggingFaceHub(
            repo_id="mistralai/Mistral-7B-Instruct-v0.2",
            model_kwargs={"temperature": 0.7, "max_length": 512}
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are an expert in the New York housing market. You are receiving data that represent the predicted house price based on user inputs along with data that represent price, poperty square foot and number of houses in the sublocality chosen by the user. Analyse these data and build a small, insightful and direct report comparing the predicted price, property square foot and the ratio between them with the data observed in the sublocality. Add more comparisons and analysis as you see fit. Write in english and with simple language."),
                ("user", "question: {question}")
            ]
        )

        chain = prompt | llm | output_parser

        data_input = f"Predicted house price {pred_price} Property area in square foots selected by the user {propsqft} Sublocality (region) of the house selected by the user {sublocality} Median price of the houses in the sublocality (region) selected by the user {med_price} Median property square foot of the houses in the sublocality (region) selected by the user {med_propertysqft} Total number of houses in the sublocality selected by the user {n_houses}."
        
        response = chain.invoke({'question': data_input})

        return response, med_price, med_propertysqft, n_houses
    
    except Exception as e:
        print(f"An error occurred during LLM abd RAG application: {str(e)}")
        return response, med_price, med_propertysqft, n_houses


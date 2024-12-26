from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import HuggingFaceHub
from app_functions.database_functions import extract_data_postgresql
import os


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
            COUNT(*) AS N_HOUSES,
        FROM ny_datasets.original_data
        WHERE SUBLOCALITY = {sublocality}
        GROUP BY SUBLOCALITY
        """
        df = extract_data_postgresql(select_query)
    
    except Exception as e:
        print(f"An error occurred during data extraction for RAG: {str(e)}")

    try:
    
        output_parser = StrOutputParser()
        
        llm = HuggingFaceHub(
            repo_id="meta-llama/Llama-2-7b-chat-hf",
            model_kwargs={"temperature": 0.7, "max_length": 512}
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "Você é um analista especializado. Analise os dados e forneça feedback em português do Brasil sobre os padrões de vendas dos produtos."),
                ("user", "question: {question}")
            ]
        )

        chain = prompt | llm | output_parser

        consulta = f"Nome do Cliente {nome_cliente} Faixa Etária do Cliente {faixa_etaria} Cidade do Cliente {cidade_cliente} Nome do Produto {nome_produto} Marca do Produto {marca_produto} Categoria do Produto {categoria_produto} Total de Venda ${total_venda:.2f} Quantidade Vendida {total_quantidade_vendida}."
        
        response = chain.invoke({'question': consulta})

        return response
    
    except Exception as e:
        print(f"An error occurred during LLM abd RAG application: {str(e)}")


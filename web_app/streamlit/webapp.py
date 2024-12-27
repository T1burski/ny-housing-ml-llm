import streamlit as st
from app_functions.database_functions import load_data_postgresql, extract_data_postgresql
from app_functions.llm_functions import llm_and_rag_application
import requests
from datetime import datetime

def main():
    
    st.set_page_config(page_title="NY Housing App", layout="wide")

    st.sidebar.title("New York Housing Prices")
    st.sidebar.subheader("Prediction of House Prices")
    st.sidebar.write("Find out the price of the house you desire in New York and also get an AI made report on the results!")
    st.sidebar.markdown("---")

    if 'feedbackSubmitted' not in st.session_state:
        st.session_state.feedbackSubmitted = False
    if 'predicted_price' not in st.session_state:
        st.session_state.predicted_price = None
    if 'ai_response' not in st.session_state:
        st.session_state.ai_response = None
    if 'user_feedback' not in st.session_state:
        st.session_state.user_feedback = None

    @st.cache_data
    def query_sublocations():
        select_query = f"""
        SELECT DISTINCT
            SUBLOCALITY
        FROM ny_datasets.original_data
        """
        sublocality_options = extract_data_postgresql(select_query)

        return sublocality_options
    
    sublocality_options = query_sublocations()
    sublocality_options_tuple = tuple(sublocality_options['sublocality'])

    with st.container(border=True):
        st.write("Area for user to input data")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.write("Inform the house size (area in square-feet) and the region:")
            prop_sqft = st.number_input("House's size (in sqft)", min_value=0.0, max_value=65535.0, step=None)
            st.divider()
            sublocality = st.selectbox("Region (sublocality) of the house", sublocality_options_tuple)

        with col2:
            st.write("Inform the number of bathrooms and bedrooms inside the house:")
            bath = st.number_input("Number of bathrooms", min_value=0.0, max_value=11.0, step=None)
            st.divider()
            beds = st.number_input("Number of bedrooms", min_value=0.0, max_value=32.0, step=None)

        with col3:
            st.write("Inform the approximate latitude and longitude of the house")
            lat = st.number_input("House's Latitude", format="%.6f", step=None)
            st.divider()
            lon = st.number_input("House's Longitude", format="%.6f", step=None)
        
        with col4:
            # Check if all fields are filled
            if prop_sqft > 0 and bath > 0 and beds > 0 and lat != 0 and lon != 0:
                button_label = "Submit"
                button_disabled = False
            else:
                button_label = "Fill all fields correctly"
                button_disabled = True
            
            # Button: Enable or disable based on condition
            if st.button(button_label, disabled=button_disabled):
                if not button_disabled:

                    payload = {
                        "bath": float(bath),
                        "beds": float(beds),
                        "propertysqft": float(prop_sqft),
                        "latitude": float(lat),
                        "longitude": float(lon)
                    }

                    response = requests.post("http://fast_api:3000/predict", json = payload).json()
                    st.session_state.predicted_price = response["predicted_price"]

                    st.divider()

                    st.write("Predicted House Price:")
                    st.write(f"{round(st.session_state.predicted_price, 2)} USD")

                    st.write(sublocality)
                else:
                    st.warning("Please fill all fields before submitting.")
    

    if st.session_state.predicted_price is not None:
    
        st.markdown("---")

        with st.container(border=True):
            st.write("AI Report:")

            try:
                st.session_state.ai_response, med_price, med_propertysqft, n_houses = llm_and_rag_application(st.session_state.predicted_price, float(prop_sqft), sublocality)

                st.write({st.session_state.ai_response})
            except Exception as e:
                st.error(f"An error occurred when generating AI response: {e}")
            
            
            if st.session_state.ai_response is not None:
            
                if not st.session_state.feedbackSubmitted:
                    st.write("Did the AI report provide satisfatory insights?")
                    feedback_col1, feedback_col2 = st.columns(2)
                    with feedback_col1:
                        if st.button("Yes"):
                            
                            st.session_state.feedbackSubmitted = True
                            st.session_state.user_feedback = "Yes"
                            st.success("Positive Feedback")
                    
                    with feedback_col2:
                        if st.button("No"):
                            
                            st.session_state.feedbackSubmitted = True
                            st.session_state.user_feedback = "No"
                            st.success("Negative Feedback")
                    
                if st.session_state.user_feedback is not None:
                    data_dict = {
                        "sublocality": sublocality,
                        "pred_price": st.session_state.predicted_price,
                        "beds": beds,
                        "bath": bath,
                        "propertysqft": prop_sqft,
                        "latitude": lat,
                        "longitude": lon,
                        "med_price": med_price,
                        "med_propertysqft": med_propertysqft,
                        "n_houses": n_houses,
                        "review": st.session_state.user_feedback,
                        "created_at": datetime.today().date().strftime("%Y-%m-%d")
                    }

                    try:
                        load_data_postgresql([data_dict])
                        st.write("Thank you!")

                    except Exception as e:
                        print(f"An error occurred when loading the data into the database")

    if st.button("Click here to make new predictions"):

        st.session_state.predicted_price = None
        st.session_state.ai_response = None
        st.session_state.user_feedback = None
        st.session_state.feedbackSubmitted = False

        st.experimental_rerun()


if __name__ == '__main__':
    main()
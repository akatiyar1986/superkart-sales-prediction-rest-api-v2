# Import necessary libraries
import streamlit as st
import requests
import pandas as pd
import json

# Define the backend API URL
# For local testing, use:
BACKEND_URL = "http://localhost:5000"
# For deployed Hugging Face Space, replace with your deployed backend URL:
# BACKEND_URL = "https://YOUR_BACKEND_SPACE_ID.hf.space"


st.set_page_config(page_title="SuperKart Sales Predictor", layout="wide")

st.title("🛒 SuperKart Product Store Sales Total Predictor")
st.markdown("Use this application to predict the total sales of a product in a store.")

# --- Single Prediction Section ---
st.header("Single Product Sales Prediction")

with st.form("single_prediction_form"):
    st.subheader("Enter Product and Store Details:")

    # Input fields for numerical features
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        product_weight = st.number_input("Product Weight (lbs)", min_value=4.0, max_value=22.0, value=12.0, step=0.1)
    with col2:
        product_allocated_area = st.number_input("Product Allocated Area (ratio)", min_value=0.004, max_value=0.298, value=0.05, step=0.001, format="%.3f")
    with col3:
        product_mrp = st.number_input("Product MRP ($)", min_value=31.0, max_value=266.0, value=150.0, step=1.0)
    with col4:
        store_establishment_year = st.number_input("Store Establishment Year", min_value=1987, max_value=2009, value=1998, step=1)

    # Input fields for categorical features (using selectbox based on EDA unique values)
    col5, col6, col7 = st.columns(3)
    with col5:
        product_sugar_content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
    with col6:
        product_type = st.selectbox("Product Type", [
            "Fruits and Vegetables", "Snack Foods", "Frozen Foods", "Dairy", "Household",
            "Baking Goods", "Canned", "Health and Hygiene", "Meat", "Soft Drinks",
            "Breads", "Hard Drinks", "Others", "Starchy Foods", "Breakfast", "Seafood"
        ])
    with col7:
        store_id = st.selectbox("Store ID", ["OUT004", "OUT001", "OUT003", "OUT002"])

    col8, col9, col10 = st.columns(3)
    with col8:
        store_size = st.selectbox("Store Size", ["Medium", "High", "Small"])
    with col9:
        store_location_city_type = st.selectbox("Store Location City Type", ["Tier 2", "Tier 1", "Tier 3"])
    with col10:
        store_type = st.selectbox("Store Type", ["Supermarket Type2", "Supermarket Type1", "Departmental Store", "Food Mart"])

    predict_button = st.form_submit_button("Predict Sales")

    if predict_button:
        # Prepare data for API request
        data = {
            "product_weight": float(product_weight),
            "product_allocated_area": float(product_allocated_area),
            "product_mrp": float(product_mrp),
            "store_establishment_year": int(store_establishment_year),
            "product_sugar_content": product_sugar_content,
            "product_type": product_type,
            "store_id": store_id,
            "store_size": store_size,
            "store_location_city_type": store_location_city_type,
            "store_type": store_type
        }

        try:
            response = requests.post(f"{BACKEND_URL}/v1/totalsales", json=data)
            if response.status_code == 200:
                prediction_result = response.json()
                st.success(f"**Predicted Product Store Sales Total:** {prediction_result['Predicted Product Store Sales Total ($)']:.2f} $")
            else:
                st.error(f"Error from backend: {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the backend API. Please ensure it is running.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

st.markdown("---")

# --- Batch Prediction Section ---
st.header("Batch Product Sales Prediction (Upload CSV)")

uploaded_file = st.file_uploader("Upload a CSV file for batch predictions", type=["csv"])

if uploaded_file is not None:
    st.write("File uploaded successfully!")
    st.subheader("Preview of your uploaded data:")
    batch_df = pd.read_csv(uploaded_file)
    st.dataframe(batch_df.head())

    batch_predict_button = st.button("Predict Sales for Batch")

    if batch_predict_button:
        # To send a file in a POST request, use 'files' parameter in requests.post
        # The 'files' parameter expects a dictionary where the key is the field name
        # (e.g., 'file') and the value is a tuple: (filename, file_object, content_type)
        files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'text/csv')}

        try:
            response = requests.post(f"{BACKEND_URL}/v1/batchsales", files=files)
            if response.status_code == 200:
                batch_prediction_results = response.json()
                st.subheader("Batch Predictions:")
                # Display predictions in a DataFrame
                # Assuming the backend returns a dict like {'Index': prediction_value}
                # or a list of predictions if no index is explicitly passed.
                # The backend was modified to return a list of predictions.
                predictions_df = pd.DataFrame(batch_prediction_results['Batch Predicted Product Store Sales Total ($)'], columns=["Predicted Product Store Sales Total ($)"])
                st.dataframe(predictions_df)
            else:
                st.error(f"Error from backend: {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the backend API. Please ensure it is running.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

st.markdown("---")
st.caption("Note: For local testing, ensure your Flask backend is running on http://localhost:5000.")
st.caption("If deployed on Hugging Face, update the `BACKEND_URL` variable in the code.")

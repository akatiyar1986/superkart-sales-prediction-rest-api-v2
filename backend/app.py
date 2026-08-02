# Import necessary libraries
import numpy as np
import joblib  # For loading the serialized model
import pandas as pd  # For data manipulation
from flask import Flask, request, jsonify  # For creating the Flask API

# Initialize the Flask application
product_store_sales_total_prediction_api = Flask("product_store_sales_total_prediction_model")

# Load the trained machine learning model
# Assuming the model is saved at "deployment_files/product_store_sales_total_prediction_model_v1_0.joblib"
#model = joblib.load("deployment_files/product_store_sales_total_prediction_model_v1_0.joblib")
model = joblib.load("product_store_sales_total_prediction_model_v1_0.joblib")

# Define the feature names in the order expected by the model
# This order is crucial because the ColumnTransformer in the pipeline expects specific column order for preprocessing
feature_names = [
    'Product_Weight',
    'Product_Allocated_Area',
    'Product_MRP',
    'Store_Establishment_Year',
    'Product_Sugar_Content',
    'Product_Type',
    'Store_Id',
    'Store_Size',
    'Store_Location_City_Type',
    'Store_Type'
]

# Define a route for the home page (GET request)
@product_store_sales_total_prediction_api.get('/')
def home():
    """
    This function handles GET requests to the root URL ('/') of the API.
    It returns a simple welcome message.
    """
    return "Welcome to the SuperKart Product Store Sales Total Prediction API!"

# Define an endpoint for single prediction (POST request)
@product_store_sales_total_prediction_api.post('/v1/totalsales')
def product_store_sales_total_prediction():
    """
    This function handles POST requests to the '/v1/totalsales' endpoint.
    It expects a JSON payload containing product details and returns
    the predicted total sales as a JSON response.

    Expected JSON format:
    {
        "product_weight": 12.66,
        "product_allocated_area": 0.027,
        "product_mrp": 117.08,
        "store_establishment_year": 2009,
        "product_sugar_content": "Low Sugar",
        "product_type": "Frozen Foods",
        "store_id": "OUT004",
        "store_size": "Medium",
        "store_location_city_type": "Tier 2",
        "store_type": "Supermarket Type2"
    }
    """
    # Get the JSON data from the request body
    product_info = request.get_json()

    # Create a list of values in the correct order based on feature_names
    # Ensure all expected keys are present in the incoming JSON
    try:
        input_values = [
            product_info['product_weight'],
            product_info['product_allocated_area'],
            product_info['product_mrp'],
            product_info['store_establishment_year'],
            product_info['product_sugar_content'],
            product_info['product_type'],
            product_info['store_id'],
            product_info['store_size'],
            product_info['store_location_city_type'],
            product_info['store_type']
        ]
    except KeyError as e:
        return jsonify({"error": f"Missing expected key in JSON payload: {e}"}), 400


    # Convert the extracted data into a Pandas DataFrame, ensuring correct column order
    input_data = pd.DataFrame([input_values], columns=feature_names)

    # Make prediction (model predicts actual sales, not log sales)
    predicted_sales = model.predict(input_data)[0]

    # Convert predicted_sales to Python float and round
    predicted_sales = round(float(predicted_sales), 2)

    # Return the predicted sales
    return jsonify({'Predicted Product Store Sales Total ($)': predicted_sales})


# Define an endpoint for batch prediction (POST request)
@product_store_sales_total_prediction_api.post('/v1/batchsales') # Corrected API name and endpoint
def predict_batch_sales():
    """
    This function handles POST requests to the '/v1/batchsales' endpoint.
    It expects a CSV file containing product details for multiple products
    and returns the predicted sales as a list in the JSON response.

    The uploaded CSV file must contain the following columns in any order:
    'Product_Weight', 'Product_Allocated_Area', 'Product_MRP', 'Store_Establishment_Year',
    'Product_Sugar_Content', 'Product_Type', 'Store_Id', 'Store_Size',
    'Store_Location_City_Type', 'Store_Type'.
    """
    # Get the uploaded CSV file from the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if not file.filename.endswith('.csv'):
        return jsonify({"error": "Invalid file type. Please upload a CSV file."}), 400

    # Read the CSV file into a Pandas DataFrame
    input_data = pd.read_csv(file)

    # Ensure the input_data has the correct columns and order for the model
    # Missing columns or incorrect names will lead to errors in the pipeline.
    try:
        input_data = input_data[feature_names] # Selects and reorders columns as expected by the model
    except KeyError as e:
        return jsonify({"error": f"Missing expected column in CSV file: {e}"}), 400


    # Make predictions for all products in the DataFrame
    predicted_sales_batch = model.predict(input_data).tolist()

    # Convert predicted_sales to Python float and round
    predicted_sales_batch = [round(float(sales), 2) for sales in predicted_sales_batch]

    # Return the predictions list as a JSON response
    return jsonify({'Batch Predicted Product Store Sales Total ($)': predicted_sales_batch})

# Run the Flask application in debug mode if this script is executed directly
if __name__ == '__main__':
    product_store_sales_total_prediction_api.run(debug=True)

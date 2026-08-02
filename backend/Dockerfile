# Use a minimal base image with Python 3.9 installed
FROM python:3.9-slim-buster

# Set the working directory inside the container to /app
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application file
COPY app.py .

# Copy the trained model and its associated files (e.g., preprocessor if it were separate)
# Assuming deployment_files is a sibling directory to backend_files
COPY ../deployment_files /app/deployment_files

# Set environment variable for Flask
ENV FLASK_APP=app.py

# Expose the port Flask runs on
EXPOSE 5000

# Command to run the Flask application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]

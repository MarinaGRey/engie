# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt ./

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code to the working directory
COPY . .

# Copy the payload1.json file to the working directory
COPY payload1.json ./

# Expose the port that the Flask app runs on
EXPOSE 8888

# Command to run your application
CMD ["python", "app.py"]

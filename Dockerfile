# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that Uvicorn will run on (Render automatically maps this)
EXPOSE 10000

# Command to run the application using Uvicorn
# Uvicorn will run your FastAPI app 'app' from 'main.py'
# It listens on 0.0.0.0 for external access
# $PORT is an environment variable provided by Render, which Uvicorn will use
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
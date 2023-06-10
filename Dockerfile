# Base image
FROM python:3.8-slim-buster

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the required packages from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY . .

# Expose the port on which the application will run
EXPOSE 5000

# Start the Flask application
CMD [ "python", "app.py" ]

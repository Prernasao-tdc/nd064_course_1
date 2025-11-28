# Use the official Python base image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Initialize the database
RUN python init_db.py

# Expose the application port
EXPOSE 3111

# Command to run the application
CMD ["python", "app.py"]
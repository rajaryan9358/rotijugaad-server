# Use the official Python image as the base
FROM python:3.8

# Set the working directory inside the container
WORKDIR /app

# Copy the application code into the container
COPY . /app

# Install dependencies
# RUN pip install -r requirements.txt

# Expose the port that the Django development server will run on
EXPOSE 8000

# Define the command to run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Expose port 8050 for the Dash app
EXPOSE 8050

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "app.py"]



# NEXT STEPS:
    # Build Docker Image
    # docker build -t your-image-name .
    # Run Docker Container
    # docker run -p 8050:8050 your-image-name
    # Access the Dash app at http://localhost:8050 in your web browser

# Run on your machine:  This simulates a fresh environment to ensure everything works as expected.
# docker-compose down -v  # Stop containers and remove volumes
# docker system prune -a  # Remove all images and containers
# docker-compose up --build

# Use a lightweight Python base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application files
COPY app.py /app/
COPY static /app/static/

# Install Flask
RUN pip install --root-user-action=ignore flask psutil

# Expose the Flask port
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]

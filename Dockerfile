# Use a lightweight Python base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application files
COPY app.py /app/
COPY static /app/static/

# Install Flask and Gunicorn (and other dependencies)
RUN pip install --disable-pip-version-check --root-user-action=ignore flask psutil matplotlib docker gunicorn

# Expose the Flask port
EXPOSE 5000

# Use Gunicorn to run the Flask app
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]


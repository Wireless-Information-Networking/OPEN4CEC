# Use Python image
FROM python:3.9

# Set working directory
WORKDIR /app

# Copy and install requirements
COPY app.py /app/
RUN pip install flask

# Run the app
CMD ["python", "app.py"]

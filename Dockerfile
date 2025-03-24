FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy specific Python files to the container
COPY webcrawler.py /app/
COPY email_sender.py /app/
COPY styles.css /app/

# Install dependencies if a requirements.txt file exists
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt || echo "No requirements.txt found, skipping installation."

# Run the webcrawler script
CMD ["python", "webcrawler.py"]

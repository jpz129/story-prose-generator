# Use an official slim Python image.
FROM python:3.12-slim

# Set the working directory.
WORKDIR /app

# Copy requirement file and install dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download the spaCy model.
RUN python -m spacy download en_core_web_md

# Copy the full app.
COPY . .

# Expose the port that Cloud Run expects.
EXPOSE 8080

# Command to run the application.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
# Use a lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependency list
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy only critical folders and files
COPY requirements.txt .
COPY handlers/ handlers/
COPY utils/ utils/
COPY mainbot.py .

# Command to run your bot
CMD ["python", "mainbot.py"]

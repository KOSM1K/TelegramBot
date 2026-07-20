# Use an official lightweight Python image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only requirements first to leverage Docker cache (faster rebuilds)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Run the bot. We use 'python -m app.main' so Python treats 'app' as a package
CMD ["python", "-m", "app.main"]

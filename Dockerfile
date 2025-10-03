# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies, including Google Chrome using the modern key method
RUN apt-get update && apt-get install -y wget gnupg unzip --no-install-recommends \
    # Download the Google Chrome signing key and store it in the dedicated keyring folder
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google-chrome.gpg \
    # Add the Google Chrome repository, now pointing to the new key
    && sh -c 'echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    # Update package lists and install Chrome
    && apt-get update \
    && apt-get install -y google-chrome-stable --no-install-recommends \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code
COPY . .

# Command to run the application
CMD ["python3", "esimga.py"]

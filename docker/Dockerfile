FROM python:3.10-alpine

# Install build dependencies for compiling Python packages
RUN apk add --no-cache build-base python3-dev

# Create application directory
RUN mkdir /cybermillionaire

# Set the working directory inside the container
WORKDIR /cybermillionaire

# Upgrade pip for Python 3
RUN pip3 install --upgrade pip

# Install Python dependencies from requirements.txt using pip3
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

# Copy the rest of the application files to the container
COPY ./cybermillionaire /cybermillionaire

# Copy the entrypoint.sh script to the container
COPY ./entrypoint.sh /entrypoint.sh

# Make sure entrypoint.sh is executable
RUN chmod +x /entrypoint.sh

# Set entrypoint to run the entrypoint.sh script
ENTRYPOINT ["sh", "/entrypoint.sh"]

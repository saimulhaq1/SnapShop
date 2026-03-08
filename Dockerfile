FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies (needed for mysqlclient/psycopg2 if any)
RUN apt-get update \
    && apt-get install -y gcc default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install gunicorn whitenoise

# Copy project
COPY . /app/

# Make the start script executable
RUN chmod +x /app/start.sh

# Expose port (Render dynamically sets the PORT environment variable)
EXPOSE 8000

# Run the application
CMD ["/app/start.sh"]

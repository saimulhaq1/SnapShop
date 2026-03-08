#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting deployment process..."

# Apply database migrations
echo "Running database migrations..."
# Flask-Migrate command
flask db upgrade

# Run Gunicorn
echo "Starting Gunicorn server..."
# Using gevent workers as you have socketio
exec gunicorn "app:create_app()" -w 4 -k gevent -b 0.0.0.0:${PORT:-8000}

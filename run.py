import os
from dotenv import load_dotenv

# Load environment variables from .env file before anything else
load_dotenv()

from app import create_app
from app.extensions import socketio

# Create the app instance using the factory
app = create_app()

if __name__ == "__main__":
    # In a local environment, debug=True helps with development
    socketio.run(app, debug=True)
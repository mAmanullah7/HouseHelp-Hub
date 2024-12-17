import os

from app import app

# Gunicorn will look for 'application'
application = app

if __name__ == "__main__":
    app.run()

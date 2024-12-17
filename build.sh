#!/bin/bash
gunicorn wsgi:application --bind 0.0.0.0:$PORT


pip install -r requirements.txt 
apt get install build-essential
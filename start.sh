#!/bin/bash
# Start script for the Web Scraper application

# Start the Git auto-commit watcher in the background
echo "Starting Git auto-commit watcher..."
python git_auto_commit.py &
GIT_WATCHER_PID=$!

# Start the Flask application
echo "Starting Flask application..."
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app

# If the Flask application stops, kill the Git watcher
kill $GIT_WATCHER_PID
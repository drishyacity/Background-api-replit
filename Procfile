
web: gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 300 --preload --max-requests 1000 --max-requests-jitter 100 app:app

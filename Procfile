web: gunicorn routes:flask_app
worker: celery -E -A routes.celery worker -l info
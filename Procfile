release: python manage.py migrate
web: gunicorn config.wsgi
worker: python script/01.py
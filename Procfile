clock: python populate_db.py
web: gunicorn flask_app:app
web: python manage.py runserver --host 0.0.0.0 --port ${PORT}
init: python manage.py db init
migrate: python manage.py db migrate
upgrade: python manage.py db upgrade
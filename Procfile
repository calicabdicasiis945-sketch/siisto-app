web: python manage.py migrate --noinput && python manage.py seed_exercise_library && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --log-file -

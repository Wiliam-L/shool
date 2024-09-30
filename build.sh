#!/usr/bin/env bash
# Exit on error
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.get_or_create(username='wlopez', defaults={'email': 'admin@example.com', 'password': '123asdfgna'})" | python manage.py shell

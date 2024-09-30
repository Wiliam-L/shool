#!/usr/bin/env bash
# Exit on error
set -o errexit

# Instalar dependencias
pip install -r requirements.txt

# Recolectar archivos estáticos
python manage.py collectstatic --no-input

# Ejecutar migraciones
python manage.py migrate

# Crear el grupo y el usuario
echo "
from django.contrib.auth.models import User, Group

# Crea el grupo
group, created = Group.objects.get_or_create(name='admin')

user, created = User.objects.get_or_create(
    username='wlopez',
    defaults={'email': 'admin@example.com'}
)

if created:
    user.set_password('123asdfgna')
    user.save()

user.groups.add(group)
" | python manage.py shell

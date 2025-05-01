pip install -r requirements.txt

# Migraciones y archivos estáticos
python manage.py collectstatic --noinput
python manage.py migrate

# Crear superusuario automáticamente si no existe
echo "from django.contrib.auth import get_user_model; \
User = get_user_model(); \
User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists() or \
User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')" \
| python manage.py shell
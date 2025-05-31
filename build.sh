# --- Instalación de dependencias con Pipenv ---
echo "Instalando dependencias con Pipenv..."
pipenv install --deploy --system || { echo "Fallo al instalar dependencias con Pipenv"; exit 1; }

# --- Migraciones y archivos estáticos (ejecutados con Pipenv) ---
echo "Ejecutando migraciones de Django..."
pipenv run python manage.py migrate || { echo "Fallo en las migraciones de Django"; exit 1; }

echo "Recolectando archivos estáticos..."
pipenv run python manage.py collectstatic --noinput || { echo "Fallo al recolectar archivos estáticos"; exit 1; }

# --- Crear superusuario automáticamente si no existe (ejecutado con Pipenv) ---
echo "Creando superusuario si no existe..."
pipenv run python manage.py shell <<EOF || { echo "Fallo al crear superusuario"; exit 1; }
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print("Superusuario creado.")
else:
    print("El superusuario ya existe.")
EOF

echo "Proceso de construcción completado exitosamente."
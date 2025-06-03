# --- Instalación de dependencias con Pipenv ---
echo "Instalando dependencias con Pipenv..."
pipenv install --deploy --system || { echo "Fallo al instalar dependencias con Pipenv"; exit 1; }

# --- Migraciones y archivos estáticos ---
echo "Ejecutando makemigrations..."
pipenv run python manage.py makemigrations || { echo "Fallo en makemigrations"; exit 1; }

echo "Ejecutando migraciones de Django..."
pipenv run python manage.py migrate || { echo "Fallo en las migraciones de Django"; exit 1; }

echo "Recolectando archivos estáticos..."
pipenv run python manage.py collectstatic --noinput || { echo "Fallo al recolectar archivos estáticos"; exit 1; }

# --- Crear superusuario automáticamente ---
echo "Creando superusuario si no existe..."
pipenv run python manage.py shell <<EOF_PYTHON || { echo "Fallo al crear superusuario"; exit 1; }
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print("Superusuario creado.")
else:
    print("El superusuario ya existe.")
EOF_PYTHON

echo "Proceso de construcción completado exitosamente."
#!/usr/bin/env bash
# build.sh

# Instalar dependencias
pip install -r requirements.txt

# Migraciones y archivos estáticos
python manage.py collectstatic --noinput
python manage.py migrate
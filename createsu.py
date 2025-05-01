import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Crea un superusuario si no existe.'

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not User.objects.filter(username=username).exists():
            if not username or not password:
                self.stdout.write(self.style.ERROR('Debes definir las variables de entorno DJANGO_SUPERUSER_USERNAME y DJANGO_SUPERUSER_PASSWORD en Render.'))
                return

            User.objects.create_superuser(username, email, password)
            self.stdout.write(self.style.SUCCESS(f'Superusuario "{username}" creado exitosamente.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'El superusuario "{username}" ya existe.'))
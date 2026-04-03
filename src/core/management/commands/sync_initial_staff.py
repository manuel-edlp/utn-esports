import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Staff

class Command(BaseCommand):
    help = 'Sincroniza el usuario staff inicial desde variables de entorno'

    def handle(self, *args, **options):
        email = os.environ.get('INITIAL_STAFF_EMAIL', 'manuelmorullo@hotmail.com')
        password = os.environ.get('INITIAL_STAFF_PASSWORD', '1234')
        nombre = os.environ.get('INITIAL_STAFF_NOMBRE', 'Manuel')
        apellido = os.environ.get('INITIAL_STAFF_APELLIDO', 'Morullo')
        dni = os.environ.get('INITIAL_STAFF_DNI', '99999999')

        if not email or not password:
            self.stdout.write(self.style.WARNING('Faltan variables de entorno para el staff.'))
            return

        # 1. Sincronizar el User de Django
        user, created = User.objects.get_or_create(
            username=email, 
            defaults={'email': email}
        )
        
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        # 2. Sincronizar tu modelo Staff
        Staff.objects.update_or_create(
            user=user,
            defaults={
                'nombre': nombre,
                'apellido': apellido,
                'dni': dni,
                'email': email,
                'rol': 'staff',
                'inscripciones_habilitadas': True
            }
        )

        status = "creado" if created else "actualizado"
        self.stdout.write(self.style.SUCCESS(f'Usuario Staff {email} {status} correctamente.'))
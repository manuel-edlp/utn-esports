from django.db import migrations
import os

def create_initial_staff(apps, schema_editor):
    email = os.environ.get('INITIAL_STAFF_EMAIL')
    password = os.environ.get('INITIAL_STAFF_PASSWORD')

    if not email or not password:
        return

    User = apps.get_model('auth', 'User')
    Staff = apps.get_model('core', 'Staff')

    nombre = os.environ.get('INITIAL_STAFF_NOMBRE', 'Admin')
    apellido = os.environ.get('INITIAL_STAFF_APELLIDO', 'UTN')
    dni = os.environ.get('INITIAL_STAFF_DNI', '99999999')

    user, created = User.objects.get_or_create(
        username=email,
        defaults={
            'email': email,
            'is_staff': True,
            'is_superuser': True,
        },
    )

    needs_save = False
    if user.email != email:
        user.email = email
        needs_save = True
    if not user.is_staff:
        user.is_staff = True
        needs_save = True
    if not user.is_superuser:
        user.is_superuser = True
        needs_save = True

    if created or needs_save:
        user.save()

    user.set_password(password)
    user.save(update_fields=['password'])

    Staff.objects.update_or_create(
        user=user,
        defaults={
            'nombre': nombre,
            'apellido': apellido,
            'dni': dni,
            'email': email,
            'rol': 'staff',
            'inscripciones_habilitadas': True,
        },
    )

def noop_reverse(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_alter_equipo_comprobante_pago_alter_equipo_logo_and_more'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_initial_staff, noop_reverse),
    ]
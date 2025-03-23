from django.db import models
from django.contrib.auth.models import User


class EstadoAprobacion(models.TextChoices):
    APROBADO = "Aprobado", "Aprobado"
    RECHAZADO = "Rechazado", "Rechazado"
    EN_REVISION = "En revisión", "En revisión"
    PAGO_PENDIENTE = "Pago pendiente", "Pago de inscripción pendiente"

    
class Usuario(models.Model):
    # Roles
    ES_JUGADOR = 'jugador'
    ES_STAFF = 'staff'
    ROL_CHOICES = [
        (ES_JUGADOR, 'Jugador'),
        (ES_STAFF, 'Staff'),
    ]

    # Relación con el modelo User de Django
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='usuario')

    # Datos comunes para jugadores y staff
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=40, unique=True)
    email = models.EmailField(unique=True)

    # Rol del usuario (jugador o staff)
    rol = models.CharField(max_length=10, choices=ROL_CHOICES, default=ES_JUGADOR)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    def es_jugador(self):
        return self.rol == self.ES_JUGADOR

    def es_staff(self):
        return self.rol == self.ES_STAFF
    
    # La defino abstracta para que no se cree una tabla en la base de datos
    class Meta:
        abstract = True


class Jugador(Usuario):
    # Relacion con el modelo User de Django
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='jugador')

    # Datos adicionales para jugadores
    telefono = models.CharField(max_length=40)
    telegram = models.CharField(max_length=40)
    pais = models.CharField(max_length=40)
    foto = models.ImageField(upload_to='fotos/', null=True)
    legajo = models.CharField(max_length=40, blank=True ,null=True)

    # Datos de Riot
    riot_id = models.CharField(max_length=40, unique=True)

    # Relación ForeignKey con Equipo
    equipo = models.ForeignKey('Equipo', on_delete=models.SET_NULL, null=True, related_name='miembros', blank=True)

    # Campo para controlar la edición del perfil
    edicion_habilitada = models.BooleanField(default=True)


    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Staff(Usuario):
    # Relacion con el modelo User de Django
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff')

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Equipo(models.Model):
    nombre = models.CharField(max_length=40, unique=True)
    abreviatura = models.CharField(max_length=10)
    logo = models.ImageField(upload_to='logos/')
    comprobante_pago = models.ImageField(upload_to='comprobantes/')
    estadoAprobacion = models.CharField(
        max_length=20,
        choices=EstadoAprobacion.choices,
        default=EstadoAprobacion.PAGO_PENDIENTE
    )
    creado_por = models.ForeignKey(Jugador, on_delete=models.CASCADE, related_name='equipos_creados')
    capitan = models.ForeignKey(Jugador, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipo_capitan')

    def __str__(self):
        return f"{self.nombre}"


class Invitacion(models.Model):
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='invitaciones')
    jugador_invitado = models.ForeignKey(Jugador, on_delete=models.CASCADE, related_name='invitaciones_recibidas')
    aceptada = models.BooleanField(default=False)

    def __str__(self):
        return f"Invitación a {self.jugador_invitado} para unirse a {self.equipo}"
    
class TwitchClip(models.Model):
    nombre = models.CharField(max_length=100, help_text="Nombre descriptivo del clip")
    url = models.URLField(help_text="URL completa del clip de Twitch")
    activo = models.BooleanField(default=True, help_text="¿Este clip está activo y debe mostrarse en el carrusel?")

    def __str__(self):
        return self.nombre

    def get_embed_url(self):
        """
        Convierte la URL del clip en un formato compatible con el iframe de Twitch.
        """
        clip_id = self.url.split('/')[-1]  # Extrae el ID del clip de la URL
        return f"https://clips.twitch.tv/embed?clip={clip_id}&parent=127.0.0.1"
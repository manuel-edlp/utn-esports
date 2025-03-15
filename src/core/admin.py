from django.contrib import admin
from .models import Usuario, Jugador, Staff, Equipo, Invitacion

# Modelos registrados en Django Admin

@admin.register(Jugador)
class JugadorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'usuario_riot', 'riot_id', 'telefono', 'pais')
    search_fields = ('nombre', 'apellido', 'usuario_riot', 'riot_id')

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'email')
    search_fields = ('nombre', 'apellido', 'email')

@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'abreviatura', 'creado_por', 'aprobado')
    list_filter = ('aprobado',)
    search_fields = ('nombre', 'creado_por__nombre')

@admin.register(Invitacion)
class InvitacionAdmin(admin.ModelAdmin):
    list_display = ('equipo', 'jugador_invitado', 'aceptada')
    list_filter = ('aceptada',)
    search_fields = ('equipo__nombre', 'jugador_invitado__nombre')
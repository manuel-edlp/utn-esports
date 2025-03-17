from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('faq/', views.Faq.as_view(), name='faq'),
    path('sponsors/', views.Sponsors.as_view(), name='sponsors'),
    path('register/', views.RegistroView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Jugador
    path('player/home/', views.PlayerHomeView.as_view(), name='player_home'),
    path('player/perfil/', views.PerfilView.as_view(), name='perfil'),
    path('player/crear_equipo/', views.CrearEquipoView.as_view(), name='crear_equipo'),
    path('player/editar_equipo/<int:equipo_id>/', views.EditarEquipoView.as_view(), name='editar_equipo'),
    path('player/eliminar_equipo/<int:equipo_id>/', views.EliminarEquipoView.as_view(), name='eliminar_equipo'),

    # Invitaciones
    path('player/invitar/<int:equipo_id>/', views.InvitarJugadorView.as_view(), name='invitar_jugador'),
    path('player/invitaciones/<int:invitacion_id>/aceptar/', views.AceptarInvitacionView.as_view(), name='aceptar_invitacion'),
    path('player/invitaciones/<int:invitacion_id>/rechazar/', views.RechazarInvitacionView.as_view(), name='rechazar_invitacion'),
]


# Sirve archivos multimedia en modo de desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.urls import path
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
]
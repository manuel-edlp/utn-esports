from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('faq/', views.Faq.as_view(), name='faq'),
    path('sponsors/', views.Sponsors.as_view(), name='sponsors'),
    path('register/', views.RegistroView.as_view(), name='register'),
]
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views import View
from .models import Jugador
from django.urls import reverse_lazy

class Home(TemplateView):
    template_name = 'home/home.html'

class Faq(TemplateView):
    template_name = 'faq/faq.html'

class Sponsors(TemplateView):
    template_name = 'sponsors/sponsors.html'

class RegistroView(View):
    template_name = "register/register.html"
    success_url = reverse_lazy("home")

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        # Paso 1: Datos personales
        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        dni = request.POST.get("dni")
        telefono = request.POST.get("telefono")
        pais = request.POST.get("pais")

        # Paso 2: Datos de Riot
        usuario_riot = request.POST.get("riot-username")
        riot_id = request.POST.get("riot-tag")

        # Paso 3: Credenciales
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm-password")

        # Validaciones
        if password != confirm_password:
            return render(request, self.template_name, {"error": "Las contraseñas no coinciden."})

        # Verifica si el usuario ya existe
        if User.objects.filter(email=email).exists():
            return render(request, self.template_name, {"error": "El correo electrónico ya está registrado."})

        # Crea el usuario base (User de Django)
        try:
            user = User.objects.create_user(
                username=email,  # Uso el email como nombre de usuario
                email=email,
                password=password,  # Django aplica el hash automáticamente
            )
        except Exception as e:
            return render(request, self.template_name, {"error": f"Error al crear el usuario: {e}"})

        # Crea el jugador con la contraseña encriptada
        try:

            jugador = Jugador.objects.create(
                user=user,  # Relación uno a uno con User
                nombre=nombre,
                apellido=apellido,
                dni=dni,
                email=email,
                telefono=telefono,
                pais=pais,
                usuario_riot=usuario_riot,
                riot_id=riot_id
            )
        except Exception as e:
            user.delete()  # Si algo falla, eliminamos el usuario
            return render(request, self.template_name, {"error": f"Error al crear el jugador: {e}"})

        # Redirige a la página de inicio
        return redirect(self.success_url)
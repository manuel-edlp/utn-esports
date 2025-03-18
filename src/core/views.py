import json
from django.http import JsonResponse
from django.views.generic import TemplateView, RedirectView, ListView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from .models import Equipo, Invitacion, Jugador
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

class Home(TemplateView):
    template_name = 'home/home.html'

class Faq(TemplateView):
    template_name = 'faq/faq.html'

class Reglamento(TemplateView):
    template_name = 'reglamento/reglamento.html'

class Sponsors(TemplateView):
    template_name = 'sponsors/sponsors.html'

class RegistroView(View):
    template_name = "register/register.html"
    success_url = reverse_lazy("login")

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        # Paso 1: Datos personales
        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        dni = request.POST.get("dni")
        telefono = request.POST.get("telefono")
        pais = request.POST.get("pais")
        legajo = request.POST.get("legajo")

        # Paso 2: Datos de Riot
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
                legajo=legajo,
                email=email,
                telefono=telefono,
                pais=pais,
                riot_id=riot_id
            )
        except Exception as e:
            user.delete()  # Si algo falla, eliminamos el usuario
            return render(request, self.template_name, {"error": f"Error al crear el jugador: {e}"})

        # Redirige a la página de inicio
        return redirect(self.success_url)
    
class LoginView(TemplateView):
    template_name = 'login/login.html'

    def get(self, request, *args, **kwargs):
        # Compruebo si hay un parámetro 'next' en la URL, lo que indica que la sesión ha expirado
        if request.GET.get('next'):
            messages.warning(request, "Tu sesión ha expirado. Por favor, inicia sesión nuevamente.", extra_tags='session_expired')
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Autentica al usuario
        user = authenticate(request, username=email, password=password)

        if user is not None:
            # Inicia sesión
            login(request, user)
            return redirect('player_home')
        else:
            # Muestra mensaje de error si las credenciales son incorrectas
            messages.error(request, 'Correo electrónico o contraseña incorrectos.')
            return render(request, self.template_name)
        
class PlayerHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'player/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtiene el jugador asociado al usuario actual
        try:
            jugador = Jugador.objects.get(user=self.request.user)
            context['jugador'] = jugador  # Pasa los datos del jugador a la plantilla

            # Obtiene el equipo al que pertenece el jugador (si existe)
            equipo = jugador.equipo
            context['equipo'] = equipo  # Pasa el equipo a la plantilla

            # Obtiene las invitaciones pendientes del jugador
            invitaciones = Invitacion.objects.filter(jugador_invitado=jugador, aceptada=False)
            context['invitaciones'] = invitaciones  # Pasa las invitaciones a la plantilla

        except Jugador.DoesNotExist:
            context['jugador'] = None
            context['equipo'] = None
            context['invitaciones'] = []

        return context


class PerfilView(LoginRequiredMixin, TemplateView):
    template_name = 'player/perfil.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtiene el jugador asociado al usuario actual
        try:
            jugador = Jugador.objects.get(user=self.request.user)
            context['jugador'] = jugador  # Pasa los datos del jugador a la plantilla
        except Jugador.DoesNotExist:
            context['jugador'] = None  # Si no existe, pasa None

        return context
    


class CrearEquipoView(LoginRequiredMixin, TemplateView):
    template_name = 'player/crear_equipo.html'

    def get(self, request, *args, **kwargs):
        # Verificar si el usuario es un jugador
        if not hasattr(request.user, 'jugador'):
            messages.error(request, "Solo los jugadores pueden crear equipos.")
            return redirect('player_home')

        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        # Verifica si el usuario es un jugador
        if not hasattr(request.user, 'jugador'):
            messages.error(request, "Solo los jugadores pueden crear equipos.")
            return redirect('player_home')

        # Obteniene los datos del formulario
        nombre = request.POST.get('nombre')
        abreviatura = request.POST.get('abreviatura')
        logo = request.FILES.get('logo')
        comprobante_pago = request.FILES.get('comprobante_pago')

        # Valida los datos
        if not nombre or not abreviatura or not logo or not comprobante_pago:
            messages.error(request, "Todos los campos son obligatorios.")
            return render(request, self.template_name)

        # Crear el equipo
        try:
            equipo = Equipo(
                nombre=nombre,
                abreviatura=abreviatura,
                logo=logo,
                comprobante_pago=comprobante_pago,
                creado_por=request.user.jugador
            )
            equipo.save()

            # Asocia el equipo al jugador que lo creos
            jugador = request.user.jugador
            jugador.equipo = equipo
            jugador.save()

            # Mensaje de éxito
            messages.success(request, f"Equipo '{equipo.nombre}' creado exitosamente.")
            return redirect('player_home')

        except Exception as e:
            messages.error(request, f"Error al crear el equipo: {str(e)}")
            return render(request, self.template_name)


class EditarEquipoView(LoginRequiredMixin, TemplateView):
    template_name = 'player/editar_equipo.html'

    def get(self, request, equipo_id, *args, **kwargs):
        equipo = get_object_or_404(Equipo, id=equipo_id)
        
        # Verifica si el jugador es miembro del equipo
        if request.user.jugador not in equipo.miembros.all():
            messages.error(request, "No tienes permisos para editar este equipo.")

        return render(request, self.template_name, {'equipo': equipo})

    def post(self, request, equipo_id, *args, **kwargs):
        equipo = get_object_or_404(Equipo, id=equipo_id)
        
        # Verifica si el jugador es miembro del equipo
        if request.user.jugador not in equipo.miembros.all():
            messages.error(request, "No tienes permisos para editar este equipo.")
        

        # Continuar con la actualización del equipo
        equipo.nombre = request.POST.get('nombre')
        equipo.abreviatura = request.POST.get('abreviatura')
        if 'logo' in request.FILES:
            equipo.logo = request.FILES['logo']
        if 'comprobante_pago' in request.FILES:
            equipo.comprobante_pago = request.FILES['comprobante_pago']
        equipo.save()
        messages.success(request, f"Equipo '{equipo.nombre}' actualizado exitosamente.")
        return redirect('player_home')
    
class EliminarEquipoView(LoginRequiredMixin, View):
    def post(self, request, equipo_id, *args, **kwargs):
        equipo = get_object_or_404(Equipo, id=equipo_id, creado_por=request.user.jugador)
        equipo.delete()
        messages.success(request, f"Equipo '{equipo.nombre}' eliminado exitosamente.")
        return redirect('player_home')

class AbandonarEquipoView(LoginRequiredMixin, View):
    def post(self, request, equipo_id, *args, **kwargs):
        equipo = get_object_or_404(Equipo, id=equipo_id)
        if request.user.jugador in equipo.miembros.all():
            equipo.miembros.remove(request.user.jugador)
            messages.success(request, f"Has abandonado el equipo '{equipo.nombre}' exitosamente.")
            return redirect('player_home')
        else:
            messages.error(request, "Error. No eres miembro de este equipo.")
            return redirect('player_home')

class InvitarJugadorView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)  # Decodifica el JSON
            email = data.get('email', '').strip().lower()  # Normaliza el correo
        except json.JSONDecodeError:
            return JsonResponse({'error': "Formato de datos inválido."}, status=400)

        equipo_id = self.kwargs.get('equipo_id')
        equipo = get_object_or_404(Equipo, id=equipo_id)

        try:
            jugador_invitado = Jugador.objects.get(email=email)
        except Jugador.DoesNotExist:
            return JsonResponse({'error': "No se encontró un jugador con ese correo electrónico."}, status=400)

        if Invitacion.objects.filter(equipo=equipo, jugador_invitado=jugador_invitado, aceptada=False).exists():
            return JsonResponse({'warning': "Ya has enviado una invitación a este jugador."}, status=200)

        Invitacion.objects.create(equipo=equipo, jugador_invitado=jugador_invitado, aceptada=False)
        return JsonResponse({'success': f"Invitación enviada a {jugador_invitado.nombre} {jugador_invitado.apellido}."}, status=200)
    
class ListarInvitacionesView(ListView):
    template_name = 'player_home.html'
    context_object_name = 'invitaciones'

    def get_queryset(self):
        # Obtiene las invitaciones del jugador actual
        return Invitacion.objects.filter(jugador_invitado=self.request.user.jugador, aceptada=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['equipo'] = self.request.user.jugador.equipos_creados.first()
        return context

class AceptarInvitacionView(View):
    def post(self, request, *args, **kwargs):
        invitacion_id = self.kwargs.get('invitacion_id')
        invitacion = get_object_or_404(Invitacion, id=invitacion_id)

        # Verifica que la invitación no haya sido aceptada previamente
        if invitacion.aceptada:
            messages.warning(request, "Esta invitación ya ha sido aceptada.")
            return redirect('player_home')

        # Verifica que el jugador no esté ya en un equipo
        if invitacion.jugador_invitado.equipo:
            messages.warning(request, "Ya perteneces a un equipo.")
            return redirect('player_home')

        # Acepta la invitación
        invitacion.aceptada = True
        invitacion.save()

        # Asigna el equipo al jugador
        invitacion.jugador_invitado.equipo = invitacion.equipo
        invitacion.jugador_invitado.save()

        messages.success(request, f"Has aceptado la invitación para unirte a {invitacion.equipo.nombre}.")
        return redirect('player_home')
    
class RechazarInvitacionView(View):
    def post(self, request, *args, **kwargs):
        invitacion_id = self.kwargs.get('invitacion_id')
        invitacion = get_object_or_404(Invitacion, id=invitacion_id)

        # Verifica que la invitación no haya sido aceptada previamente
        if invitacion.aceptada:
            messages.warning(request, "Esta invitación ya ha sido aceptada.")
            return redirect('player_home')

        invitacion.delete()

        messages.success(request, "Has rechazado la invitación.")
        return redirect('player_home')
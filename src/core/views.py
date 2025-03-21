import json
from django.forms import ValidationError
from django.http import JsonResponse
from django.views.generic import TemplateView, RedirectView, ListView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from .models import Equipo, EstadoAprobacion, Invitacion, Jugador
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
import filetype
import re

class Home(TemplateView):
    template_name = 'home/home.html'

class Faq(TemplateView):
    template_name = 'faq/faq.html'

class Reglamento(TemplateView):
    template_name = 'reglamento/reglamento.html'

class Sponsors(TemplateView):
    template_name = 'sponsors/sponsors.html'


# Función para validar el formulario de registro
def validar_formulario(form_data):
    errors = {}

    # Validar contraseñas
    if form_data["password"] != form_data["confirm_password"]:
        errors["password"] = "Las contraseñas no coinciden."

    # Validar email único
    if User.objects.filter(email=form_data["email"]).exists():
        errors["email"] = "El correo electrónico ya está registrado."

    # Validar DNI único
    if Jugador.objects.filter(dni=form_data["dni"]).exists():
        errors["dni"] = "El DNI ya está registrado."

    # Validar Riot ID único
    if Jugador.objects.filter(riot_id=form_data["riot_id"]).exists():
        errors["riot_id"] = "El Riot ID ya está registrado."

    # Validar formato de Riot ID
    if form_data["riot_id"] and "#" not in form_data["riot_id"]:
        errors["riot_id"] = "El Riot ID debe contener el símbolo '#'."

    # Validar si se seleccionó una opción en "pertenece-utn"
    if not form_data.get("pertenece_utn"):
        errors["pertenece_utn"] = "Debes seleccionar una opción."

    # Validar legajo único (si pertenece a la UTN)
    if form_data.get("pertenece_utn") == "si":
        if Jugador.objects.filter(legajo=form_data["legajo"]).exists():
            errors["legajo"] = "El legajo ya está registrado."

    # Validar campos obligatorios
    required_fields = ["nombre", "apellido", "dni", "telefono", "telegram", "pais", "riot_id", "email", "password", "confirm_password"]
    if form_data.get("pertenece_utn") == "si":
        required_fields.append("legajo")

    for field in required_fields:
        if not form_data[field]:
            errors[field] = "Este campo es obligatorio."

    # Validar foto (si es necesario)
    if not form_data["foto"]:
        errors["foto"] = "Debes subir una foto."

    # Validar tipo de texto en los campos (solo si el campo no está vacío)
    if form_data["nombre"] and not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÜüÑñ\s]+$", form_data["nombre"]):
        errors["nombre"] = "El nombre solo puede contener letras y espacios."

    if form_data["apellido"] and not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÜüÑñ\s]+$", form_data["apellido"]):
        errors["apellido"] = "El apellido solo puede contener letras y espacios."

    if form_data["legajo"] and not re.match(r"^\d+$", form_data["legajo"]):
        errors["legajo"] = "El legajo solo puede contener números."

    if form_data["telefono"] and not re.match(r"^[0-9+\-\s]+$", form_data["telefono"]):
        errors["telefono"] = "El teléfono solo puede contener números, espacios, guiones y el símbolo +."

    if form_data["pais"] and re.search(r"\d", form_data["pais"]):
        errors["pais"] = "El país no puede contener números."

    if form_data["email"] and not re.match(r"^[^@]+@[^@]+\.[^@]+$", form_data["email"]):
        errors["email"] = "El correo electrónico no es válido."

    return errors

class RegistroView(View):
    template_name = "register/register.html"
    success_url = reverse_lazy("login")

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        # Recuperar los datos del formulario
        form_data = {
            "nombre": request.POST.get("nombre"),
            "apellido": request.POST.get("apellido"),
            "dni": request.POST.get("dni"),
            "telefono": request.POST.get("telefono"),
            "telegram": request.POST.get("telegram"),
            "pais": request.POST.get("pais"),
            "legajo": request.POST.get("legajo"),
            "foto": request.FILES.get("foto"),
            "riot_id": request.POST.get("riot-tag"),
            "email": request.POST.get("email"),
            "password": request.POST.get("password"),
            "confirm_password": request.POST.get("confirm-password"),
            "pertenece_utn": request.POST.get("pertenece-utn"),
        }

        # Validar el formulario
        errors = validar_formulario(form_data)

        # Si hay errores, renderizar el formulario con los errores y los datos ingresados
        if errors:
            return render(request, self.template_name, {"errors": errors, "form_data": form_data})

        # Crear el usuario base (User de Django)
        try:
            user = User.objects.create_user(
                username=form_data["email"],  # Uso el email como nombre de usuario
                email=form_data["email"],
                password=form_data["password"],  # Django aplica el hash automáticamente
            )
        except Exception as e:
            errors["general"] = f"Error al crear el usuario: {e}"
            return render(request, self.template_name, {"errors": errors, "form_data": form_data})

        # Crear el jugador
        try:
            jugador = Jugador.objects.create(
                user=user,
                nombre=form_data["nombre"],
                apellido=form_data["apellido"],
                dni=form_data["dni"],
                foto=form_data["foto"],
                legajo=form_data["legajo"] if form_data["pertenece_utn"] == "si" else None,
                email=form_data["email"],
                telefono=form_data["telefono"],
                telegram=form_data["telegram"],
                pais=form_data["pais"],
                riot_id=form_data["riot_id"],
            )
        except Exception as e:
            user.delete()  # Si algo falla, eliminamos el usuario
            errors["general"] = f"Error al crear el jugador: {e}"
            return render(request, self.template_name, {"errors": errors, "form_data": form_data})

        # Redirigir a la página de inicio
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
            messages.error(request, 'Correo electrónico o contraseña incorrectos.', extra_tags='login_error')
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
    success_url = reverse_lazy("perfil")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtiene el jugador asociado al usuario actual
        try:
            jugador = Jugador.objects.get(user=self.request.user)
            context['jugador'] = jugador  # Pasa los datos del jugador a la plantilla
        except Jugador.DoesNotExist:
            context['jugador'] = None  # Si no existe, pasa None

        return context

    def post(self, request, *args, **kwargs):
        # Obtengo el jugador actual
        jugador = get_object_or_404(Jugador, user=request.user)

        # Actualio los campos del jugador
        jugador.nombre = request.POST.get("nombre", jugador.nombre)
        jugador.apellido = request.POST.get("apellido", jugador.apellido)
        jugador.dni = request.POST.get("dni", jugador.dni)
        jugador.telefono = request.POST.get("telefono", jugador.telefono)
        jugador.telegram = request.POST.get("telegram", jugador.telegram)
        jugador.pais = request.POST.get("pais", jugador.pais)
        jugador.legajo = request.POST.get("legajo", jugador.legajo)
        jugador.riot_id = request.POST.get("riot_id", jugador.riot_id)
        jugador.email = request.POST.get("email", jugador.email)

        # Manejo la foto de perfil (si se sube una nueva)
        if "foto" in request.FILES:
            jugador.foto = request.FILES["foto"]

        try:
            jugador.save()
            # Actualizo el email del usuario de Django si cambia
            if jugador.email != request.user.email:
                request.user.email = jugador.email
                request.user.save()
        except Exception as e:
            context = self.get_context_data()
            context["error"] = f"Error al actualizar el perfil: {e}"
            return render(request, self.template_name, context)

        return redirect(self.success_url)
    


class CrearEquipoView(LoginRequiredMixin, TemplateView):
    template_name = 'player/crear_equipo.html'

    def get(self, request, *args, **kwargs):
        # Verifica si el usuario es un jugador
        if not hasattr(request.user, 'jugador'):
            messages.error(request, "Solo los jugadores pueden crear equipos.")
            return redirect('player_home')

        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        # Verifica si el usuario es un jugador
        if not hasattr(request.user, 'jugador'):
            messages.error(request, "Solo los jugadores pueden crear equipos.")
            return redirect('player_home')

        # Obtiene los datos del formulario
        nombre = request.POST.get('nombre')
        abreviatura = request.POST.get('abreviatura')
        logo = request.FILES.get('logo')
        estadoAprobacion = EstadoAprobacion.PAGO_PENDIENTE

        # Valida los datos
        if not nombre or not abreviatura or not logo:
            messages.error(request, "Todos los campos son obligatorios.")
            return render(request, self.template_name, {'nombre': nombre, 'abreviatura': abreviatura})

        # Verifica si el nombre del equipo ya existe en la base de datos
        if Equipo.objects.filter(nombre=nombre).exists():
            messages.error(request, "El nombre del equipo ya está en uso. Elige otro.", extra_tags='error-nombre-equipo')
            return render(request, self.template_name, {'nombre': nombre, 'abreviatura': abreviatura})
        
        # Verifica si la abreviatura del equipo ya existe en la base de datos
        if Equipo.objects.filter(abreviatura=abreviatura).exists():
            messages.error(request, "La abreviatura del equipo ya está en uso. Elige otra.", extra_tags='error-abreviatura-equipo')
            return render(request, self.template_name, {'nombre': nombre, 'abreviatura': abreviatura})

        # Validación del tipo de archivo
        try:
            if 'logo' in request.FILES:
                logo = request.FILES['logo']
                kind = filetype.guess(logo.read(1024))  # Analiza los primeros bytes
                if kind is None or kind.mime not in ['image/jpeg', 'image/png', 'image/jpg']:
                    raise ValidationError("Tipo de archivo no permitido para el logo.")

            # Creo el equipo
            equipo = Equipo(
                nombre=nombre,
                abreviatura=abreviatura,
                logo=logo,
                creado_por=request.user.jugador,
                estadoAprobacion=estadoAprobacion,
                capitan=request.user.jugador
            )
            equipo.save()

            # Asocio el equipo al jugador que lo creó
            jugador = request.user.jugador
            jugador.equipo = equipo
            jugador.save()

            # Mensaje de éxito
            messages.success(request, f"Equipo '{equipo.nombre}' creado exitosamente.")
            return redirect('player_home')

        except ValidationError as e:
            messages.error(request, str(e), extra_tags='error-tipo-archivo')
            return render(request, 'player/crear_equipo.html', {'nombre': nombre, 'abreviatura': abreviatura, 'messages': messages.get_messages(request)})



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
        nombre = request.POST.get('nombre')
        abreviatura = request.POST.get('abreviatura')

        if request.user.jugador not in equipo.miembros.all():
            messages.error(request, "No tienes permisos para editar este equipo.")

         # Verifica si el nombre del equipo ya existe en la base de datos
        if Equipo.objects.filter(nombre=nombre).exists():
            messages.error(request, "El nombre del equipo ya está en uso. Elige otro.", extra_tags='error-nombre-equipo')
            return render(request, self.template_name, {'nombre': nombre, 'abreviatura': abreviatura})
        
        # Verifica si la abreviatura del equipo ya existe en la base de datos
        if Equipo.objects.filter(abreviatura=abreviatura).exists():
            messages.error(request, "La abreviatura del equipo ya está en uso. Elige otra.", extra_tags='error-abreviatura-equipo')
            return render(request, self.template_name, {'nombre': nombre, 'abreviatura': abreviatura})
        

        equipo.nombre = nombre
        equipo.abreviatura = abreviatura


        try:

            if 'logo' in request.FILES:
                logo = request.FILES['logo']
                kind = filetype.guess(logo.read(1024))  # Analiza los primeros bytes
                if kind is None or kind.mime not in ['image/jpeg', 'image/png', 'image/jpg']:
                    raise ValidationError("Tipo de archivo no permitido.")
                logo.seek(0)
                equipo.logo = logo

            equipo.save()
            messages.success(request, f"Equipo '{equipo.nombre}' actualizado exitosamente.")
            return redirect('player_home')
            

        except ValidationError as e:
            messages.error(request, str(e), extra_tags='error-tipo-archivo')
            return render(request, 'player/editar_equipo.html', {'nombre': nombre, 'abreviatura': abreviatura, 'equipo': equipo, 'messages': messages.get_messages(request)})
    
class EliminarEquipoView(LoginRequiredMixin, View):
    def post(self, request, equipo_id, *args, **kwargs):
        equipo = get_object_or_404(Equipo, id=equipo_id, creado_por=request.user.jugador)
        equipo.delete()
        messages.success(request, f"Equipo '{equipo.nombre}' eliminado exitosamente.")
        return redirect('player_home')


class AbandonarEquipoView(LoginRequiredMixin, View):
    def post(self, request, equipo_id, *args, **kwargs):
        equipo = get_object_or_404(Equipo, id=equipo_id)
        jugador = request.user.jugador

        # Verifica si el jugador es miembro del equipo
        if jugador in equipo.miembros.all():

            # Si el jugador es el capitán, transfiero la capitanía
            if equipo.capitan == jugador:

                # Obtengor otro miembro para transfiero la capitanía
                nuevo_capitan = equipo.miembros.exclude(id=jugador.id).first()  # Excluyo al jugador actual

                if nuevo_capitan:
                    # Transfiero la capitanía al nuevo miembro
                    equipo.capitan = nuevo_capitan
                    equipo.save()
                    messages.success(request, f"La capitanía ha sido transferida a {nuevo_capitan.nombre}.")
                else:
                    equipo.capitan = None

            # Remuevo al jugador del equipo
            equipo.miembros.remove(jugador)

            # Verifica si el equipo quedó sin miembros
            if equipo.miembros.count() == 0:
                equipo.delete()  # Elimino el equipo si no hay más miembros
                messages.success(request, f"Has abandonado el equipo '{equipo.nombre}'. Como eras el último miembro, el equipo ha sido eliminado.")
            else:
                messages.success(request, f"Has abandonado el equipo '{equipo.nombre}' exitosamente.")

            return redirect('player_home')
        else:
            messages.error(request, "Error. No eres miembro de este equipo.")
            return redirect('player_home')

class PagarInscripcionView(LoginRequiredMixin, TemplateView):
    template_name = 'player/pagar_inscripcion.html'

    def get(self, request, *args, **kwargs):
        # Verifica si el usuario es un jugador
        if not hasattr(request.user, 'jugador'):
            messages.error(request, "Solo los jugadores pueden realizar pagos.")
            return redirect('player_home')

        # Verifica si el equipo existe y si el jugador pertenece a ese equipo
        equipo_id = self.kwargs.get('equipo_id')
        try:
            equipo = Equipo.objects.get(id=equipo_id)
            if equipo.creado_por != request.user.jugador and equipo.miembros.filter(id=request.user.jugador.id).count() == 0:
                messages.error(request, "Solo los miembros de este equipo pueden realizar pagos.")
                return redirect('player_home')
        except Equipo.DoesNotExist:
            messages.error(request, "No se encontró el equipo.")
            return redirect('player_home')

        return render(request, self.template_name, {'equipo': equipo})

    def post(self, request, *args, **kwargs):
        # Verifica si el usuario es un jugador
        if not hasattr(request.user, 'jugador'):
            messages.error(request, "Solo los jugadores pueden realizar pagos.")
            return redirect('player_home')

        # Obtiene el ID del equipo
        equipo_id = self.kwargs.get('equipo_id')
        try:
            equipo = Equipo.objects.get(id=equipo_id)
            if equipo.creado_por != request.user.jugador and equipo.miembros.filter(id=request.user.jugador.id).count() == 0:
                messages.error(request, "Solo los miembros de este equipo pueden realizar pagos.")
                return redirect('player_home')
        except Equipo.DoesNotExist:
            messages.error(request, "No se encontró el equipo.")
            return redirect('player_home')

        # Obtiene el archivo de comprobante de pago (único archivo)
        comprobante_pago = request.FILES.get('comprobante_pago')

        if not comprobante_pago:
            messages.error(request, "Debes adjuntar un comprobante de pago.")
            return render(request, self.template_name, {'equipo': equipo})

        # Validación del tipo de archivo
        try:
            kind = filetype.guess(comprobante_pago.read(1024))  # Analiza los primeros bytes
            if kind is None or kind.mime not in ['image/jpeg', 'image/jpg', 'image/png', 'application/zip', 'application/x-rar-compressed']:
                raise ValidationError("Tipo de archivo no permitido para el comprobante de pago.")
            
            # Guarda el comprobante de pago
            equipo.comprobante_pago = comprobante_pago
            equipo.estadoAprobacion = EstadoAprobacion.EN_REVISION
            equipo.save()

            # Mensaje de éxito
            messages.success(request, "Comprobante de pago subido exitosamente. Tu equipo está en revisión.")
            return redirect('player_home')

        except ValidationError as e:
            messages.error(request, str(e), extra_tags='error-tipo-archivo')
            return render(request, self.template_name, {'equipo': equipo, 'messages': messages.get_messages(request)})

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
            return JsonResponse({'warning': "El jugador ya ha recibido una invitación para este equipo."}, status=200)

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
            messages.warning(request, "Esta invitación ya ha sido aceptada.", extra_tags='invitacion')
            return redirect('player_home')

        # Verifica que el jugador no esté ya en un equipo
        if invitacion.jugador_invitado.equipo:
            messages.warning(request, "Ya perteneces a un equipo.", extra_tags='invitacion')
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
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Equipo, Invitacion, Jugador
from threading import Thread

def enviar_correo_thread(subject, body, recipient_list):
    def _send():
        send_mail(
            subject=subject,
            message=body,
            html_message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
        )
    Thread(target=_send).start()

@receiver(post_save, sender=Jugador)
def enviar_correo_bienvenida(sender, instance, created, **kwargs):
    if created:
        subject = "¡Bienvenido a Torneo Esports!"
        body = f"""
        <h1>Hola {instance.nombre},</h1>
        <p>
            Te damos la bienvenida al <strong>Torneo Liga Leyendas del Sur</strong>. Tu registro ha sido exitoso.
        </p>
        <p>
            Ahora puedes iniciar sesión y comenzar a disfrutar de todas las funcionalidades de la plataforma.
        </p>
        <p>
            Si tienes alguna duda o necesitas ayuda, no dudes en contactarnos a <strong>esports@frlp.utn.edu.ar</strong> o por nuestras redes.
        </p>
        <p>
            ¡Gracias por unirte a nosotros!
        </p>
        <p>
            Saludos, el<strong> Equipo del Torneo Liga Leyendas del Sur</strong>
        </p>
        """
        enviar_correo_thread(subject, body, [instance.email])

@receiver(post_save, sender=Invitacion)
def enviar_correo_invitacion(sender, instance, created, **kwargs):
    if created:
        equipo = instance.equipo
        jugador_invitado = instance.jugador_invitado

        subject = f"Invitación para unirse al equipo {equipo.nombre}"
        body = f"""
        <h1>Hola {jugador_invitado.nombre},</h1>
        <p>
            Has recibido una invitación para unirte al equipo <strong>{equipo.nombre}</strong>.
        </p>
        <p>
            Para aceptar la invitación, inicia sesión en tu cuenta y revisa la sección de invitaciones.
        </p>
        <p>
            ¡Esperamos verte en el equipo!
        </p>
        <p>
            Saludos, el<strong> Equipo del Torneo Liga Leyendas del Sur</strong>
        </p>
        """
        enviar_correo_thread(subject, body, [jugador_invitado.email])

@receiver(pre_save, sender=Equipo)
def capturar_estado_original(sender, instance, **kwargs):
    if instance.pk:
        original = Equipo.objects.get(pk=instance.pk)
        instance._original_estadoAprobacion = original.estadoAprobacion
    else:
        instance._original_estadoAprobacion = None

@receiver(post_save, sender=Equipo)
def enviar_correo_cambio_estado(sender, instance, **kwargs):
    if hasattr(instance, '_original_estadoAprobacion') and instance._original_estadoAprobacion is not None:
        if instance.estadoAprobacion != instance._original_estadoAprobacion:
            integrantes = Jugador.objects.filter(equipo=instance)
            for jugador in integrantes:
                subject = f"Estado de aprobación actualizado: {instance.estadoAprobacion}"
                body = f"""
                <h1>Hola {jugador.nombre},</h1>
                <p>
                    Te informamos que el estado de aprobación de tu equipo <strong>{instance.nombre}</strong> ha sido actualizado a:
                </p>
                <p>
                    <strong>{instance.estadoAprobacion}</strong>.
                </p>
                <p>
                    A continuación, detallamos el significado de cada estado:
                </p>
                <ul>
                    <li><strong>Aprobado:</strong> ¡Tu equipo está listo para participar en el torneo! Pronto recibirás más detalles.</li>
                    <li><strong>En revisión:</strong> Estamos revisando la información de tu equipo. Te avisaremos cuando haya novedades.</li>
                    <li><strong>Pago pendiente:</strong> Para completar la inscripción, es necesario que realices el pago correspondiente.</li>
                    <li><strong>Rechazado:</strong> Lamentamos informarte que tu equipo no ha sido aprobado. Si tienes dudas, contáctanos.</li>
                </ul>
                <p>
                    Si necesitas ayuda o tienes alguna pregunta, no dudes en escribirnos a <strong>esports@frlp.utn.edu.ar</strong> o contactarnos por nuestras redes sociales.
                </p>
                <p>
                    ¡Gracias por ser parte de nuestro torneo!
                </p>
                <p>
                    Saludos, el<strong> Equipo del Torneo Liga Leyendas del Sur</strong>
                </p>
                """
                enviar_correo_thread(subject, body, [jugador.email])
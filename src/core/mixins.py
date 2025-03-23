from django.core.exceptions import PermissionDenied
from .models import Staff 

class StaffRequiredMixin:
    """
    Mixin que verifica si el usuario tiene una instancia de Staff asociada.
    """
    def dispatch(self, request, *args, **kwargs):
        # Verifica si el usuario está autenticado y tiene una instancia de Staff
        if not request.user.is_authenticated or not hasattr(request.user, 'staff'):
            raise PermissionDenied("No tienes permisos para acceder a esta página.")
        return super().dispatch(request, *args, **kwargs)
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from .models import Entrenador


def es_staff_o_admin(user):
    """Verifica si el usuario es staff o superusuario."""
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(es_staff_o_admin)
def entrenador_list(request):
    """Lista de entrenadores, solo visible para staff y administradores."""
    entrenadores = Entrenador.objects.filter(activo=True).order_by('apellidos', 'nombres')
    return render(request, 'administracion/entrenador_list.html', {
        'entrenadores': entrenadores,
    })

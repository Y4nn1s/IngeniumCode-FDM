from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import RepresentanteSignUpForm


class RepresentanteSignUpView(CreateView):
    """Vista de registro público exclusivo para representantes."""
    form_class = RepresentanteSignUpForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


import os
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@csrf_exempt
@require_http_methods(["GET"])
def create_superuser_temp(request):
    """
    Endpoint TEMPORAL para crear superuser en producción.
    DEBE SER ELIMINADO inmediatamente después de usar.
    Protegido por secret token via env var SETUP_SECRET.
    """
    secret = request.GET.get('token', '')
    expected = os.environ.get('SETUP_SECRET', '')
    if not expected or secret != expected:
        return HttpResponseForbidden('Forbidden')

    username = request.GET.get('username', '')
    email = request.GET.get('email', '')
    password = request.GET.get('password', '')

    if not all([username, email, password]):
        return JsonResponse({'error': 'username, email y password requeridos'}, status=400)

    User = get_user_model()
    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': f'Usuario {username} ya existe'}, status=400)

    user = User.objects.create_superuser(username=username, email=email, password=password)
    return JsonResponse({
        'status': 'created',
        'username': user.username,
        'email': user.email,
        'is_superuser': user.is_superuser,
        'message': 'Superuser creado. ELIMINAR ESTE ENDPOINT INMEDIATAMENTE.'
    })

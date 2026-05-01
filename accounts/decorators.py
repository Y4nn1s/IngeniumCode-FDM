"""
Decoradores helper para control de acceso por rol.
Cada decorador valida que el usuario pertenezca al grupo requerido.
"""
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def _en_grupo(user, nombre_grupo):
    return user.is_authenticated and user.groups.filter(name=nombre_grupo).exists()


def _es_representante(user):
    return (
        user.is_authenticated and
        hasattr(user, 'representante') and
        user.representante is not None
    )


def _forbidden(request):
    return render(request, '403.html', status=403)


def grupo_requerido(nombre_grupo):
    """Decorador genérico para exigir un grupo específico."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if request.user.is_superuser or _en_grupo(request.user, nombre_grupo):
                return view_func(request, *args, **kwargs)
            return _forbidden(request)
        return _wrapped
    return decorator


def cualquier_grupo_requerido(*nombres_grupo):
    """Decorador para exigir al menos uno de varios grupos."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            for nombre in nombres_grupo:
                if _en_grupo(request.user, nombre):
                    return view_func(request, *args, **kwargs)
            return _forbidden(request)
        return _wrapped
    return decorator


# Decoradores específicos por rol
tesoreria_required = grupo_requerido('Tesoreria')
coord_general_required = grupo_requerido('CoordinadorGeneral')
coord_deportivo_required = grupo_requerido('CoordinadorDeportivo')
entrenador_required = grupo_requerido('Entrenador')


def representante_required(view_func):
    """Solo representantes (con perfil Representante asociado)."""
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if _es_representante(request.user):
            return view_func(request, *args, **kwargs)
        return _forbidden(request)
    return _wrapped


def staff_required(view_func):
    """
    Cualquier staff interno: Tesoreria, CoordinadorGeneral,
    CoordinadorDeportivo o Entrenador.
    NO permite representantes.
    """
    return cualquier_grupo_requerido(
        'Tesoreria',
        'CoordinadorGeneral',
        'CoordinadorDeportivo',
        'Entrenador',
    )(view_func)


def lectura_atletas_required(view_func):
    """
    Quien puede VER atletas:
    - Cualquier staff interno
    - Representantes (pero verán solo los suyos vía queryset filtrado)
    """
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        es_staff = request.user.groups.filter(
            name__in=['Tesoreria', 'CoordinadorGeneral',
                      'CoordinadorDeportivo', 'Entrenador']
        ).exists()
        es_representante_obj = (
            hasattr(request.user, 'representante') and
            request.user.representante is not None
        )
        if es_staff or es_representante_obj:
            return view_func(request, *args, **kwargs)
        return _forbidden(request)
    return _wrapped


def edicion_atletas_required(view_func):
    """
    Quien puede CREAR/EDITAR/BORRAR atletas:
    Solo CoordinadorGeneral, CoordinadorDeportivo y superuser.
    """
    return cualquier_grupo_requerido(
        'CoordinadorGeneral', 'CoordinadorDeportivo'
    )(view_func)


def edicion_representantes_required(view_func):
    """
    Quien puede CREAR/EDITAR representantes desde el panel:
    Solo CoordinadorGeneral y superuser.
    (El signup público crea representantes vía RepresentanteSignUpForm.)
    """
    return grupo_requerido('CoordinadorGeneral')(view_func)


def gestion_deportiva_required(view_func):
    """
    Quien puede gestionar partidos, evaluaciones, estadísticas:
    CoordinadorGeneral, CoordinadorDeportivo, Entrenador.
    """
    return cualquier_grupo_requerido(
        'CoordinadorGeneral', 'CoordinadorDeportivo', 'Entrenador'
    )(view_func)

import logging

from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.dispatch import receiver

logger = logging.getLogger('security.ratelimit')


def get_client_ip(request):
    """Extrae la IP real del cliente, considerando proxies."""
    if request is None:
        return 'unknown'
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    logger.info(
        'Login exitoso - username: %s - ip: %s',
        user.username,
        get_client_ip(request),
    )


@receiver(user_logged_out)
def on_user_logged_out(sender, request, user, **kwargs):
    username = user.username if user else 'unknown'
    logger.info(
        'Logout - username: %s - ip: %s',
        username,
        get_client_ip(request),
    )


@receiver(user_login_failed)
def on_user_login_failed(sender, credentials, request, **kwargs):
    logger.warning(
        'Login fallido (credenciales incorrectas) - username intentado: %s - ip: %s',
        credentials.get('username', ''),
        get_client_ip(request),
    )

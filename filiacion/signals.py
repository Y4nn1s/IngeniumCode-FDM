import os
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import Atleta

@receiver(post_delete, sender=Atleta)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Borra el archivo de imagen del sistema cuando se borra el objeto Atleta.
    """
    if instance.foto_perfil:
        if os.path.isfile(instance.foto_perfil.path):
            os.remove(instance.foto_perfil.path)

@receiver(pre_save, sender=Atleta)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Borra el archivo antiguo del sistema cuando se actualiza la imagen.
    """
    if not instance.pk:
        return False

    try:
        old_file = Atleta.objects.get(pk=instance.pk).foto_perfil
    except Atleta.DoesNotExist:
        return False

    new_file = instance.foto_perfil
    if not old_file == new_file:
        if old_file and os.path.isfile(old_file.path):
            os.remove(old_file.path)

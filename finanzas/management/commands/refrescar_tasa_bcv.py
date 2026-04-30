# finanzas/management/commands/refrescar_tasa_bcv.py
from django.core.management.base import BaseCommand
from finanzas.services.tasa_bcv import refrescar_tasa_actual


class Command(BaseCommand):
    help = 'Refresca la tasa BCV del día desde DolarAPI.'

    def handle(self, *args, **opts):
        tasa = refrescar_tasa_actual()
        if tasa is None:
            self.stdout.write(self.style.ERROR(
                'No se pudo obtener la tasa. Verifica conectividad con DolarAPI.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'Tasa BCV de hoy actualizada: {tasa} Bs/USD'
            ))

from django import forms
from django.core.exceptions import ValidationError
from .models import Partido


class PartidoProgramarForm(forms.ModelForm):
    """Formulario para programar un partido futuro (sin resultados)."""
    class Meta:
        model = Partido
        fields = ['fecha_hora', 'equipo_rival', 'tipo', 'condicion']
        widgets = {
            'fecha_hora': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'equipo_rival': forms.TextInput(attrs={'placeholder': 'Nombre del equipo rival'}),
        }

    def clean_equipo_rival(self):
        rival = self.cleaned_data.get('equipo_rival', '')
        if len(rival) < 3:
            raise ValidationError("El nombre del equipo debe tener al menos 3 caracteres.")
        return rival


class PartidoResultadoForm(forms.ModelForm):
    """Formulario para registrar el resultado de un partido ya jugado."""
    class Meta:
        model = Partido
        fields = ['goles_favor_escuela', 'goles_contra_rival']
        widgets = {
            'goles_favor_escuela': forms.NumberInput(attrs={'min': '0', 'max': '50'}),
            'goles_contra_rival': forms.NumberInput(attrs={'min': '0', 'max': '50'}),
        }
        labels = {
            'goles_favor_escuela': 'Goles a Favor (FDM)',
            'goles_contra_rival': 'Goles en Contra (Rival)',
        }


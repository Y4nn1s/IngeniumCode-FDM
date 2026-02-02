from django import forms
from django.core.exceptions import ValidationError
from .models import Partido


class PartidoProgramarForm(forms.ModelForm):
    """Formulario para programar un partido futuro (sin resultados)."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        input_classes = 'shadow-sm bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': input_classes})

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        input_classes = 'shadow-sm bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': input_classes})

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


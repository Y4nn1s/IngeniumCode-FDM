from django import forms
from django.core.exceptions import ValidationError

from .models import Entrenador


class EntrenadorForm(forms.ModelForm):
    """Formulario para crear/editar Entrenador."""
    
    class Meta:
        model = Entrenador
        fields = ['nombres', 'apellidos', 'licencia', 'telefono', 'coordinador', 'activo']
        widgets = {
            'nombres': forms.TextInput(attrs={
                'class': 'form-input w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'placeholder': 'Nombre del entrenador'
            }),
            'apellidos': forms.TextInput(attrs={
                'class': 'form-input w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'placeholder': 'Apellido del entrenador'
            }),
            'licencia': forms.Select(attrs={
                'class': 'form-select w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-input w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'inputmode': 'numeric',
                'pattern': '[0-9]*',
                'maxlength': '11',
                'placeholder': '04141234567'
            }),
            'coordinador': forms.Select(attrs={
                'class': 'form-select w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-indigo-600'
            }),
        }
        labels = {
            'nombres': 'Nombres',
            'apellidos': 'Apellidos',
            'licencia': 'Tipo de Licencia',
            'telefono': 'Teléfono',
            'coordinador': 'Coordinador a Cargo',
            'activo': 'Activo',
        }

    def clean_telefono(self):
        """Valida que el teléfono tenga 11 dígitos."""
        tel = self.cleaned_data.get('telefono', '')
        if not tel.isdigit():
            raise ValidationError("El teléfono debe contener solo números.")
        if len(tel) != 11:
            raise ValidationError("El teléfono debe tener 11 dígitos (ej: 04141234567).")
        return tel

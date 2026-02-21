from django import forms
from django.core.exceptions import ValidationError

from .models import Entrenador


class EntrenadorForm(forms.ModelForm):
    """Formulario para crear/editar Entrenador."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        input_classes = 'appearance-none block w-full bg-white dark:bg-slate-700 text-gray-700 dark:text-gray-200 border border-gray-200 dark:border-slate-600 rounded py-2 px-4 leading-tight focus:outline-none focus:bg-white dark:focus:bg-slate-600 focus:border-blue-500'
        checkbox_classes = 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500' # Tailwind for checkbox
        
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': checkbox_classes})
            else:
                field.widget.attrs.update({'class': input_classes})

    class Meta:
        model = Entrenador
        fields = ['nombres', 'apellidos', 'licencia', 'telefono', 'coordinador', 'activo']
        widgets = {
            'nombres': forms.TextInput(attrs={'placeholder': 'Nombre del entrenador'}),
            'apellidos': forms.TextInput(attrs={'placeholder': 'Apellido del entrenador'}),
            'telefono': forms.TextInput(attrs={'inputmode': 'numeric', 'pattern': '[0-9]*', 'maxlength': '11', 'placeholder': '04141234567'}),
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

from django import forms
from django.core.exceptions import ValidationError

from .models import Personal
from core.models import CatCargo


class EntrenadorForm(forms.ModelForm):
    """Formulario para crear/editar Personal con rol Entrenador."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        input_classes = 'appearance-none block w-full bg-white dark:bg-slate-700 text-gray-700 dark:text-gray-200 border border-gray-200 dark:border-slate-600 rounded py-2 px-4 leading-tight focus:outline-none focus:bg-white dark:focus:bg-slate-600 focus:border-blue-500'
        checkbox_classes = 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500'
        
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': checkbox_classes})
            else:
                field.widget.attrs.update({'class': input_classes})

    class Meta:
        model = Personal
        fields = ['cedula_identidad', 'nombres', 'apellidos', 'licencia', 'telefono', 'activo']
        widgets = {
            'cedula_identidad': forms.TextInput(attrs={'placeholder': 'V-12345678'}),
            'nombres': forms.TextInput(attrs={'placeholder': 'Nombre del entrenador'}),
            'apellidos': forms.TextInput(attrs={'placeholder': 'Apellido del entrenador'}),
            'telefono': forms.TextInput(attrs={'inputmode': 'numeric', 'pattern': '[0-9]*', 'maxlength': '11', 'placeholder': '04141234567'}),
        }
        labels = {
            'cedula_identidad': 'Cédula de Identidad',
            'nombres': 'Nombres',
            'apellidos': 'Apellidos',
            'licencia': 'Tipo de Licencia',
            'telefono': 'Teléfono',
            'activo': 'Activo',
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        cargo_entrenador, _ = CatCargo.objects.get_or_create(
            nombre='Entrenador',
            defaults={'descripcion': 'Personal técnico encargado del entrenamiento'}
        )
        instance.cargo = cargo_entrenador
        if commit:
            instance.save()
        return instance

    def clean_telefono(self):
        tel = self.cleaned_data.get('telefono', '')
        if tel and not tel.isdigit():
            raise ValidationError("El teléfono debe contener solo números.")
        if tel and len(tel) != 11:
            raise ValidationError("El teléfono debe tener 11 dígitos (ej: 04141234567).")
        return tel

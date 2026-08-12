from datetime import date
from django import forms
from django.core.exceptions import ValidationError
from .models import Atleta, Representante


class RepresentanteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        input_classes = 'appearance-none block w-full bg-white dark:bg-slate-700 text-gray-700 dark:text-gray-200 border border-gray-200 dark:border-slate-600 rounded py-2 px-4 leading-tight focus:outline-none focus:bg-white dark:focus:bg-slate-600 focus:border-blue-500'
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': input_classes})

    class Meta:
        model = Representante
        fields = '__all__'
        widgets = {
            'cedula_identidad': forms.TextInput(attrs={'inputmode': 'numeric', 'pattern': '[0-9]*', 'maxlength': '9', 'minlength': '6'}),
            'telefono_principal': forms.TextInput(attrs={'inputmode': 'numeric', 'pattern': '[0-9]*', 'maxlength': '11', 'placeholder': '04141234567'}),
            'direccion_habitacion': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_cedula_identidad(self):
        ci = self.cleaned_data.get('cedula_identidad', '')
        if ci and not ci.isdigit():
            raise ValidationError("La cédula debe contener solo números.")
        return ci

    def clean_telefono_principal(self):
        tel = self.cleaned_data.get('telefono_principal', '')
        if tel and not tel.isdigit():
            raise ValidationError("El teléfono debe contener solo números.")
        if tel and len(tel) != 11:
            raise ValidationError("El teléfono debe tener 11 dígitos (ej: 04141234567).")
        return tel


class AtletaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        input_classes = 'appearance-none block w-full bg-white dark:bg-slate-700 text-gray-700 dark:text-gray-200 border border-gray-200 dark:border-slate-600 rounded py-2 px-4 leading-tight focus:outline-none focus:bg-white dark:focus:bg-slate-600 focus:border-blue-500'
        file_input_classes = 'block w-full text-sm text-gray-900 dark:text-gray-200 border border-gray-200 dark:border-slate-600 rounded-lg cursor-pointer bg-white dark:bg-slate-700 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500'

        # FKs a catálogos: UX limpia con empty_label en español.
        empty_labels = {
            'representante': 'Seleccione un representante...',
            'categoria': 'Seleccione una categoría...',
            'posicion': 'Seleccione una posición...',
            'lateralidad': 'Seleccione la lateralidad...',
        }
        for field_name, label in empty_labels.items():
            field = self.fields.get(field_name)
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = label

        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs.update({'class': file_input_classes})
            elif not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': input_classes})

    class Meta:
        model = Atleta
        fields = '__all__'
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'cedula_identidad': forms.TextInput(attrs={'inputmode': 'numeric', 'pattern': '[0-9]*', 'maxlength': '9'}),
            'peso_kg': forms.NumberInput(attrs={'step': '0.01', 'min': '10', 'max': '120'}),
            'altura_mts': forms.NumberInput(attrs={'step': '0.01', 'min': '0.50', 'max': '2.50'}),
            'foto_perfil': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }

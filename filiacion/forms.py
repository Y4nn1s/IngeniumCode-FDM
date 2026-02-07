from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import Atleta, Representante


class RepresentanteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        input_classes = 'shadow-sm bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': input_classes})

    class Meta:
        model = Representante
        fields = '__all__'
        widgets = {
            'cedula_identidad': forms.TextInput(attrs={'inputmode': 'numeric', 'pattern': '[0-9]*', 'maxlength': '8', 'minlength': '8'}),
            'telefono_principal': forms.TextInput(attrs={'inputmode': 'numeric', 'pattern': '[0-9]*', 'maxlength': '11', 'placeholder': '04141234567'}),
            'direccion_habitacion': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_cedula_identidad(self):
        ci = self.cleaned_data.get('cedula_identidad', '')
        if not ci.isdigit():
            raise ValidationError("La cédula debe contener solo números.")
        if len(ci) != 8:
            raise ValidationError("La cédula debe tener exactamente 8 dígitos.")
        return ci

    def clean_telefono_principal(self):
        tel = self.cleaned_data.get('telefono_principal', '')
        if not tel.isdigit():
            raise ValidationError("El teléfono debe contener solo números.")
        if len(tel) != 11:
            raise ValidationError("El teléfono debe tener 11 dígitos (ej: 04141234567).")
        return tel


class AtletaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        input_classes = 'appearance-none block w-full bg-white text-gray-700 border border-gray-200 rounded py-2 px-4 leading-tight focus:outline-none focus:bg-white focus:border-blue-500'
        file_input_classes = 'block w-full text-sm text-gray-900 border border-gray-200 rounded-lg cursor-pointer bg-white file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500'

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
            'cedula_escolar': forms.TextInput(attrs={'inputmode': 'numeric', 'pattern': '[0-9]*', 'maxlength': '8', 'minlength': '8'}),
            'peso_kg': forms.NumberInput(attrs={
                'step': '0.01', 
                'min': '10', 
                'max': '200',
                'oninput': 'if(this.value.length > 3) this.value = this.value.slice(0, 3);'
            }),
            'altura_mts': forms.NumberInput(attrs={'step': '0.01', 'min': '0.50', 'max': '2.50'}),
            'foto_perfil': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }

    def clean_cedula_escolar(self):
        ce = self.cleaned_data.get('cedula_escolar')
        if ce:
            if not ce.isdigit():
                raise ValidationError("La cédula escolar debe contener solo números.")
            if len(ce) != 8:
                raise ValidationError("La cédula escolar debe tener exactamente 8 dígitos.")
        return ce

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get('fecha_nacimiento')
        if fecha:
            hoy = date.today()
            if fecha > hoy:
                raise ValidationError("La fecha de nacimiento no puede ser en el futuro.")
            edad = (hoy - fecha).days // 365
            if edad > 18:
                raise ValidationError("El atleta no puede tener más de 18 años.")
            if edad < 3:
                raise ValidationError("El atleta debe tener al menos 3 años.")
        return fecha

    def clean_peso_kg(self):
        peso = self.cleaned_data.get('peso_kg')
        if peso is not None:
            if peso < 10 or peso > 200:
                raise ValidationError("El peso debe estar entre 10 y 200 kg.")
        return peso

    def clean_altura_mts(self):
        altura = self.cleaned_data.get('altura_mts')
        if altura is not None:
            if altura < 0.50 or altura > 2.50:
                raise ValidationError("La altura debe estar entre 0.50 y 2.50 metros.")
        return altura


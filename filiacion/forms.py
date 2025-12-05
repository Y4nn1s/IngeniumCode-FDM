from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import Atleta, Representante


class RepresentanteForm(forms.ModelForm):
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


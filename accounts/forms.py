from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class StaffOnlyAuthenticationForm(AuthenticationForm):
    """
    Login restringido a usuarios con is_staff=True.
    Los representantes y usuarios externos no pueden iniciar sesión.
    """

    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': (
            'Credenciales incorrectas. Verifica tu usuario y contraseña.'
        ),
        'inactive': 'Esta cuenta está desactivada.',
        'no_staff': 'Esta cuenta no tiene acceso a la plataforma interna.',
    }

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise ValidationError(
                self.error_messages['no_staff'],
                code='no_staff',
            )


class RepresentanteSignUpForm(UserCreationForm):
    """
    Formulario de registro público exclusivo para representantes.
    Fuerza is_staff=False e is_superuser=False por seguridad.
    """

    first_name = forms.CharField(
        max_length=150,
        required=True,
        label='Nombres',
        widget=forms.TextInput(attrs={'autocomplete': 'given-name'}),
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label='Apellidos',
        widget=forms.TextInput(attrs={'autocomplete': 'family-name'}),
    )
    email = forms.EmailField(
        required=True,
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={'autocomplete': 'email'}),
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',
                  'password1', 'password2')
        labels = {
            'username': 'Cédula de Identidad (Ej. V12345678)',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
        return user

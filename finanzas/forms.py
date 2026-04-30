# finanzas/forms.py
from django import forms
from django.utils import timezone
from .models import Pago, Mensualidad

# Clases Tailwind reutilizables para inputs del formulario
INPUT_CSS = 'w-full px-3 py-2 border rounded-lg text-sm dark:bg-slate-800 dark:border-slate-600 dark:text-gray-200 focus:ring-2 focus:ring-fdm-blue focus:border-fdm-blue'
SELECT_CSS = INPUT_CSS
TEXTAREA_CSS = INPUT_CSS


class ReportarPagoForm(forms.ModelForm):
    mensualidades = forms.ModelMultipleChoiceField(
        queryset=Mensualidad.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Selecciona qué mensualidades cubre este pago"
    )

    class Meta:
        model = Pago
        fields = [
            'metodo', 'banco_emisor', 'referencia',
            'monto_bs', 'fecha_pago', 'comprobante'
        ]
        widgets = {
            'metodo': forms.Select(attrs={'class': SELECT_CSS}),
            'banco_emisor': forms.Select(attrs={'class': SELECT_CSS}),
            'referencia': forms.TextInput(attrs={'class': INPUT_CSS, 'placeholder': 'Nro. de referencia'}),
            'monto_bs': forms.NumberInput(attrs={'class': INPUT_CSS, 'placeholder': '0.00', 'step': '0.01'}),
            'fecha_pago': forms.DateInput(attrs={'type': 'date', 'class': INPUT_CSS}),
            'comprobante': forms.ClearableFileInput(attrs={'class': INPUT_CSS}),
        }

    def __init__(self, *args, **kwargs):
        representante = kwargs.pop('representante', None)
        super().__init__(*args, **kwargs)
        if representante:
            atletas = representante.atletas.filter(activo=True)
            qs = Mensualidad.objects.filter(
                atleta__in=atletas, pagada=False
            ).select_related('atleta').order_by('fecha_vencimiento')
            self.fields['mensualidades'].queryset = qs
            # Etiqueta enriquecida con monto USD
            self.fields['mensualidades'].label_from_instance = (
                lambda m: f"{m.atleta.nombres} {m.atleta.apellidos} — {m.etiqueta_periodo} (${m.monto_usd})"
            )

    def clean_comprobante(self):
        f = self.cleaned_data['comprobante']
        if f.size > 5 * 1024 * 1024:
            raise forms.ValidationError('El comprobante no puede superar 5MB.')
        ext = f.name.lower().rsplit('.', 1)[-1]
        if ext not in ('jpg', 'jpeg', 'png', 'pdf'):
            raise forms.ValidationError('Solo se aceptan archivos JPG, PNG o PDF.')
        return f

    def clean_fecha_pago(self):
        fecha = self.cleaned_data['fecha_pago']
        if fecha > timezone.now().date():
            raise forms.ValidationError('La fecha de pago no puede ser futura.')
        return fecha

    def clean(self):
        cleaned = super().clean()
        ref = cleaned.get('referencia')
        banco = cleaned.get('banco_emisor')
        if ref and banco:
            existe = Pago.objects.filter(
                banco_emisor=banco,
                referencia=ref,
                estado__in=['PENDIENTE', 'APROBADO']
            ).exists()
            if existe:
                raise forms.ValidationError(
                    f'Ya existe un pago activo con referencia {ref} de ese banco.'
                )
        return cleaned


class AprobarPagoForm(forms.Form):
    tasa_bcv = forms.DecimalField(
        max_digits=12, decimal_places=4, min_value=0,
        help_text='Tasa BCV del día del pago (Bs por USD)',
        widget=forms.NumberInput(attrs={
            'class': INPUT_CSS,
            'placeholder': 'Ej: 36.5000',
            'step': '0.0001',
        })
    )


class RechazarPagoForm(forms.Form):
    motivo = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': TEXTAREA_CSS, 'placeholder': 'Motivo del rechazo...'}),
        max_length=500,
        help_text='Explica al representante por qué se rechaza.'
    )

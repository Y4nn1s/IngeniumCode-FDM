from django import forms
from django.core.exceptions import ValidationError
from .models import Estadistica, Partido, EvaluacionTecnica, EvaluacionPsicosocial


# --- Clases de estilos Tailwind para inputs compactos (uso en tablas) ---
TAILWIND_COMPACT_NUMBER = (
    'w-16 text-center bg-gray-50 border border-gray-300 text-gray-900 '
    'text-sm rounded focus:ring-blue-500 focus:border-blue-500 p-1.5'
)
TAILWIND_COMPACT_CHECKBOX = (
    'w-5 h-5 text-blue-600 bg-gray-100 border-gray-300 rounded '
    'focus:ring-blue-500 focus:ring-2'
)





class PartidoProgramarForm(forms.ModelForm):
    """Formulario para programar un partido futuro (sin resultados)."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        input_classes = 'shadow-sm bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': input_classes})

    class Meta:
        model = Partido
        fields = ['categoria', 'fecha_hora', 'equipo_rival', 'tipo', 'condicion']
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


class EvaluacionTecnicaForm(forms.ModelForm):
    """Formulario para registrar evaluación técnica de un atleta."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        input_classes = 'shadow-sm bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        textarea_classes = input_classes + ' h-24' # Extend input for textarea
        
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': textarea_classes})
            elif not isinstance(field.widget, forms.CheckboxInput): 
                field.widget.attrs.update({'class': input_classes})

    class Meta:
        model = EvaluacionTecnica
        fields = [
            'atleta', 'entrenador', 'fecha_evaluacion',
            'velocidad', 'resistencia', 'control_balon',
            'pase_corto', 'tiro', 'inteligencia_tactica', 'observaciones'
        ]
        widgets = {
            'fecha_evaluacion': forms.DateInput(attrs={'type': 'date'}), # Type date preserved
        }


class EvaluacionPsicosocialForm(forms.ModelForm):
    """Formulario para registrar evaluación psicosocial de un atleta."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        input_classes = 'shadow-sm bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        textarea_classes = input_classes + ' h-24' # Extend input for textarea

        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': textarea_classes})
            elif not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': input_classes})

    class Meta:
        model = EvaluacionPsicosocial
        fields = [
            'atleta', 'coordinador_evaluador', 'fecha_evaluacion',
            'compromiso', 'puntualidad', 'companerismo',
            'respeto', 'manejo_frustracion', 'observaciones_conductuales'
        ]
        widgets = {
            'fecha_evaluacion': forms.DateInput(attrs={'type': 'date'}), # Type date preserved
        }


class EstadisticaForm(forms.ModelForm):
    """Formulario fila para estadísticas individuales de un atleta en un partido."""
    class Meta:
        model = Estadistica
        fields = [
            'es_titular', 'goles', 'asistencias',
            'tarjetas_amarillas', 'tarjetas_rojas', 'calificacion_dt'
        ]
        widgets = {
            'es_titular': forms.CheckboxInput(attrs={
                'class': TAILWIND_COMPACT_CHECKBOX
            }),
            'goles': forms.NumberInput(attrs={
                'class': TAILWIND_COMPACT_NUMBER,
                'min': '0', 'max': '20'
            }),
            'asistencias': forms.NumberInput(attrs={
                'class': TAILWIND_COMPACT_NUMBER,
                'min': '0', 'max': '20'
            }),
            'tarjetas_amarillas': forms.NumberInput(attrs={
                'class': TAILWIND_COMPACT_NUMBER,
                'min': '0', 'max': '2'
            }),
            'tarjetas_rojas': forms.NumberInput(attrs={
                'class': TAILWIND_COMPACT_NUMBER,
                'min': '0', 'max': '1'
            }),
            'calificacion_dt': forms.NumberInput(attrs={
                'class': TAILWIND_COMPACT_NUMBER,
                'min': '1', 'max': '10'
            }),
        }
        labels = {
            'es_titular': 'Titular',
            'goles': 'Goles',
            'asistencias': 'Asist.',
            'tarjetas_amarillas': '🟨',
            'tarjetas_rojas': '🟥',
            'calificacion_dt': 'Nota',
        }

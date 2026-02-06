from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, UpdateView, TemplateView

from filiacion.models import Atleta
from .forms import (
    EvaluacionPsicosocialForm,
    EvaluacionTecnicaForm,
    EstadisticaForm,
    PartidoProgramarForm,
    PartidoResultadoForm,
)
from .models import Estadistica, EvaluacionPsicosocial, EvaluacionTecnica, Partido


@login_required
def partido_list(request):
    partidos_pendientes = Partido.objects.filter(procesado=False).order_by('fecha_hora')
    partidos_jugados = Partido.objects.filter(procesado=True).order_by('-fecha_hora')
    return render(request, 'deportivo/partido_list.html', {
        'partidos_pendientes': partidos_pendientes,
        'partidos_jugados': partidos_jugados,
    })


@login_required
def partido_detail(request, pk):
    """Ver detalles de un partido y sus estadísticas."""
    partido = get_object_or_404(Partido, pk=pk)
    estadisticas = partido.estadisticas.select_related('atleta').order_by(
        '-es_titular', '-goles', 'atleta__apellidos'
    )
    
    # Calcular resumen de estadísticas
    resumen = {
        'total_goles': sum(e.goles for e in estadisticas),
        'total_asistencias': sum(e.asistencias for e in estadisticas),
        'total_amarillas': sum(e.tarjetas_amarillas for e in estadisticas),
        'total_rojas': sum(e.tarjetas_rojas for e in estadisticas),
        'titulares': sum(1 for e in estadisticas if e.es_titular),
    }
    
    return render(request, 'deportivo/partido_detail.html', {
        'partido': partido,
        'estadisticas': estadisticas,
        'resumen': resumen,
    })


@login_required
def partido_create(request):
    """Programar un nuevo partido (futuro)."""
    if request.method == 'POST':
        form = PartidoProgramarForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('partido_list')
    else:
        form = PartidoProgramarForm()
    return render(request, 'deportivo/partido_form.html', {
        'form': form,
        'titulo': 'Programar Partido'
    })


@login_required
def partido_registrar_resultado(request, pk):
    """Registrar el resultado de un partido con estadísticas individuales por atleta."""
    partido = get_object_or_404(Partido, pk=pk)
    
    if partido.procesado:
        return redirect('partido_list')
    
    # Obtener atletas activos de la categoría del partido
    atletas_categoria = Atleta.objects.filter(
        categoria=partido.categoria,
        activo=True
    ).order_by('apellidos', 'nombres')
    
    # Crear el formset factory
    EstadisticaFormSet = modelformset_factory(
        Estadistica,
        form=EstadisticaForm,
        extra=0,
        can_delete=False
    )
    
    # Verificar si ya existen estadísticas para este partido
    estadisticas_existentes = Estadistica.objects.filter(partido=partido)
    
    if request.method == 'POST':
        form = PartidoResultadoForm(request.POST, instance=partido)
        formset = EstadisticaFormSet(request.POST, prefix='estadisticas')
        
        if form.is_valid() and formset.is_valid():
            # Guardar estadísticas individuales
            total_goles_fdm = 0
            for i, estadistica_form in enumerate(formset):
                if estadistica_form.cleaned_data:
                    estadistica = estadistica_form.save(commit=False)
                    estadistica.partido = partido
                    # Asignar atleta desde la lista ordenada
                    if not estadistica.pk:  # Solo si es nuevo
                        estadistica.atleta = atletas_categoria[i]
                    estadistica.save()
                    total_goles_fdm += estadistica.goles
            
            # Guardar resultado del partido
            partido = form.save(commit=False)
            # Calcular goles a favor desde las estadísticas individuales
            partido.goles_favor_escuela = total_goles_fdm
            
            # Determinar resultado automáticamente
            gf = partido.goles_favor_escuela
            gc = partido.goles_contra_rival
            if gf > gc:
                partido.resultado = 'VICTORIA'
            elif gf < gc:
                partido.resultado = 'DERROTA'
            else:
                partido.resultado = 'EMPATE'
            partido.procesado = True
            partido.save()
            
            return redirect('partido_list')
    else:
        form = PartidoResultadoForm(instance=partido)
        
        if estadisticas_existentes.exists():
            # Cargar estadísticas existentes ordenadas igual que atletas_categoria
            formset = EstadisticaFormSet(
                queryset=estadisticas_existentes.order_by('atleta__apellidos', 'atleta__nombres'),
                prefix='estadisticas'
            )
        else:
            # Inicializar formset vacío con datos iniciales para cada atleta
            initial_data = [
                {'goles': 0, 'asistencias': 0, 'tarjetas_amarillas': 0,
                 'tarjetas_rojas': 0, 'calificacion_dt': 5, 'es_titular': False}
                for _ in atletas_categoria
            ]
            EstadisticaFormSet = modelformset_factory(
                Estadistica,
                form=EstadisticaForm,
                extra=len(atletas_categoria),
                can_delete=False
            )
            formset = EstadisticaFormSet(
                queryset=Estadistica.objects.none(),
                prefix='estadisticas',
                initial=initial_data
            )
    
    # Emparejar atletas con formularios para el template
    atletas_con_forms = list(zip(atletas_categoria, formset))
    
    return render(request, 'deportivo/partido_resultado_form.html', {
        'form': form,
        'formset': formset,
        'atletas_con_forms': atletas_con_forms,
        'partido': partido,
        'titulo': f'Resultado: FDM vs {partido.equipo_rival}'
    })


# --- Vistas para Evaluaciones ---


class EvaluacionTecnicaCreateView(LoginRequiredMixin, CreateView):
    model = EvaluacionTecnica
    form_class = EvaluacionTecnicaForm
    template_name = 'deportivo/evaluacion_tecnica_form.html'

    def get_success_url(self):
        return reverse('atleta_detail', kwargs={'pk': self.object.atleta.pk})


class EvaluacionTecnicaUpdateView(LoginRequiredMixin, UpdateView):
    model = EvaluacionTecnica
    form_class = EvaluacionTecnicaForm
    template_name = 'deportivo/evaluacion_tecnica_form.html'

    def get_success_url(self):
        return reverse('atleta_detail', kwargs={'pk': self.object.atleta.pk})


class EvaluacionPsicosocialCreateView(LoginRequiredMixin, CreateView):
    model = EvaluacionPsicosocial
    form_class = EvaluacionPsicosocialForm
    template_name = 'deportivo/evaluacion_psicosocial_form.html'

    def get_success_url(self):
        return reverse('atleta_detail', kwargs={'pk': self.object.atleta.pk})


class EvaluacionPsicosocialUpdateView(LoginRequiredMixin, UpdateView):
    model = EvaluacionPsicosocial
    form_class = EvaluacionPsicosocialForm
    template_name = 'deportivo/evaluacion_psicosocial_form.html'

    def get_success_url(self):
        return reverse('atleta_detail', kwargs={'pk': self.object.atleta.pk})


# --- Vista de Panel de Estadísticas ---


class EstadisticasView(LoginRequiredMixin, TemplateView):
    """Panel de estadísticas acumuladas de atletas."""
    template_name = 'deportivo/estadisticas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Top 10 goleadores
        context['top_goleadores'] = Estadistica.objects.values(
            'atleta__pk',
            'atleta__nombres',
            'atleta__apellidos',
            'atleta__categoria__nombre',
            'atleta__foto_perfil'
        ).annotate(
            total_goles=Sum('goles')
        ).filter(
            total_goles__gt=0
        ).order_by('-total_goles')[:10]
        
        # Top 10 asistentes
        context['top_asistentes'] = Estadistica.objects.values(
            'atleta__pk',
            'atleta__nombres',
            'atleta__apellidos',
            'atleta__categoria__nombre',
            'atleta__foto_perfil'
        ).annotate(
            total_asistencias=Sum('asistencias')
        ).filter(
            total_asistencias__gt=0
        ).order_by('-total_asistencias')[:10]
        
        # Tarjetas acumuladas (disciplina)
        context['tarjetas_acumuladas'] = Estadistica.objects.values(
            'atleta__pk',
            'atleta__nombres',
            'atleta__apellidos',
            'atleta__categoria__nombre',
            'atleta__foto_perfil'
        ).annotate(
            total_amarillas=Sum('tarjetas_amarillas'),
            total_rojas=Sum('tarjetas_rojas')
        ).filter(
            total_amarillas__gt=0
        ).order_by('-total_rojas', '-total_amarillas')[:10]
        
        # Estadísticas generales
        context['total_partidos'] = Partido.objects.filter(procesado=True).count()
        context['total_victorias'] = Partido.objects.filter(
            procesado=True, resultado='VICTORIA'
        ).count()
        context['total_empates'] = Partido.objects.filter(
            procesado=True, resultado='EMPATE'
        ).count()
        context['total_derrotas'] = Partido.objects.filter(
            procesado=True, resultado='DERROTA'
        ).count()
        
        return context


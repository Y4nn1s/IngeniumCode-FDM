from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, UpdateView

from .forms import (
    EvaluacionPsicosocialForm,
    EvaluacionTecnicaForm,
    PartidoProgramarForm,
    PartidoResultadoForm,
)
from .models import EvaluacionPsicosocial, EvaluacionTecnica, Partido


def partido_list(request):
    partidos_pendientes = Partido.objects.filter(procesado=False).order_by('fecha_hora')
    partidos_jugados = Partido.objects.filter(procesado=True).order_by('-fecha_hora')
    return render(request, 'deportivo/partido_list.html', {
        'partidos_pendientes': partidos_pendientes,
        'partidos_jugados': partidos_jugados,
    })


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


def partido_registrar_resultado(request, pk):
    """Registrar el resultado de un partido ya jugado."""
    partido = get_object_or_404(Partido, pk=pk)
    
    if partido.procesado:
        return redirect('partido_list')
    
    if request.method == 'POST':
        form = PartidoResultadoForm(request.POST, instance=partido)
        if form.is_valid():
            partido = form.save(commit=False)
            # Calcular resultado automáticamente
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
    
    return render(request, 'deportivo/partido_resultado_form.html', {
        'form': form,
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

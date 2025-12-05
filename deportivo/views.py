from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Partido
from .forms import PartidoProgramarForm, PartidoResultadoForm


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


from django.shortcuts import render, get_object_or_404, redirect
from .models import Atleta, Representante
from .forms import AtletaForm, RepresentanteForm

# --- Atletas ---

def atleta_list(request):
    atletas = Atleta.objects.all().order_by('apellidos')
    return render(request, 'filiacion/atleta_list.html', {'atletas': atletas})

def atleta_detail(request, pk):
    atleta = get_object_or_404(Atleta, pk=pk)
    return render(request, 'filiacion/atleta_detail.html', {'atleta': atleta})

def atleta_create(request):
    if request.method == 'POST':
        form = AtletaForm(request.POST, request.FILES)
        if form.is_valid():
            atleta = form.save()
            return redirect('atleta_detail', pk=atleta.pk)
    else:
        form = AtletaForm()
    return render(request, 'filiacion/atleta_form.html', {'form': form, 'titulo': 'Nuevo Atleta'})

def atleta_update(request, pk):
    atleta = get_object_or_404(Atleta, pk=pk)
    if request.method == 'POST':
        form = AtletaForm(request.POST, request.FILES, instance=atleta)
        if form.is_valid():
            form.save()
            return redirect('atleta_detail', pk=atleta.pk)
    else:
        form = AtletaForm(instance=atleta)
    return render(request, 'filiacion/atleta_form.html', {'form': form, 'titulo': f'Editar {atleta.nombres}'})

def atleta_delete(request, pk):
    atleta = get_object_or_404(Atleta, pk=pk)
    if request.method == 'POST':
        atleta.delete()
        return redirect('atleta_list')
    return render(request, 'filiacion/atleta_confirm_delete.html', {'atleta': atleta})

# --- Representantes ---

def representante_list(request):
    representantes = Representante.objects.all().order_by('apellidos')
    return render(request, 'filiacion/representante_list.html', {'representantes': representantes})

def representante_create(request):
    if request.method == 'POST':
        form = RepresentanteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('representante_list')
    else:
        form = RepresentanteForm()
    return render(request, 'filiacion/representante_form.html', {'form': form, 'titulo': 'Nuevo Representante'})

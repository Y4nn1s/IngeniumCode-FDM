from django.contrib.auth.decorators import login_required
from accounts.decorators import (
    lectura_atletas_required,
    edicion_atletas_required,
    edicion_representantes_required,
    staff_required,
)
from django.shortcuts import render, get_object_or_404, redirect

def _es_solo_representante(user):
    """True si el usuario es representante puro (no staff, no superuser)."""
    if user.is_superuser:
        return False
    es_staff_interno = user.groups.filter(
        name__in=['Tesoreria', 'CoordinadorGeneral',
                  'CoordinadorDeportivo', 'Entrenador']
    ).exists()
    if es_staff_interno:
        return False
    return hasattr(user, 'representante') and user.representante is not None

def _forbidden(request):
    return render(request, '403.html', status=403)
from django.views import View
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from .models import Atleta, Representante
from .forms import AtletaForm, RepresentanteForm
from .utils import generar_ficha_tecnica_pdf

# --- Atletas ---


@lectura_atletas_required
def atleta_list(request):
    """
    Staff interno ve TODOS los atletas.
    Representantes ven SOLO sus atletas.
    """
    if _es_solo_representante(request.user):
        atletas = Atleta.objects.filter(
            representante=request.user.representante
        ).order_by('apellidos')
    else:
        atletas = Atleta.objects.all().order_by('apellidos')
    return render(request, 'filiacion/atleta_list.html', {'atletas': atletas})


@lectura_atletas_required
def atleta_detail(request, pk):
    """Representantes solo pueden ver sus propios atletas."""
    atleta = get_object_or_404(Atleta, pk=pk)
    if _es_solo_representante(request.user):
        if atleta.representante_id != request.user.representante.id:
            return _forbidden(request)
    return render(request, 'filiacion/atleta_detail.html', {'atleta': atleta})


@edicion_atletas_required
def atleta_create(request):
    if request.method == 'POST':
        form = AtletaForm(request.POST, request.FILES)
        if form.is_valid():
            atleta = form.save()
            return redirect('atleta_detail', pk=atleta.pk)
    else:
        form = AtletaForm()
    return render(request, 'filiacion/atleta_form.html', {'form': form, 'titulo': 'Nuevo Atleta'})


@edicion_atletas_required
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


@edicion_atletas_required
def atleta_delete(request, pk):
    atleta = get_object_or_404(Atleta, pk=pk)
    if request.method == 'POST':
        atleta.delete()
        return redirect('atleta_list')
    return render(request, 'filiacion/atleta_confirm_delete.html', {'atleta': atleta})

# --- Representantes ---


@staff_required
def representante_list(request):
    """Solo staff interno ve la lista de representantes."""
    representantes = Representante.objects.all().order_by('apellidos')
    return render(request, 'filiacion/representante_list.html', {'representantes': representantes})


@edicion_representantes_required
def representante_create(request):
    if request.method == 'POST':
        form = RepresentanteForm(request.POST)
        if form.is_valid():
            representante = form.save()
            return redirect('representante_detail', pk=representante.pk)
    else:
        form = RepresentanteForm()
    return render(request, 'filiacion/representante_form.html', {'form': form, 'titulo': 'Nuevo Representante'})


@login_required
def representante_detail(request, pk):
    """
    Staff ve cualquier representante.
    Representantes solo ven su propio perfil.
    """
    representante = get_object_or_404(Representante, pk=pk)
    if _es_solo_representante(request.user):
        if representante.id != request.user.representante.id:
            return _forbidden(request)
    return render(request, 'filiacion/representante_detail.html', {'representante': representante})


@edicion_representantes_required
def representante_update(request, pk):
    representante = get_object_or_404(Representante, pk=pk)
    if request.method == 'POST':
        form = RepresentanteForm(request.POST, instance=representante)
        if form.is_valid():
            form.save()
            return redirect('representante_detail', pk=representante.pk)
    else:
        form = RepresentanteForm(instance=representante)
    return render(request, 'filiacion/representante_form.html', {'form': form, 'titulo': f'Editar {representante.nombres}'})

# Vista para descargar ficha técnica en PDF
@method_decorator(lectura_atletas_required, name='dispatch')
class DescargarFichaPDF(View):
    """
    Vista para generar y descargar la ficha técnica de un atleta en PDF.
    Permite especificar evaluaciones específicas mediante parámetros GET.
    """
    def get(self, request, pk):
        # Obtener parámetros opcionales de evaluaciones
        eval_tecnica_id = request.GET.get('eval_tecnica_id')
        eval_psicosocial_id = request.GET.get('eval_psicosocial_id')
        
        # Convertir a int si existen
        if eval_tecnica_id:
            eval_tecnica_id = int(eval_tecnica_id)
        if eval_psicosocial_id:
            eval_psicosocial_id = int(eval_psicosocial_id)
        
        # Generar el PDF
        pdf_bytes = generar_ficha_tecnica_pdf(pk, eval_tecnica_id, eval_psicosocial_id)
        
        # Obtener el nombre del atleta para el archivo
        atleta = get_object_or_404(Atleta, pk=pk)

        # Verificación de permiso para representantes
        if _es_solo_representante(request.user):
            if atleta.representante_id != request.user.representante.id:
                return _forbidden(request)

        filename = f"ficha_tecnica_{atleta.nombres}_{atleta.apellidos}.pdf"
        
        # Crear respuesta HTTP con el PDF
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        
        return response

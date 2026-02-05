from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from .forms import EntrenadorForm
from .models import Entrenador


def es_staff_o_admin(user):
    """Verifica si el usuario es staff o superusuario."""
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(es_staff_o_admin)
def entrenador_list(request):
    """Lista de entrenadores, solo visible para staff y administradores."""
    entrenadores = Entrenador.objects.filter(activo=True).order_by('apellidos', 'nombres')
    return render(request, 'administracion/entrenador_list.html', {
        'entrenadores': entrenadores,
    })


class SuperusuarioRequiredMixin(UserPassesTestMixin):
    """Mixin que restringe el acceso solo a superusuarios."""
    
    def test_func(self):
        return self.request.user.is_superuser


class EntrenadorCreateView(LoginRequiredMixin, SuperusuarioRequiredMixin, CreateView):
    """Vista para crear un nuevo entrenador (solo superusuarios)."""
    model = Entrenador
    form_class = EntrenadorForm
    template_name = 'administracion/entrenador_form.html'
    success_url = reverse_lazy('entrenador_list')

    def form_valid(self, form):
        messages.success(self.request, 'Entrenador creado exitosamente.')
        return super().form_valid(form)


class EntrenadorUpdateView(LoginRequiredMixin, SuperusuarioRequiredMixin, UpdateView):
    """Vista para editar un entrenador existente (solo superusuarios)."""
    model = Entrenador
    form_class = EntrenadorForm
    template_name = 'administracion/entrenador_form.html'
    success_url = reverse_lazy('entrenador_list')

    def form_valid(self, form):
        messages.success(self.request, 'Entrenador actualizado exitosamente.')
        return super().form_valid(form)


class EntrenadorDeleteView(LoginRequiredMixin, SuperusuarioRequiredMixin, DeleteView):
    """Vista para eliminar un entrenador (solo superusuarios)."""
    model = Entrenador
    template_name = 'administracion/entrenador_confirm_delete.html'
    success_url = reverse_lazy('entrenador_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Entrenador eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


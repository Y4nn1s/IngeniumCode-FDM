from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import RepresentanteSignUpForm


class RepresentanteSignUpView(CreateView):
    """Vista de registro público exclusivo para representantes."""
    form_class = RepresentanteSignUpForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

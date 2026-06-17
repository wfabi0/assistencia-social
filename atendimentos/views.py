from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from .models import Atendimento
from .forms import AtendimentoForm

# Create your views here.
class AtendimentoCreateView(CreateView):
    model = Atendimento
    form_class = AtendimentoForm
    template_name = "atendimentos/form.html"
    success_url = reverse_lazy("lista_atendimentos")
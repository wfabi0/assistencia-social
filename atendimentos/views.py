from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from .models import Atendimento
from .forms import AtendimentoForm

# Create your views here.
class AtendimentoListView(ListView):
    model = Atendimento
    template_name = "atendimentos/list.html"
    context_object_name = "atendimentos"
    
    def get_paginate_by(self, queryset):
        return self.request.GET.get("por_pagina", 10)  # padrão 10
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["por_pagina"] = self.request.GET.get("por_pagina", self.get_paginate_by(None))
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("q")
        if search_query:
            queryset = queryset.filter(
                aluno__nome__icontains=search_query
            ) | queryset.filter(
                servidor__nome__icontains=search_query
            ) | queryset.filter(
                usuario_externo__nome__icontains=search_query
            )
        return queryset.order_by("-data_atendimento")

class AtendimentoCreateView(CreateView):
    model = Atendimento
    form_class = AtendimentoForm
    template_name = "atendimentos/form.html"
    success_url = reverse_lazy("lista_atendimentos")

class AtendimentoUpdateView(UpdateView):
    model = Atendimento
    form_class = AtendimentoForm
    template_name = "atendimentos/form.html"
    success_url = reverse_lazy("lista_atendimentos")
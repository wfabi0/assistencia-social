from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from .models import Atendimento
from .forms import AtendimentoForm

# Create your views here.
class AtendimentoListView(ListView):
    model = Atendimento
    template_name = "atendimentos/list.html"
    context_object_name = "atendimentos"
    # paginate_by = 10
    
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
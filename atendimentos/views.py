from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Atendimento
from .forms import AtendimentoForm
from usuarios.models import Aluno, Servidor, UsuarioExterno

# Create your views here.
class AtendimentoListView(LoginRequiredMixin, ListView):
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

class AtendimentoCreateView(LoginRequiredMixin, CreateView):
    model = Atendimento
    form_class = AtendimentoForm
    template_name = "atendimentos/form.html"
    success_url = reverse_lazy("lista_atendimentos")

class AtendimentoUpdateView(LoginRequiredMixin, UpdateView):
    model = Atendimento
    form_class = AtendimentoForm
    template_name = "atendimentos/form.html"
    success_url = reverse_lazy("lista_atendimentos")

class AtendimentoDeleteView(LoginRequiredMixin, DeleteView):
    model = Atendimento
    template_name = "atendimentos/confirm_delete.html"
    success_url = reverse_lazy("lista_atendimentos")

@login_required
def buscar_alunos(request):
    q = request.GET.get("q", "").strip()
    if len(q) < 2:
        return JsonResponse([], safe=False)  # Retorna uma lista vazia se a consulta for muito curta
    alunos = Aluno.objects.filter(
        Q(nome__icontains=q) | Q(ra__icontains=q)
    )
    dados = [{"id": aluno.pk, "texto": f"{aluno.nome} - (RA: {aluno.ra})", "detalhe": aluno.curso} 
            for aluno in alunos]
    return JsonResponse(dados, safe=False)

@login_required
def buscar_servidores(request):
    q = request.GET.get("q", "").strip()
    if len(q) < 2:
        return JsonResponse([], safe=False)
    servidores = Servidor.objects.filter(
        Q(nome__icontains=q) | Q(siape__icontains=q)
    )[:8]
    dados = [
        {"id": s.pk, "texto": f"{s.siape} — {s.nome}", "detalhe": s.cargo}
        for s in servidores
    ]
    return JsonResponse(dados, safe=False)

@login_required
def buscar_usuarios_externos(request):
    q = request.GET.get("q", "").strip()
    if len(q) < 2:
        return JsonResponse([], safe=False)
    usuarios = UsuarioExterno.objects.filter(
        Q(nome__icontains=q) | Q(cpf__icontains=q)
    )[:8]
    dados = [
        {"id": u.pk, "texto": u.nome, "detalhe": u.cpf}
        for u in usuarios
    ]
    return JsonResponse(dados, safe=False)
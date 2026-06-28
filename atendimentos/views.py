from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from .models import Atendimento
from .forms import AtendimentoForm
from usuarios.models import Aluno, Servidor, UsuarioExterno

# --- MIXIN CUSTOMIZADO ---
class CustomPermissionMixin(PermissionRequiredMixin):
    """
    Mixin que redireciona para a home com uma mensagem de erro 
    caso o usuário não tenha a permissão necessária.
    """
    def handle_no_permission(self):
        messages.error(self.request, "Você não tem permissão para acessar esta área.")
        return redirect('home')

# --- VIEWS DE ATENDIMENTO ---

class AtendimentoListView(LoginRequiredMixin, CustomPermissionMixin, ListView):
    permission_required = "atendimentos.view_atendimento"
    model = Atendimento
    template_name = "atendimentos/list.html"
    context_object_name = "atendimentos"
    
    def get_paginate_by(self, queryset):
        return self.request.GET.get("por_pagina", 10)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["por_pagina"] = self.request.GET.get("por_pagina", 10)
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("q")
        if search_query:
            queryset = queryset.filter(
                Q(aluno__nome__icontains=search_query) |
                Q(servidor__nome__icontains=search_query) |
                Q(usuario_externo__nome__icontains=search_query)
            )
        return queryset.order_by("-data_atendimento")

class AtendimentoCreateView(LoginRequiredMixin, CustomPermissionMixin, CreateView):
    permission_required = "atendimentos.add_atendimento"
    model = Atendimento
    form_class = AtendimentoForm
    template_name = "atendimentos/form.html"
    success_url = reverse_lazy("lista_atendimentos")
    
    def form_valid(self, form):
        messages.success(self.request, "Atendimento registrado com sucesso.")
        return super().form_valid(form)

class AtendimentoUpdateView(LoginRequiredMixin, CustomPermissionMixin, UpdateView):
    permission_required = "atendimentos.change_atendimento"
    model = Atendimento
    form_class = AtendimentoForm
    template_name = "atendimentos/form.html"
    success_url = reverse_lazy("lista_atendimentos")
    
    def form_valid(self, form):
        messages.success(self.request, "Atendimento atualizado com sucesso.")
        return super().form_valid(form)

class AtendimentoDeleteView(LoginRequiredMixin, CustomPermissionMixin, DeleteView):
    permission_required = "atendimentos.delete_atendimento"
    model = Atendimento
    template_name = "atendimentos/confirm_delete.html"
    success_url = reverse_lazy("lista_atendimentos")
    
    def form_valid(self, form):
        messages.success(self.request, "Atendimento removido com sucesso.")
        return super().form_valid(form)

# --- BUSCAS VIA AJAX ---

@login_required
@permission_required("atendimentos.view_aluno", raise_exception=True)
def buscar_alunos(request):
    q = request.GET.get("q", "").strip()
    if len(q) < 2: return JsonResponse([], safe=False)
    alunos = Aluno.objects.filter(Q(nome__icontains=q) | Q(ra__icontains=q))
    dados = [{"id": a.pk, "texto": f"{a.nome} - (RA: {a.ra})", "detalhe": a.curso} for a in alunos]
    return JsonResponse(dados, safe=False)

@login_required
@permission_required("atendimentos.view_servidor", raise_exception=True)
def buscar_servidores(request):
    q = request.GET.get("q", "").strip()
    if len(q) < 2: return JsonResponse([], safe=False)
    servidores = Servidor.objects.filter(Q(nome__icontains=q) | Q(siape__icontains=q))[:8]
    dados = [{"id": s.pk, "texto": f"{s.siape} — {s.nome}", "detalhe": s.cargo} for s in servidores]
    return JsonResponse(dados, safe=False)

@login_required
@permission_required("atendimentos.view_usuarioexterno", raise_exception=True)
def buscar_usuarios_externos(request):
    q = request.GET.get("q", "").strip()
    if len(q) < 2: return JsonResponse([], safe=False)
    usuarios = UsuarioExterno.objects.filter(Q(nome__icontains=q) | Q(cpf__icontains=q))[:8]
    dados = [{"id": u.pk, "texto": u.nome, "detalhe": u.cpf} for u in usuarios]
    return JsonResponse(dados, safe=False)
from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from .forms import ServidorForm, AlunoForm
from .models import Endereco, Responsavel, Servidor, Aluno
from .forms import ServidorForm, AlunoForm, UsuarioExternoForm
from .models import Endereco, Servidor, Aluno, UsuarioExterno
from django.views.generic.list import MultipleObjectMixin
from atendimentos.models import Atendimento  
from usuarios.models import Aluno, Servidor  


class CustomPermissionMixin(PermissionRequiredMixin):

    def handle_no_permission(self):
        messages.error(self.request, "Você não tem permissão para acessar esta área.")
        return redirect('home')


@login_required
def home(request):
    return render(request, 'home.html')

@login_required
@permission_required('usuarios.view_endereco', raise_exception=False)
def endereco_autocomplete(request):
    if not request.user.has_perm('usuarios.view_endereco'):
        return JsonResponse({'error': 'Sem permissão'}, status=403)
        
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'results': []})

    enderecos = Endereco.objects.filter(
        Q(logradouro__icontains=query) | Q(numero__icontains=query) | 
        Q(bairro__icontains=query) | Q(cidade__icontains=query) | 
        Q(estado__icontains=query) | Q(cep__icontains=query)
    ).order_by('logradouro', 'numero')[:10]

    results = [{'id': e.pk, 'label': str(e)} for e in enderecos]
    return JsonResponse({'results': results})

# usuarios/views.py

@login_required
@permission_required('usuarios.view_responsavel', raise_exception=False)
def responsavel_autocomplete(request):
    if not request.user.has_perm('usuarios.view_responsavel'):
        return JsonResponse({'error': 'Sem permissão'}, status=403)

    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'results': []})

    responsaveis = Responsavel.objects.filter(
        Q(nome__icontains=query) |
        Q(cpf__icontains=query) |
        Q(email__icontains=query) |
        Q(telefone__icontains=query) |
        Q(parentesco__icontains=query) |
        Q(endereco__logradouro__icontains=query) |
        Q(endereco__bairro__icontains=query) |
        Q(endereco__cidade__icontains=query) |
        Q(endereco__estado__icontains=query)
    ).select_related('endereco').order_by('nome')[:10]

    results = []
    for r in responsaveis:
        results.append({
            'id': r.pk,
            'label': str(r),
            'cpf': r.cpf,
            'telefone': r.telefone,
            'email': r.email,
            'parentesco': r.parentesco,
        })
    return JsonResponse({'results': results})

@login_required
@permission_required('usuarios.view_aluno', raise_exception=False)
def curso_autocomplete(request):
    if not request.user.has_perm('usuarios.view_aluno'):
        return JsonResponse({'error': 'Sem permissão'}, status=403)
        
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'results': []})

    cursos = Aluno.objects.filter(
        curso__icontains=query
    ).values_list('curso', flat=True).distinct().order_by('curso')[:10]

    results = [{'id': curso, 'label': curso} for curso in cursos if curso]
    
    return JsonResponse({'results': results})


class AlunoListView(LoginRequiredMixin, CustomPermissionMixin, ListView):
    permission_required = 'usuarios.view_aluno'
    model = Aluno
    template_name = 'usuarios/aluno/aluno_list.html'
    context_object_name = 'alunos'
    paginate_by = 5

    def get_paginate_by(self, queryset):
        page_size = self.request.GET.get('page_size')
        try: return int(page_size) if int(page_size) > 0 else self.paginate_by
        except (TypeError, ValueError): return self.paginate_by

    def get_queryset(self):
        queryset = Aluno.objects.select_related('endereco').order_by('nome')
        search = self.request.GET.get('q', '').strip()
        if search: queryset = queryset.filter(Q(nome__icontains=search) | Q(ra__icontains=search))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '').strip()
        context['page_size'] = self.get_paginate_by(self.get_queryset())
        context['page_size_options'] = [5, 10, 25, 50]
        return context

class AlunoDetailView(LoginRequiredMixin, CustomPermissionMixin, DetailView):
    permission_required = 'usuarios.view_aluno'
    model = Aluno
    template_name = 'usuarios/aluno/aluno_detail.html'
    context_object_name = 'aluno'
    
    def get_queryset(self):
        return Aluno.objects.prefetch_related('responsaveis')

class AlunoCreateView(LoginRequiredMixin, CustomPermissionMixin, CreateView):
    permission_required = 'usuarios.add_aluno'
    model = Aluno
    form_class = AlunoForm
    template_name = 'usuarios/aluno/aluno_form.html'
    success_url = reverse_lazy('aluno_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Aluno cadastrado com sucesso!')
        return super().form_valid(form)

class AlunoUpdateView(LoginRequiredMixin, CustomPermissionMixin, UpdateView):
    permission_required = 'usuarios.change_aluno'
    model = Aluno
    form_class = AlunoForm
    template_name = 'usuarios/aluno/aluno_form.html'
    success_url = reverse_lazy('aluno_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Aluno atualizado com sucesso!')
        return super().form_valid(form)

class AlunoDeleteView(LoginRequiredMixin, CustomPermissionMixin, DeleteView):
    permission_required = 'usuarios.delete_aluno'
    model = Aluno
    template_name = 'usuarios/aluno/aluno_confirm_delete.html'
    success_url = reverse_lazy('aluno_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Aluno removido com sucesso!')
        return super().form_valid(form)

class HistoricoAlunoView(LoginRequiredMixin, CustomPermissionMixin, ListView):
    permission_required = 'usuarios.view_aluno'
    model = Atendimento
    template_name = 'atendimentos/historico.html'
    context_object_name = 'atendimentos'
    paginate_by = 5

    def get_queryset(self):
        return Atendimento.objects.filter(aluno__id=self.kwargs['pk']).order_by('-data_atendimento')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pessoa'] = Aluno.objects.get(pk=self.kwargs['pk'])
        context['tipo_pessoa'] = 'Aluno'
        return context

class HistoricoServidorView(LoginRequiredMixin, CustomPermissionMixin, ListView):
    permission_required = 'usuarios.view_servidor'
    model = Atendimento
    template_name = 'atendimentos/historico.html'
    context_object_name = 'atendimentos'
    paginate_by = 5

    def get_queryset(self):
        return Atendimento.objects.filter(servidor__id=self.kwargs['pk']).order_by('-data_atendimento')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pessoa'] = Servidor.objects.get(pk=self.kwargs['pk'])
        context['tipo_pessoa'] = 'Servidor'
        return context


class ServidorListView(LoginRequiredMixin, CustomPermissionMixin, ListView):
    permission_required = 'usuarios.view_servidor'
    model = Servidor
    template_name = 'usuarios/servidor/servidor_list.html'
    context_object_name = 'servidores'
    paginate_by = 10

    def get_paginate_by(self, queryset):
        page_size = self.request.GET.get('page_size')
        try: return int(page_size) if int(page_size) > 0 else self.paginate_by
        except (TypeError, ValueError): return self.paginate_by

    def get_queryset(self):
        queryset = Servidor.objects.select_related('endereco').order_by('nome')
        search = self.request.GET.get('q', '').strip()
        if search: queryset = queryset.filter(Q(nome__icontains=search) | Q(siape__icontains=search) | Q(cargo__icontains=search) | Q(email__icontains=search) | Q(telefone__icontains=search))
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '').strip()
        context['page_size'] = self.get_paginate_by(self.get_queryset())
        context['page_size_options'] = [5, 10, 25, 50]
        return context

class ServidorCreateView(LoginRequiredMixin, CustomPermissionMixin, CreateView):
    permission_required = 'usuarios.add_servidor'
    model = Servidor
    form_class = ServidorForm
    template_name = 'usuarios/servidor/servidor_form.html'
    success_url = reverse_lazy('servidor_list')
    
    def form_valid(self, form):
        messages.success(self.request, "Servidor cadastrado com sucesso!")
        return super().form_valid(form)

class ServidorUpdateView(LoginRequiredMixin, CustomPermissionMixin, UpdateView):
    permission_required = 'usuarios.change_servidor'
    model = Servidor
    form_class = ServidorForm
    template_name = 'usuarios/servidor/servidor_form.html'
    success_url = reverse_lazy('servidor_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Servidor atualizado com sucesso!')
        return super().form_valid(form)

class ServidorDeleteView(LoginRequiredMixin, CustomPermissionMixin, DeleteView):
    permission_required = 'usuarios.delete_servidor'
    model = Servidor
    template_name = 'usuarios/servidor/servidor_confirm_delete.html'
    success_url = reverse_lazy('servidor_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Servidor removido com sucesso!')
        return super().form_valid(form)

def login_view(request):
    if request.user.is_authenticated: return redirect('home')
    if request.method == 'POST':
        usuario = request.POST.get('username')
        senha = request.POST.get('password')
        lembrar = request.POST.get('remember')
        user = authenticate(request, username=usuario, password=senha)
        if user is not None:
            login(request, user)
            request.session.set_expiry(1209600 if lembrar == 'on' else 0)
            return redirect(request.GET.get('next', 'home'))
        else: messages.error(request, 'Usuário ou senha inválidos.')
    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')


class UsuarioExternoListView(LoginRequiredMixin, CustomPermissionMixin, ListView):
    permission_required = 'usuarios.view_usuarioexterno'
    model = UsuarioExterno
    template_name = 'usuarios/usuario_externo/usuario_externo_list.html'
    context_object_name = 'usuarios_externos'
    paginate_by = 5  
    
    def get_paginate_by(self, queryset):
        page_size = self.request.GET.get('page_size')
        try:
            page_size = int(page_size)
        except (TypeError, ValueError):
            return self.paginate_by
        return page_size if page_size > 0 else self.paginate_by
    
    def get_queryset(self):
        queryset = UsuarioExterno.objects.select_related('endereco').order_by('nome')
        serach = self.request.GET.get('q', '').strip()
        if serach:
            queryset = queryset.filter(
                Q(nome__icontains=serach)
                | Q(cpf__icontains=serach)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '').strip()
        context['page_size'] = self.get_paginate_by(self.get_queryset())
        context['page_size_options'] = [5, 10, 25, 50]
        return context

class UsuarioExternoDetailView(LoginRequiredMixin, CustomPermissionMixin, DetailView):
    permission_required = 'usuarios.view_usuarioexterno'
    model = UsuarioExterno
    template_name = 'usuarios/usuario_externo/usuario_externo_detail.html'
    context_object_name = 'usuario_externo'

class UsuarioExternoCreateView(LoginRequiredMixin, CustomPermissionMixin, CreateView):
    permission_required = 'usuarios.add_usuarioexterno'
    model = UsuarioExterno
    form_class = UsuarioExternoForm
    template_name = 'usuarios/usuario_externo/usuario_externo_form.html'
    success_url = reverse_lazy('usuario_externo_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Usuário Externo cadastrado com sucesso!')
        return super().form_valid(form)
    
class UsuarioExternoUpdateView(LoginRequiredMixin, CustomPermissionMixin, UpdateView):
    permission_required = 'usuarios.change_usuarioexterno'
    model = UsuarioExterno
    form_class = UsuarioExternoForm
    template_name = 'usuarios/usuario_externo/usuario_externo_form.html'
    success_url = reverse_lazy('usuario_externo_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Usuário Externo atualizado com sucesso!')
        return super().form_valid(form)

class UsuarioExternoDeleteView(LoginRequiredMixin, CustomPermissionMixin, DeleteView):
    permission_required = 'usuarios.delete_usuarioexterno'
    model = UsuarioExterno
    template_name = 'usuarios/usuario_externo_confirm_delete.html'
    success_url = reverse_lazy('usuario_externo_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Usuário Externo removido com sucesso!')
        return super().form_valid(form)

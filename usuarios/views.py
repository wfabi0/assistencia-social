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
from .models import Endereco, Servidor, Aluno
from .forms import ServidorForm, AlunoForm, UsuarioExternoForm
from .models import Endereco, Servidor, Aluno, UsuarioExterno


class CustomPermissionMixin(PermissionRequiredMixin):
    """
    Mixin que redireciona para a home com uma mensagem de erro 
    caso o usuário não tenha a permissão necessária.
    """
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

class AlunoListView(LoginRequiredMixin, CustomPermissionMixin, ListView):
    permission_required = 'usuarios.view_aluno'
    model = Aluno
    template_name = 'usuarios/aluno_list.html'
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

class AlunoCreateView(LoginRequiredMixin, CustomPermissionMixin, CreateView):
    permission_required = 'usuarios.add_aluno'
    model = Aluno
    form_class = AlunoForm
    template_name = 'usuarios/aluno_form.html'
    success_url = reverse_lazy('aluno_list')

class AlunoUpdateView(LoginRequiredMixin, CustomPermissionMixin, UpdateView):
    permission_required = 'usuarios.change_aluno'
    model = Aluno
    form_class = AlunoForm
    template_name = 'usuarios/aluno_form.html'
    success_url = reverse_lazy('aluno_list')

class AlunoDetailView(LoginRequiredMixin, CustomPermissionMixin, DetailView):
    permission_required = 'usuarios.view_aluno'
    model = Aluno
    template_name = 'usuarios/aluno_detail.html'
    context_object_name = 'aluno'

class ServidorListView(LoginRequiredMixin, CustomPermissionMixin, ListView):
    permission_required = 'usuarios.view_servidor'
    model = Servidor
    template_name = 'usuarios/servidor_list.html'
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

class ServidorCreateView(LoginRequiredMixin, CustomPermissionMixin, CreateView):
    permission_required = 'usuarios.add_servidor'
    model = Servidor
    form_class = ServidorForm
    template_name = 'usuarios/servidor_form.html'
    success_url = reverse_lazy('servidor_list')

class ServidorUpdateView(LoginRequiredMixin, CustomPermissionMixin, UpdateView):
    permission_required = 'usuarios.change_servidor'
    model = Servidor
    form_class = ServidorForm
    template_name = 'usuarios/servidor_form.html'
    success_url = reverse_lazy('servidor_list')

class ServidorDeleteView(LoginRequiredMixin, CustomPermissionMixin, DeleteView):
    permission_required = 'usuarios.delete_servidor'
    model = Servidor
    template_name = 'usuarios/servidor_confirm_delete.html'
    success_url = reverse_lazy('servidor_list')

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
    paginate_by = 5  # padrão 5
    
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
    
class UsuarioExternoUpdateView(LoginRequiredMixin, CustomPermissionMixin, UpdateView):
    permission_required = 'usuarios.change_usuarioexterno'
    model = UsuarioExterno
    form_class = UsuarioExternoForm
    template_name = 'usuarios/usuario_externo/usuario_externo_form.html'
    success_url = reverse_lazy('usuario_externo_list')

class UsuarioExternoDeleteView(LoginRequiredMixin, CustomPermissionMixin, DeleteView):
    permission_required = 'usuarios.delete_usuarioexterno'
    model = UsuarioExterno
    template_name = 'usuarios/usuario_externo_confirm_delete.html'
    success_url = reverse_lazy('usuario_externo_list')

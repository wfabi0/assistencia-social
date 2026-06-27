from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .forms import ServidorForm, AlunoForm
from .models import Endereco, Servidor, Aluno


@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def endereco_autocomplete(request):
    query = request.GET.get('q', '').strip()

    if not query:
        return JsonResponse({'results': []})

    enderecos = Endereco.objects.filter(
        Q(logradouro__icontains=query)
        | Q(numero__icontains=query)
        | Q(bairro__icontains=query)
        | Q(cidade__icontains=query)
        | Q(estado__icontains=query)
        | Q(cep__icontains=query)
    ).order_by('logradouro', 'numero')[:10]

    results = [
        {
            'id': endereco.pk,
            'label': str(endereco),
        }
        for endereco in enderecos
    ]

    return JsonResponse({'results': results})

class AlunoListView(LoginRequiredMixin, ListView):
    model = Aluno
    template_name = 'usuarios/aluno_list.html'
    context_object_name = 'alunos'
    paginate_by = 5  

    def get_paginate_by(self, queryset):
        page_size = self.request.GET.get('page_size')

        try:
            page_size = int(page_size)
        except (TypeError, ValueError):
            return self.paginate_by

        return page_size if page_size > 0 else self.paginate_by

    def get_queryset(self):
        queryset = Aluno.objects.select_related('endereco').order_by('nome')
        search = self.request.GET.get('q', '').strip()

        if search:
            queryset = queryset.filter(
                Q(nome__icontains=search)
                | Q(ra__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '').strip()
        context['page_size'] = self.get_paginate_by(self.get_queryset())
        context['page_size_options'] = [5, 10, 25, 50]
        return context


class AlunoCreateView(LoginRequiredMixin, CreateView):
    model = Aluno
    form_class = AlunoForm
    template_name = 'usuarios/aluno_form.html'
    success_url = reverse_lazy('aluno_list')


class AlunoUpdateView(LoginRequiredMixin, UpdateView):
    model = Aluno
    form_class = AlunoForm
    template_name = 'usuarios/aluno_form.html'
    success_url = reverse_lazy('aluno_list')


class AlunoDetailView(LoginRequiredMixin, DetailView):
    model = Aluno
    template_name = 'usuarios/aluno_detail.html'
    context_object_name = 'aluno'


class ServidorListView(LoginRequiredMixin, ListView):
    model = Servidor
    template_name = 'usuarios/servidor_list.html'
    context_object_name = 'servidores'
    paginate_by = 10

    def get_paginate_by(self, queryset):
        page_size = self.request.GET.get('page_size')

        try:
            page_size = int(page_size)
        except (TypeError, ValueError):
            return self.paginate_by

        return page_size if page_size > 0 else self.paginate_by

    def get_queryset(self):
        queryset = Servidor.objects.select_related('endereco').order_by('nome')
        search = self.request.GET.get('q', '').strip()

        if search:
            queryset = queryset.filter(
                Q(nome__icontains=search)
                | Q(siape__icontains=search)
                | Q(cargo__icontains=search)
                | Q(email__icontains=search)
                | Q(telefone__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '').strip()
        context['page_size'] = self.get_paginate_by(self.get_queryset())
        context['page_size_options'] = [10, 25, 50]
        return context


class ServidorCreateView(LoginRequiredMixin, CreateView):
    model = Servidor
    form_class = ServidorForm
    template_name = 'usuarios/servidor_form.html'
    success_url = reverse_lazy('servidor_list')


class ServidorUpdateView(LoginRequiredMixin, UpdateView):
    model = Servidor
    form_class = ServidorForm
    template_name = 'usuarios/servidor_form.html'
    success_url = reverse_lazy('servidor_list')


class ServidorDeleteView(LoginRequiredMixin, DeleteView):
    model = Servidor
    template_name = 'usuarios/servidor_confirm_delete.html'
    success_url = reverse_lazy('servidor_list')
    
    
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        usuario = request.POST.get('username')
        senha = request.POST.get('password')
        lembrar = request.POST.get('remember')

        user = authenticate(request, username=usuario, password=senha)

        if user is not None:
            login(request, user)

            if lembrar == 'on':
                request.session.set_expiry(1209600)  # 14 dias em segundos
            else:
                request.session.set_expiry(0)  # Expira ao fechar o navegador

            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuário ou senha inválidos.')

    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')
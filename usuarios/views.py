from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from .forms import ServidorForm
from .models import Endereco, Servidor


def home(request):
    return render(request, 'home.html')


def aluno_list(request):
    return render(request, 'usuarios/aluno_list.html')


def aluno_form(request):
    return render(request, 'usuarios/aluno_form.html')


def aluno_detail(request):
    return render(request, 'usuarios/aluno_detail.html')


def aluno_update(request, pk=None):
    return render(request, 'usuarios/aluno_form.html')


def aluno_historico(request, pk=None):
    return render(request, 'usuarios/aluno_detail.html')


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


class ServidorListView(ListView):
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


class ServidorCreateView(CreateView):
    model = Servidor
    form_class = ServidorForm
    template_name = 'usuarios/servidor_form.html'
    success_url = reverse_lazy('servidor_list')


class ServidorUpdateView(UpdateView):
    model = Servidor
    form_class = ServidorForm
    template_name = 'usuarios/servidor_form.html'
    success_url = reverse_lazy('servidor_list')

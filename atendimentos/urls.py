from django.urls import path
from . import views

urlpatterns = [
    path("atendimentos/", views.AtendimentoListView.as_view(), name="lista_atendimentos"),
    path("atendimentos/novo/", views.AtendimentoCreateView.as_view(), name="novo_atendimento"),
    path("atendimentos/<int:pk>/editar/", views.AtendimentoUpdateView.as_view(), name="editar_atendimento"),
    path("atendimentos/<int:pk>/excluir/", views.AtendimentoDeleteView.as_view(), name="excluir_atendimento"),

    # Endpoints de busca para autocomplete
    path("atendimentos/buscar/alunos/", views.buscar_alunos, name="buscar_alunos"),
    path("atendimentos/buscar/servidores/", views.buscar_servidores, name="buscar_servidores"),
    path("atendimentos/buscar/usuarios-externos/", views.buscar_usuarios_externos, name="buscar_usuarios_externos"),
]
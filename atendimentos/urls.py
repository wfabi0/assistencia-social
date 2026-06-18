from django.urls import path
from . import views

urlpatterns = [
    path("atendimentos/", views.AtendimentoListView.as_view(), name="lista_atendimentos"),
    path("atendimentos/novo/", views.AtendimentoCreateView.as_view(), name="novo_atendimento"),
]
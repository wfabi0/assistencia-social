from django.urls import path
from . import views

urlpatterns = [
    path("atendimentos/novo/", views.AtendimentoCreateView.as_view(), name="novo_atendimento"),
]
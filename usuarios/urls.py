from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('enderecos/busca/', views.endereco_autocomplete,
         name='endereco_autocomplete'),

    path('alunos/', views.AlunoListView.as_view(), name='aluno_list'),

    path('alunos/novo/', views.AlunoCreateView.as_view(), name='aluno_create'),

    path('alunos/<int:pk>/historico/', views.HistoricoAlunoView.as_view(), name='aluno_detail'),

    path('alunos/<int:pk>/editar/', views.AlunoUpdateView.as_view(), name='aluno_update'),

    path('servidores/<int:pk>/historico/', views.HistoricoServidorView.as_view(), name='servidor_detail'),

    path('servidores/', views.ServidorListView.as_view(), name='servidor_list'),

    path('servidores/novo/', views.ServidorCreateView.as_view(),
         name='servidor_create'),

    path('servidores/<int:pk>/editar/',
         views.ServidorUpdateView.as_view(), name='servidor_update'),

    path('servidores/<int:pk>/excluir/',
         views.ServidorDeleteView.as_view(), name='servidor_delete'),

]

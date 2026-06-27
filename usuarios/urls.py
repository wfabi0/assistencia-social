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
     
     path('usuarios-externos/', views.UsuarioExternoListView.as_view(), name='usuario_externo_list'),
     path('usuarios-externos/novo/', views.UsuarioExternoCreateView.as_view(), name='usuario_externo_create'),
     path('usuarios-externos/<int:pk>/editar/', views.UsuarioExternoUpdateView.as_view(), name='usuario_externo_update'),
     path('usuarios-externos/<int:pk>/excluir/', views.UsuarioExternoDeleteView.as_view(), name='usuario_externo_delete'),
     path('usuarios-externos/<int:pk>/', views.UsuarioExternoDetailView.as_view(), name='usuario_externo_detail'),
]

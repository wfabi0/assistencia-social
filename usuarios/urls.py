from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api_views import (
    AlunoViewSet, ServidorViewSet, 
    UsuarioExternoViewSet, EnderecoViewSet
)

router = DefaultRouter()
router.register(r'alunos', AlunoViewSet, basename='api-aluno')
router.register(r'servidores', ServidorViewSet, basename='api-servidor')
router.register(r'usuarios-externos', UsuarioExternoViewSet, basename='api-usuario-externo')
router.register(r'enderecos', EnderecoViewSet, basename='api-endereco')

urlpatterns = [
    path('api/', include(router.urls)),
    
    path('', views.home, name='home'),

    path('enderecos/busca/', views.endereco_autocomplete,
         name='endereco_autocomplete'),
     
    path('cursos/busca/', views.curso_autocomplete, name='curso_autocomplete'),

    path('alunos/', views.AlunoListView.as_view(), name='aluno_list'),

    path('alunos/novo/', views.AlunoCreateView.as_view(), name='aluno_create'),

    path('alunos/<int:pk>/detail/', views.AlunoDetailView.as_view(), name='aluno_detail'),
     
    path('alunos/<int:pk>/historico/', views.HistoricoAlunoView.as_view(), name='aluno_historico'),

    path('alunos/<int:pk>/editar/', views.AlunoUpdateView.as_view(), name='aluno_update'),
     
    path('alunos/<int:pk>/excluir/',
         views.AlunoDeleteView.as_view(), name='aluno_delete'),

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
    path('usuarios-externos/<int:pk>/detail/', views.UsuarioExternoDetailView.as_view(), name='usuario_externo_detail'),
]
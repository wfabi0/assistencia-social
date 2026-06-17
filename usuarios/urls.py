from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('alunos/', views.aluno_list, name='aluno_list'),

    path('alunos/novo/', views.aluno_form, name='aluno_create'),

    path('alunos/<int:pk>/', views.aluno_detail, name='aluno_detail'),

    path('alunos/<int:pk>/editar/', views.aluno_update, name='aluno_update'),

    path('alunos/<int:pk>/historico/', views.aluno_historico, name='aluno_historico'),
]
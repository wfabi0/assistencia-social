from django.shortcuts import render

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
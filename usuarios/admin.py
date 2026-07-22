from django.contrib import admin
from .models import Usuario, Aluno, Servidor, UsuarioExterno, Endereco, Responsavel
from django.contrib.auth.admin import UserAdmin

admin.site.register(Aluno)
admin.site.register(Servidor)
admin.site.register(UsuarioExterno)
admin.site.register(Endereco)
admin.site.register(Responsavel)

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Dados Profissionais', {
            'fields': ('cress',)
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Dados Profissionais', {
            'fields': ('cress',)
        }),
    )
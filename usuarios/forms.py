from django import forms
from django.core.exceptions import ValidationError

from .models import Servidor


class ServidorForm(forms.ModelForm):
    class Meta:
        model = Servidor
        fields = ['siape', 'nome', 'cargo', 'email', 'telefone', 'endereco']
        widgets = {
            'siape': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0000000'}),
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cargo'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemplo.com'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'endereco': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_siape(self):
        siape = self.cleaned_data['siape'].strip()

        if not siape.isdigit():
            raise ValidationError('O SIAPE deve conter apenas números.')

        if len(siape) < 5:
            raise ValidationError('O SIAPE deve ter pelo menos 5 dígitos.')

        return siape

    def clean_nome(self):
        nome = self.cleaned_data['nome'].strip()

        if len(nome) < 3:
            raise ValidationError('Informe um nome válido.')

        return nome

    def clean_cargo(self):
        cargo = self.cleaned_data['cargo'].strip()

        if len(cargo) < 3:
            raise ValidationError('Informe um cargo válido.')

        return cargo

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')

        if not telefone:
            return telefone

        telefone = telefone.strip()

        if not all(char.isdigit() or char in ' ()+-' for char in telefone):
            raise ValidationError('Informe um telefone válido.')

        return telefone

import re

from django import forms
from django.core.exceptions import ValidationError

from .models import Endereco, Servidor


ENDERECO_PATTERN = re.compile(
    r'^\s*(?P<logradouro>.+?),\s*(?P<numero>.+?)\s*-\s*(?P<bairro>.+?),\s*(?P<cidade>.+?)\s*-\s*(?P<estado>.+?),\s*CEP:\s*(?P<cep>.+?)\s*$'
)


class ServidorForm(forms.ModelForm):

    CARGO_CHOICES = [
        ('Professor', 'Professor'),
        ('Técnico Administrativo', 'Técnico Administrativo'),
        ('Coordenador', 'Coordenador'),
        ('Diretor', 'Diretor'),
        ('Outros', 'Outros'),
    ]

    cargo = forms.ChoiceField(
        choices=CARGO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    cargo_outro = forms.CharField(
        required=False,
        label='Outro cargo',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Informe o cargo'
        })
    )

    endereco_busca = forms.CharField(
        label='Endereço',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite para buscar um endereço cadastrado',
            'autocomplete': 'off',
        }),
    )

    endereco_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Servidor
        fields = [
            'siape',
            'nome',
            'cargo',
            'cargo_outro',
            'email',
            'telefone',
        ]
        widgets = {
            'siape': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '0000000'
            }),
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemplo.com'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        endereco = getattr(self.instance, 'endereco', None)

        if endereco:
            self.fields['endereco_busca'].initial = str(endereco)
            self.fields['endereco_id'].initial = endereco.pk

        if self.instance.pk and self.instance.cargo:
            cargos_padrao = [cargo[0] for cargo in self.CARGO_CHOICES]

            if self.instance.cargo not in cargos_padrao:
                self.initial['cargo'] = 'Outros'
                self.initial['cargo_outro'] = self.instance.cargo
            else:
                self.initial['cargo'] = self.instance.cargo

    def _parse_endereco_texto(self, endereco_texto):
        match = ENDERECO_PATTERN.match(endereco_texto)

        if not match:
            return None

        dados = {
            chave: valor.strip()
            for chave, valor in match.groupdict().items()
        }

        if not all(dados.values()):
            return None

        return dados

    def clean_siape(self):
        siape = self.cleaned_data['siape'].strip()

        if not siape.isdigit():
            raise ValidationError(
                'O SIAPE deve conter apenas números.'
            )

        if len(siape) < 5:
            raise ValidationError(
                'O SIAPE deve ter pelo menos 5 dígitos.'
            )

        return siape

    def clean_nome(self):
        nome = self.cleaned_data['nome'].strip()

        if len(nome) < 3:
            raise ValidationError(
                'Informe um nome válido.'
            )

        return nome

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')

        if not telefone:
            return telefone

        telefone = telefone.strip()

        if not all(
            char.isdigit() or char in ' ()+-'
            for char in telefone
        ):
            raise ValidationError(
                'Informe um telefone válido.'
            )

        return telefone

    def clean_endereco_busca(self):
        return self.cleaned_data.get(
            'endereco_busca',
            ''
        ).strip()

    def clean(self):
        cleaned_data = super().clean()

        cargo = cleaned_data.get('cargo')
        cargo_outro = cleaned_data.get(
            'cargo_outro',
            ''
        ).strip()

        endereco_id = cleaned_data.get('endereco_id')
        endereco_busca = cleaned_data.get(
            'endereco_busca',
            ''
        )

        self._endereco_resolvido = None
        self._novo_endereco_dados = None

        if cargo == 'Outros' and not cargo_outro:
            self.add_error(
                'cargo_outro',
                'Informe o cargo.'
            )

        if endereco_id:
            endereco = Endereco.objects.filter(
                pk=endereco_id
            ).first()

            if endereco is None:
                self.add_error(
                    'endereco_busca',
                    'Selecione um endereço existente da lista ou deixe o campo vazio para cadastrar um novo.'
                )
                return cleaned_data

            self._endereco_resolvido = endereco
            return cleaned_data

        if not endereco_busca:
            return cleaned_data

        endereco_dados = self._parse_endereco_texto(
            endereco_busca
        )

        if endereco_dados is None:
            self.add_error(
                'endereco_busca',
                'Digite o endereço no formato "Rua, número - bairro, cidade - estado, CEP: 00000-000" ou selecione uma opção da lista.'
            )
            return cleaned_data

        self._novo_endereco_dados = endereco_dados

        return cleaned_data

    def save(self, commit=True):
        servidor = super().save(commit=False)

        if self.cleaned_data['cargo'] == 'Outros':
            servidor.cargo = self.cleaned_data['cargo_outro']
        else:
            servidor.cargo = self.cleaned_data['cargo']

        if self._endereco_resolvido is not None:
            servidor.endereco = self._endereco_resolvido

        elif self._novo_endereco_dados is not None:
            endereco, _ = Endereco.objects.get_or_create(
                **self._novo_endereco_dados
            )
            servidor.endereco = endereco

        else:
            servidor.endereco = None

        if commit:
            servidor.save()

        return servidor

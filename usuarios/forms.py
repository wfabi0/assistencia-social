import re

from django import forms
from django.core.exceptions import ValidationError

from .models import Endereco, Servidor, Aluno, UsuarioExterno, Responsavel


ENDERECO_PATTERN = re.compile(
    r'^\s*(?P<logradouro>.+?)\s*,\s*(?P<numero>.+?)\s*[,\-]\s*(?P<bairro>.+?)\s*[,\-]\s*(?P<cidade>.+?)\s*[,\-]\s*(?P<estado>[A-Za-z]{2})\s*[,\-]?\s*(?:CEP[:\s]*)?(?P<cep>\d{5}-?\d{3})\s*$',
    re.IGNORECASE
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
                'class': 'form-control telefone-mask',
                'placeholder': '(00) 00000-0000',
                'maxlength': '15',
                'onkeyup': "let v=this.value.replace(/\D/g,''); v=v.replace(/^(\d{2})(\d)/g,'($1) $2'); v=v.replace(/(\d)(\d{4})$/,'$1-$2'); this.value=v;"
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
        
        if self.is_bound:
            for field_name in self.errors:
                if field_name in self.fields:
                    attrs = self.fields[field_name].widget.attrs
                    attrs['class'] = attrs.get('class', '') + ' is-invalid'

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

        numeros = re.sub(r'\D', '', telefone)

        if numeros.startswith('55') and len(numeros) > 11:
            numeros = numeros[2:]

        tamanho = len(numeros)

        if tamanho == 0:
            return ''

        if tamanho not in (10, 11):
            raise ValidationError(
                'Informe um telefone válido com DDD (ex: 31 99999-9999).'
            )

        if tamanho == 11:
            telefone_formatado = f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
        else:
            telefone_formatado = f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"

        return telefone_formatado

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
    

class AlunoForm(forms.ModelForm):
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

    responsavel_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput()
    )

    responsavel_nome = forms.CharField(
        label='Nome do Responsável',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome completo do responsável'
        })
    )

    responsavel_cpf = forms.CharField(
        label='CPF do Responsável',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control cpf-mask',
            'placeholder': '000.000.000-00',
            'maxlength': '14'
        })
    )

    responsavel_telefone = forms.CharField(
        label='Telefone do Responsável',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control telefone-mask',
            'placeholder': '(00) 00000-0000',
            'maxlength': '15'
        })
    )

    responsavel_email = forms.EmailField(
        label='E-mail do Responsável',
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'email@exemplo.com'
        })
    )

    responsavel_parentesco = forms.ChoiceField(
        label='Parentesco',
        required=False,
        choices=[
            ('', 'Selecione o parentesco'),
            ('Pai', 'Pai'),
            ('Mãe', 'Mãe'),
            ('Filho', 'Filho(a)'),
            ('Irmão', 'Irmão(ã)'),
            ('Avô', 'Avô(ó)'),
            ('Tio', 'Tio(a)'),
            ('Primo', 'Primo(a)'),
            ('Cônjuge', 'Cônjuge'),
            ('Outro', 'Outro'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    class Meta:
        model = Aluno
        fields = [
            'ra',
            'nome',
            'curso',
            'email',
            'telefone',
            'data_nascimento',
        ]
        widgets = {
            'ra': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'RA00000'
            }),
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo'
            }),
            'curso': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Curso do aluno',
                'autocomplete': 'off'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemplo.com'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control telefone-mask',
                'placeholder': '(00) 00000-0000',
                'maxlength': '15',
                'onkeyup': "let v=this.value.replace(/\D/g,''); v=v.replace(/^(\d{2})(\d)/g,'($1) $2'); v=v.replace(/(\d)(\d{4})$/,'$1-$2'); this.value=v;"
            }),
            'data_nascimento': forms.DateInput(attrs={
                'class': 'form-control datepicker',
                'placeholder': 'DD/MM/YYYY',
                'autocomplete': 'off',
            }, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['ra'].required = True
        self.fields['nome'].required = True
        self.fields['email'].required = True
        self.fields['data_nascimento'].required = True

        endereco = getattr(self.instance, 'endereco', None)
        if endereco:
            self.fields['endereco_busca'].initial = str(endereco)
            self.fields['endereco_id'].initial = endereco.pk

        if self.instance.pk:
            responsavel = self.instance.responsaveis.first()
            if responsavel:
                self.fields['responsavel_id'].initial = responsavel.pk
                self.fields['responsavel_nome'].initial = responsavel.nome
                self.fields['responsavel_cpf'].initial = responsavel.cpf
                self.fields['responsavel_telefone'].initial = responsavel.telefone
                self.fields['responsavel_email'].initial = responsavel.email
                self.fields['responsavel_parentesco'].initial = responsavel.parentesco

        if self.is_bound:
            for field_name in self.errors:
                if field_name in self.fields:
                    attrs = self.fields[field_name].widget.attrs
                    attrs['class'] = attrs.get('class', '') + ' is-invalid'

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

    def clean_ra(self):
        ra = self.cleaned_data['ra'].strip()
        if len(ra) < 3:
            raise ValidationError('Informe um RA valido.')
        return ra

    def clean_nome(self):
        nome = self.cleaned_data['nome'].strip()
        if len(nome) < 3:
            raise ValidationError('Informe um nome valido.')
        return nome

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        if not telefone:
            return telefone
        numeros = re.sub(r'\D', '', telefone)
        if numeros.startswith('55') and len(numeros) > 11:
            numeros = numeros[2:]
        tamanho = len(numeros)
        if tamanho == 0:
            return ''
        if tamanho not in (10, 11):
            raise ValidationError('Informe um telefone valido com DDD (ex: 31 99999-9999).')
        if tamanho == 11:
            telefone_formatado = f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
        else:
            telefone_formatado = f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
        return telefone_formatado

    def clean_endereco_busca(self):
        return self.cleaned_data.get('endereco_busca', '').strip()

    def clean_responsavel_cpf(self):
        cpf = self.cleaned_data.get('responsavel_cpf', '').strip()
        if not cpf:
            return ''
        cpf_numeros = re.sub(r'\D', '', cpf)
        if len(cpf_numeros) != 11:
            raise ValidationError('CPF deve ter 11 dígitos.')
        cpf_formatado = f"{cpf_numeros[:3]}.{cpf_numeros[3:6]}.{cpf_numeros[6:9]}-{cpf_numeros[9:]}"
        return cpf_formatado

    def clean_responsavel_telefone(self):
        telefone = self.cleaned_data.get('responsavel_telefone', '').strip()
        if not telefone:
            return ''
        numeros = re.sub(r'\D', '', telefone)
        if numeros.startswith('55') and len(numeros) > 11:
            numeros = numeros[2:]
        tamanho = len(numeros)
        if tamanho == 0:
            return ''
        if tamanho not in (10, 11):
            raise ValidationError('Informe um telefone válido com DDD (ex: 31 99999-9999).')
        if tamanho == 11:
            telefone_formatado = f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
        else:
            telefone_formatado = f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
        return telefone_formatado

    def clean_responsavel_email(self):
        email = self.cleaned_data.get('responsavel_email', '').strip()
        if not email:
            return ''
        if '@' not in email or '.' not in email:
            raise ValidationError('Informe um e-mail válido.')
        return email

    def clean(self):
        cleaned_data = super().clean()

        endereco_id = cleaned_data.get('endereco_id')
        endereco_busca = cleaned_data.get('endereco_busca', '')

        self._endereco_resolvido = None
        self._novo_endereco_dados = None

        if endereco_id:
            endereco = Endereco.objects.filter(pk=endereco_id).first()
            if endereco is None:
                self.add_error(
                    'endereco_busca',
                    'Selecione um endereço existente da lista ou deixe o campo vazio para cadastrar um novo.'
                )
                return cleaned_data
            self._endereco_resolvido = endereco
        elif endereco_busca:
            endereco_dados = self._parse_endereco_texto(endereco_busca)
            if endereco_dados is None:
                self.add_error(
                    'endereco_busca',
                    'Digite o endereço no formato "Rua, número - bairro, cidade - estado, CEP: 00000-000" ou selecione uma opção da lista.'
                )
                return cleaned_data
            self._novo_endereco_dados = endereco_dados

        responsavel_id = cleaned_data.get('responsavel_id')
        responsavel_nome = cleaned_data.get('responsavel_nome', '').strip()
        responsavel_cpf = cleaned_data.get('responsavel_cpf', '').strip()
        responsavel_telefone = cleaned_data.get('responsavel_telefone', '').strip()
        responsavel_parentesco = cleaned_data.get('responsavel_parentesco', '')

        self._responsavel_resolvido = None

        if responsavel_id:
            responsavel = Responsavel.objects.filter(pk=responsavel_id).first()
            if responsavel is None:
                self.add_error('responsavel_nome', 'Responsável selecionado não existe mais.')
            else:
                self._responsavel_resolvido = responsavel

        if responsavel_nome:
            if not responsavel_cpf:
                self.add_error('responsavel_cpf', 'O CPF é obrigatório quando o nome do responsável é preenchido.')
            if not responsavel_telefone:
                self.add_error('responsavel_telefone', 'O telefone é obrigatório quando o nome do responsável é preenchido.')
            if not responsavel_parentesco:
                self.add_error('responsavel_parentesco', 'O parentesco é obrigatório quando o nome do responsável é preenchido.')

        return cleaned_data

    def save(self, commit=True):
        aluno = super().save(commit=False)

        if self._endereco_resolvido is not None:
            aluno.endereco = self._endereco_resolvido
        elif self._novo_endereco_dados is not None:
            endereco, _ = Endereco.objects.get_or_create(**self._novo_endereco_dados)
            aluno.endereco = endereco
        else:
            aluno.endereco = None

        if commit:
            aluno.save()

            self.instance.responsaveis.all().delete()

            responsavel_id = self.cleaned_data.get('responsavel_id')
            responsavel_nome = self.cleaned_data.get('responsavel_nome', '').strip()

            if responsavel_nome:
                if responsavel_id:
                    try:
                        responsavel = Responsavel.objects.get(pk=responsavel_id)
                        responsavel.nome = responsavel_nome
                        responsavel.cpf = self.cleaned_data.get('responsavel_cpf', '').strip()
                        responsavel.telefone = self.cleaned_data.get('responsavel_telefone', '').strip()
                        responsavel.email = self.cleaned_data.get('responsavel_email', '').strip()
                        responsavel.parentesco = self.cleaned_data.get('responsavel_parentesco', '')
                        responsavel.aluno = aluno
                        responsavel.save()
                    except Responsavel.DoesNotExist:
                        Responsavel.objects.create(
                            aluno=aluno,
                            nome=responsavel_nome,
                            cpf=self.cleaned_data.get('responsavel_cpf', '').strip(),
                            telefone=self.cleaned_data.get('responsavel_telefone', '').strip(),
                            email=self.cleaned_data.get('responsavel_email', '').strip(),
                            parentesco=self.cleaned_data.get('responsavel_parentesco', '')
                        )
                else:
                    Responsavel.objects.create(
                        aluno=aluno,
                        nome=responsavel_nome,
                        cpf=self.cleaned_data.get('responsavel_cpf', '').strip(),
                        telefone=self.cleaned_data.get('responsavel_telefone', '').strip(),
                        email=self.cleaned_data.get('responsavel_email', '').strip(),
                        parentesco=self.cleaned_data.get('responsavel_parentesco', '')
                    )

        return aluno


class UsuarioExternoForm(forms.ModelForm):
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
        model = UsuarioExterno
        fields = [
            'nome',
            'cpf',
            'data_nascimento',
            'email',
            'telefone',
        ]
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control cpf-mask',
                'placeholder': '000.000.000-00',
                'maxlength': '14',
                'onkeyup': "let v=this.value.replace(/\D/g,''); v=v.replace(/(\d{3})(\d)/,'$1.$2'); v=v.replace(/(\d{3})(\d)/,'$1.$2'); v=v.replace(/(\d{3})(\d{1,2})$/,'$1-$2'); this.value=v;"
            }),
            'data_nascimento': forms.DateInput(attrs={
                'class': 'form-control datepicker',
                'placeholder': 'dd/mm/aaaa',
                'autocomplete': 'off',
            },format='%Y-%m-%d'),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemplo.com'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control phone-mask',
                'placeholder': '(00) 00000-0000',
                'maxlength': '15',
                'onkeyup': "let v=this.value.replace(/\D/g,''); v=v.replace(/(\d{2})(\d)/,'($1) $2'); this.value=v;"
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['nome'].required = True
        self.fields['cpf'].required = True
        self.fields['data_nascimento'].required = True
        self.fields['email'].required = True
        self.fields['telefone'].required = True
        
        endereco = getattr(self.instance, 'endereco', None)
        if endereco:
            self.fields['endereco_busca'].initial = str(endereco)
            self.fields['endereco_id'].initial = endereco.pk
        
        if self.is_bound:
            for field_name in self.errors:
                if field_name in self.fields:
                    attrs = self.fields[field_name].widget.attrs
                    attrs['class'] = attrs.get('class', '') + ' is-invalid'
    
    def clean_nome(self):
        nome = self.cleaned_data['nome'].strip()
        if len(nome) < 3:
            raise ValidationError('Informe um nome válido.')
        return nome
        
    def clean_cpf(self):
        cpf = self.cleaned_data['cpf'].strip()
        if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', cpf):
            raise ValidationError('Informe um CPF válido no formato 000.000.000-00.')
        return cpf
    
    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        if not telefone:
            return telefone

        numeros = re.sub(r'\D', '', telefone)

        if numeros.startswith('55') and len(numeros) > 11:
            numeros = numeros[2:]

        tamanho = len(numeros)

        if tamanho == 0:
            return ''

        if tamanho not in (10, 11):
            raise ValidationError('Informe um telefone válido com DDD (ex: 31 99999-9999).')

        if tamanho == 11:
            telefone_formatado = f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
        else:
            telefone_formatado = f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"

        return telefone_formatado
        
    def clean_endereco_busca(self):
        return self.cleaned_data.get('endereco_busca', '').strip()
        
    def clean(self):
        cleaned_data = super().clean()

        endereco_id = cleaned_data.get('endereco_id')
        endereco_busca = cleaned_data.get('endereco_busca', '')

        self._endereco_resolvido = None
        self._novo_endereco_dados = None

        if not endereco_busca:
            return cleaned_data
            
        if endereco_id:
            endereco = Endereco.objects.filter(pk=endereco_id).first()
            if endereco is None:
                self.add_error(
                    'endereco_busca',
                    'Selecione um endereço existente da lista ou deixe o campo vazio para cadastrar um novo.'
                )
                return cleaned_data

            self._endereco_resolvido = endereco
            return cleaned_data
            
        endereco_dados = self._parse_endereco_texto(endereco_busca)
        if endereco_dados is None:
            self.add_error(
                'endereco_busca',
                'Digite o endereço no formato "Rua, número - bairro, cidade - estado, CEP: 00000-000" ou selecione uma opção da lista.'
            )
            return cleaned_data
            
        self._novo_endereco_dados = endereco_dados
        return cleaned_data
        
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
        
    def save(self, commit=True):
        usuario_externo = super().save(commit=False)
        
        if self._endereco_resolvido is not None:
            usuario_externo.endereco = self._endereco_resolvido
        elif self._novo_endereco_dados is not None:
            endereco, _ = Endereco.objects.get_or_create(**self._novo_endereco_dados)
            usuario_externo.endereco = endereco
        else:
            usuario_externo.endereco = None
        
        if commit:
            usuario_externo.save()
        
        return usuario_externo
from django import forms
from django.core.exceptions import ValidationError
from .models import Atendimento

class AtendimentoForm(forms.ModelForm):
    class Meta:
        model = Atendimento
        fields = [
            'data_atendimento',
            'descricao', 
            'status', 
            'tipo_pessoa', 
            'aluno',
            'servidor',
            'usuario_externo']
        widgets = {
            "data_atendimento": forms.DateInput(attrs={"class": "datepicker"}),
            "tipo_pessoa": forms.RadioSelect(),
            "descricao": forms.Textarea(attrs={"rows": 5}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'tipo_pessoa' in self.fields:
            self.fields['tipo_pessoa'].choices = [
                (k, v) for k, v in self.fields['tipo_pessoa'].choices if k
            ]

            # 2. Define um rádio pré-selecionado por padrão se for um formulário NOVO
            # (Se for uma edição, ele mantém o valor que já estava salvo no banco)
            if not self.instance.pk:
                self.fields['tipo_pessoa'].initial = 'ALU'  # 'ALU' para Aluno, 'SER' para Servidor, etc.

        for field_name, field in self.fields.items():
            widget_type = field.widget.__class__.__name__
            error_class = ' is-invalid' if self.is_bound and field_name in self.errors else ''
            if widget_type == 'RadioSelect':
                field.widget.attrs.update({'class': f'form-check-input{error_class}'})
            elif widget_type in ['Select', 'SelectMultiple']:
                field.widget.attrs.update({'class': f'form-select{error_class}'})
            elif widget_type == 'DateInput':
                field.widget.attrs.update({'class': f'form-control datepicker{error_class}'})
            else:
                field.widget.attrs.update({'class': f'form-control{error_class}'})
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_pessoa = cleaned_data.get("tipo_pessoa")
        
        if not cleaned_data.get("data_atendimento"):
            raise ValidationError("A data do atendimento é obrigatória.")
        
        if tipo_pessoa == "ALU":
            if not cleaned_data.get("aluno"):
                raise ValidationError("Selecione o aluno atendido.")
            cleaned_data["servidor"] = None
            cleaned_data["usuario_externo"] = None
            
        elif tipo_pessoa == "SER":
            if not cleaned_data.get("servidor"):
                raise ValidationError("Selecione o servidor atendido.")
            cleaned_data["aluno"] = None
            cleaned_data["usuario_externo"] = None
            
        elif tipo_pessoa == "EXT":
            if not cleaned_data.get("usuario_externo"):
                raise ValidationError("Selecione o usuário externo atendido.")
            cleaned_data["aluno"] = None
            cleaned_data["servidor"] = None
            
        else:
            raise ValidationError("Selecione o tipo de pessoa atendida.")
        
        return cleaned_data
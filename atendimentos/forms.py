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
            "data": forms.DateInput(attrs={"type": "date"}),
            "tipo_pessoa": forms.RadioSelect(),
            "descricao": forms.Textarea(attrs={"rows": 5}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_pessoa = cleaned_data.get("tipo_pessoa")
        
        # Validação de data obrigatória
        if not cleaned_data.get("data_atendimento"):
            raise ValidationError("A data do atendimento é obrigatória.")
        
        # Validação de pessoa e limpeza das FKs não utilizadas
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
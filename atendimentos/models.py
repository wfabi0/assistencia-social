from django.db import models
from django.core.exceptions import ValidationError
from usuarios.models import Aluno, Servidor, UsuarioExterno

# Create your models here.
class Atendimento(models.Model):
    
    class TipoPessoa(models.TextChoices):
        ALUNO = "ALU", "Aluno"
        SERVIDOR = "SER", "Servidor"
        USUARIO_EXTERNO = "EXT", "Usuário Externo"
    
    class StatusAtendimento(models.TextChoices):
        PENDENTE = "PENDENTE", "Pendente"
        EM_ANDAMENTO = "EM_ANDAMENTO", "Em Andamento"
        CONCLUIDO = "CONCLUIDO", "Concluído"
    
    data_atendimento = models.DateField("Data do Atendimento")
    descricao = models.TextField("Descrição do Atendimento")
    status = models.CharField(
        "Status do Atendimento",
        max_length=20,
        choices=StatusAtendimento.choices,
        default=StatusAtendimento.PENDENTE,
    )
    tipo_pessoa = models.CharField(
        "Tipo de Pessoa",
        max_length=3,
        choices=TipoPessoa.choices,
    )
    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="atendimentos",
    )
    servidor = models.ForeignKey(
        Servidor,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="atendimentos",
    )
    usuario_externo = models.ForeignKey(
        UsuarioExterno,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="atendimentos",
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Atendimento"
        verbose_name_plural = "Atendimentos"
        db_table = "atendimento"
        ordering = ['-data_atendimento']
    
    def clean(self):
        fks = [self.aluno_id, self.servidor_id, self.usuario_externo_id]
        preenchidas = sum(map(lambda fk : fk is not None, fks))
        if preenchidas == 0:
            raise ValidationError("É necessário preencher um dos campos: aluno, servidor ou usuário externo.")
        elif preenchidas > 1:
            raise ValidationError("Apenas um dos campos deve ser preenchido: aluno, servidor ou usuário externo.")
    
    def pessoa_atendida(self):
        return self.aluno or self.servidor or self.usuario_externo
    
    def cargo_ou_curso(self):
        if self.aluno:
            return self.aluno.curso
        elif self.servidor:
            return self.servidor.cargo
        return ""
    
    def __str__(self):
        return f"{self.data_atendimento} - {self.pessoa_atendida()} - {self.cargo_ou_curso()} - {self.get_status_display()}"
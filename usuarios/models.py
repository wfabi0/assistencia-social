from django.db import models
from django.core.validators import RegexValidator

cpf_validator = RegexValidator(
    regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
    message="CPF deve estar no formato 000.000.000-00"
)

# Create your models here.
class Endereco(models.Model):
    logradouro = models.CharField("Logradouro", max_length=255)
    numero = models.CharField("Número", max_length=10)
    bairro = models.CharField("Bairro", max_length=255)
    cidade = models.CharField("Cidade", max_length=255)
    estado = models.CharField("Estado", max_length=255)
    cep = models.CharField("CEP", max_length=10)
    
    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"
        db_table = "endereco"
        
    def __str__(self):
        return f"{self.logradouro}, {self.numero} - {self.bairro}, {self.cidade} - {self.estado}, CEP: {self.cep}"

class Aluno(models.Model):
    ra = models.CharField("RA", max_length=20, unique=True)
    nome = models.CharField("Nome", max_length=255)
    curso = models.CharField("Curso", max_length=255)
    email = models.EmailField("Email", max_length=255, blank=True, null=True)
    telefone = models.CharField("Telefone", max_length=20, blank=True, null=True)
    endereco = models.ForeignKey(Endereco, on_delete=models.SET_NULL, null=True, blank=True, related_name="alunos")
    data_nascimento = models.DateField("Data de Nascimento")
    
    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"
        db_table = "aluno"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.ra} - {self.nome} - {self.curso} - {self.email}"

class Responsavel(models.Model):
    aluno = models.ForeignKey("Aluno", on_delete=models.CASCADE, related_name="responsaveis")
    nome = models.CharField("Nome", max_length=255)
    cpf = models.CharField("CPF", max_length=14, validators=[cpf_validator], unique=True)
    telefone = models.CharField("Telefone", max_length=20)
    email = models.EmailField("Email", max_length=255, blank=True, null=True)
    endereco = models.ForeignKey(Endereco, on_delete=models.SET_NULL, null=True, blank=True, related_name="responsaveis")
    parentesco = models.CharField("Parentesco", max_length=10)
    
    class Meta:
        verbose_name = "Responsável"
        verbose_name_plural = "Responsáveis"
        db_table = "responsavel"
        
    def __str__(self):
        return self.nome

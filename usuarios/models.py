from django.db import models

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
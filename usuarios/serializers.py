from rest_framework import serializers
from .models import (
    Endereco, Aluno, Responsavel, 
    Servidor, UsuarioExterno, Usuario
)

class EnderecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = ['id', 'logradouro', 'numero', 'bairro', 'cidade', 'estado', 'cep']

class ResponsavelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Responsavel
        fields = ['id', 'nome', 'cpf', 'telefone', 'email', 'parentesco']
        read_only_fields = ['id']

class AlunoSerializer(serializers.ModelSerializer):
    endereco = EnderecoSerializer(read_only=True)
    endereco_id = serializers.PrimaryKeyRelatedField(
        source='endereco',
        queryset=Endereco.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    responsaveis = ResponsavelSerializer(many=True, read_only=True)

    class Meta:
        model = Aluno
        fields = ['id', 'ra', 'nome', 'curso', 'email', 'telefone', 
                  'endereco', 'endereco_id', 'data_nascimento', 'responsaveis']
        read_only_fields = ['id']

class ServidorSerializer(serializers.ModelSerializer):
    endereco = EnderecoSerializer(read_only=True)
    endereco_id = serializers.PrimaryKeyRelatedField(
        source='endereco',
        queryset=Endereco.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Servidor
        fields = ['id', 'siape', 'nome', 'cargo', 'email', 'telefone', 
                  'endereco', 'endereco_id']
        read_only_fields = ['id']

class UsuarioExternoSerializer(serializers.ModelSerializer):
    endereco = EnderecoSerializer(read_only=True)
    endereco_id = serializers.PrimaryKeyRelatedField(
        source='endereco',
        queryset=Endereco.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = UsuarioExterno
        fields = ['id', 'nome', 'cpf', 'data_nascimento', 'email', 
                  'telefone', 'endereco', 'endereco_id']
        read_only_fields = ['id']

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'cress']
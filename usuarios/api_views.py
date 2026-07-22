from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from usuarios.models import Aluno, Servidor, UsuarioExterno, Endereco
from .serializers import (
    AlunoSerializer, ServidorSerializer, 
    UsuarioExternoSerializer, EnderecoSerializer
)

@extend_schema_view(
    list=extend_schema(description="Lista todos os alunos"),
    create=extend_schema(description="Cria um novo aluno"),
    retrieve=extend_schema(description="Retorna detalhes de um aluno"),
    update=extend_schema(description="Atualiza um aluno"),
    partial_update=extend_schema(description="Atualiza parcialmente um aluno"),
    destroy=extend_schema(description="Remove um aluno"),
)
class AlunoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Alunos
    """
    queryset = Aluno.objects.select_related('endereco').prefetch_related('responsaveis')
    serializer_class = AlunoSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['nome', 'ra', 'curso', 'email']
    filterset_fields = ['curso', 'data_nascimento']

    @action(detail=True, methods=['get'])
    def responsaveis(self, request, pk=None):
        """Retorna os responsáveis de um aluno"""
        aluno = self.get_object()
        responsaveis = aluno.responsaveis.all()
        from .serializers import ResponsavelSerializer
        serializer = ResponsavelSerializer(responsaveis, many=True)
        return Response(serializer.data)

@extend_schema_view(
    list=extend_schema(description="Lista todos os servidores"),
    create=extend_schema(description="Cria um novo servidor"),
    retrieve=extend_schema(description="Retorna detalhes de um servidor"),
)
class ServidorViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Servidores
    """
    queryset = Servidor.objects.select_related('endereco')
    serializer_class = ServidorSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nome', 'siape', 'cargo', 'email']

@extend_schema_view(
    list=extend_schema(description="Lista todos os usuários externos"),
    create=extend_schema(description="Cria um novo usuário externo"),
    retrieve=extend_schema(description="Retorna detalhes de um usuário externo"),
)
class UsuarioExternoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Usuários Externos
    """
    queryset = UsuarioExterno.objects.select_related('endereco')
    serializer_class = UsuarioExternoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nome', 'cpf', 'email']

class EnderecoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Endereços
    """
    queryset = Endereco.objects.all()
    serializer_class = EnderecoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['logradouro', 'bairro', 'cidade', 'cep']
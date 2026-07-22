from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from .models import Atendimento
from .serializers import AtendimentoSerializer, AtendimentoListSerializer
from usuarios.models import Aluno, Servidor, UsuarioExterno


@extend_schema_view(
    list=extend_schema(
        description="Lista todos os atendimentos com filtros",
        parameters=[
            OpenApiParameter(name='aluno', description='Filtrar por ID do aluno', type=int),
            OpenApiParameter(name='servidor', description='Filtrar por ID do servidor', type=int),
            OpenApiParameter(name='usuario_externo', description='Filtrar por ID do usuário externo', type=int),
            OpenApiParameter(name='tipo_pessoa', description='Filtrar por tipo de pessoa (ALU, SER, EXT)', type=str),
            OpenApiParameter(name='status', description='Filtrar por status (PENDENTE, EM_ANDAMENTO, CONCLUIDO)', type=str),
            OpenApiParameter(name='data_inicio', description='Data inicial (YYYY-MM-DD)', type=str),
            OpenApiParameter(name='data_fim', description='Data final (YYYY-MM-DD)', type=str),
        ]
    ),
    create=extend_schema(description="Cria um novo atendimento"),
    retrieve=extend_schema(description="Retorna detalhes de um atendimento"),
    update=extend_schema(description="Atualiza um atendimento"),
    partial_update=extend_schema(description="Atualiza parcialmente um atendimento"),
    destroy=extend_schema(description="Remove um atendimento"),
)
class AtendimentoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Atendimentos
    """
    queryset = Atendimento.objects.select_related(
        'aluno', 'servidor', 'usuario_externo'
    ).order_by('-data_atendimento', '-criado_em')
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['descricao', 'aluno__nome', 'servidor__nome', 'usuario_externo__nome']
    ordering_fields = ['data_atendimento', 'criado_em', 'status']
    ordering = ['-data_atendimento']

    def get_serializer_class(self):
        """Usa serializer diferente para listagem"""
        if self.action == 'list':
            return AtendimentoListSerializer
        return AtendimentoSerializer

    def get_queryset(self):
        """Adiciona filtros manuais via query params"""
        queryset = super().get_queryset()
        
        # Filtros manuais
        aluno = self.request.query_params.get('aluno')
        if aluno:
            queryset = queryset.filter(aluno_id=aluno)
        
        servidor = self.request.query_params.get('servidor')
        if servidor:
            queryset = queryset.filter(servidor_id=servidor)
        
        usuario_externo = self.request.query_params.get('usuario_externo')
        if usuario_externo:
            queryset = queryset.filter(usuario_externo_id=usuario_externo)
        
        tipo_pessoa = self.request.query_params.get('tipo_pessoa')
        if tipo_pessoa:
            queryset = queryset.filter(tipo_pessoa=tipo_pessoa)
        
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        data_inicio = self.request.query_params.get('data_inicio')
        if data_inicio:
            queryset = queryset.filter(data_atendimento__gte=data_inicio)
        
        data_fim = self.request.query_params.get('data_fim')
        if data_fim:
            queryset = queryset.filter(data_atendimento__lte=data_fim)
        
        return queryset

    @action(detail=False, methods=['get'], url_path='por-aluno')
    def por_aluno(self, request):
        """
        Retorna todos os atendimentos de um aluno específico
        Usage: /api/atendimentos/por-aluno/?aluno_id=1
        """
        aluno_id = request.query_params.get('aluno_id')
        if not aluno_id:
            return Response(
                {'error': 'Parâmetro aluno_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        aluno = get_object_or_404(Aluno, pk=aluno_id)
        atendimentos = self.queryset.filter(aluno=aluno)
        serializer = AtendimentoListSerializer(atendimentos, many=True)
        return Response({
            'aluno': {
                'id': aluno.id,
                'nome': aluno.nome,
                'ra': aluno.ra
            },
            'total': atendimentos.count(),
            'atendimentos': serializer.data
        })

    @action(detail=False, methods=['get'], url_path='por-servidor')
    def por_servidor(self, request):
        """
        Retorna todos os atendimentos de um servidor específico
        Usage: /api/atendimentos/por-servidor/?servidor_id=1
        """
        servidor_id = request.query_params.get('servidor_id')
        if not servidor_id:
            return Response(
                {'error': 'Parâmetro servidor_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        servidor = get_object_or_404(Servidor, pk=servidor_id)
        atendimentos = self.queryset.filter(servidor=servidor)
        serializer = AtendimentoListSerializer(atendimentos, many=True)
        return Response({
            'servidor': {
                'id': servidor.id,
                'nome': servidor.nome,
                'siape': servidor.siape
            },
            'total': atendimentos.count(),
            'atendimentos': serializer.data
        })

    @action(detail=False, methods=['get'], url_path='por-usuario-externo')
    def por_usuario_externo(self, request):
        """
        Retorna todos os atendimentos de um usuário externo específico
        Usage: /api/atendimentos/por-usuario-externo/?usuario_externo_id=1
        """
        usuario_externo_id = request.query_params.get('usuario_externo_id')
        if not usuario_externo_id:
            return Response(
                {'error': 'Parâmetro usuario_externo_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        usuario_externo = get_object_or_404(UsuarioExterno, pk=usuario_externo_id)
        atendimentos = self.queryset.filter(usuario_externo=usuario_externo)
        serializer = AtendimentoListSerializer(atendimentos, many=True)
        return Response({
            'usuario_externo': {
                'id': usuario_externo.id,
                'nome': usuario_externo.nome,
                'cpf': usuario_externo.cpf
            },
            'total': atendimentos.count(),
            'atendimentos': serializer.data
        })

    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        """
        Retorna estatísticas dos atendimentos
        """
        from django.db.models import Count
        from datetime import datetime, timedelta
        
        total = self.queryset.count()
        
        por_tipo_pessoa = self.queryset.values('tipo_pessoa').annotate(
            total=Count('id')
        ).order_by('-total')
        
        por_status = self.queryset.values('status').annotate(
            total=Count('id')
        ).order_by('-total')
        
        ultimos_30_dias = self.queryset.filter(
            data_atendimento__gte=datetime.now().date() - timedelta(days=30)
        ).count()
        
        return Response({
            'total_atendimentos': total,
            'ultimos_30_dias': ultimos_30_dias,
            'por_tipo_pessoa': por_tipo_pessoa,
            'por_status': por_status,
        })
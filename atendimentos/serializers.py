from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Atendimento
from usuarios.models import Aluno, Servidor, UsuarioExterno


class AtendimentoSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.CharField(source='aluno.nome', read_only=True)
    aluno_ra = serializers.CharField(source='aluno.ra', read_only=True)
    servidor_nome = serializers.CharField(source='servidor.nome', read_only=True)
    servidor_siape = serializers.CharField(source='servidor.siape', read_only=True)
    usuario_externo_nome = serializers.CharField(source='usuario_externo.nome', read_only=True)
    usuario_externo_cpf = serializers.CharField(source='usuario_externo.cpf', read_only=True)
    cargo_ou_curso = serializers.SerializerMethodField()
    
    aluno_id = serializers.PrimaryKeyRelatedField(
        source='aluno',
        queryset=Aluno.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    servidor_id = serializers.PrimaryKeyRelatedField(
        source='servidor',
        queryset=Servidor.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    usuario_externo_id = serializers.PrimaryKeyRelatedField(
        source='usuario_externo',
        queryset=UsuarioExterno.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Atendimento
        fields = [
            'id',
            'aluno',
            'aluno_id',
            'aluno_nome',
            'aluno_ra',
            'servidor',
            'servidor_id',
            'servidor_nome',
            'servidor_siape',
            'usuario_externo',
            'usuario_externo_id',
            'usuario_externo_nome',
            'usuario_externo_cpf',
            'tipo_pessoa',
            'status',
            'data_atendimento',
            'descricao',
            'cargo_ou_curso',
            'criado_em',
            'atualizado_em',
        ]
        read_only_fields = ['id', 'criado_em', 'atualizado_em']

    @extend_schema_field(serializers.CharField(allow_blank=True))
    def get_cargo_ou_curso(self, obj):
        """Retorna o curso do aluno ou cargo do servidor"""
        return obj.cargo_ou_curso()

    def validate(self, data):
        """Valida que apenas um tipo de pessoa foi informado"""
        aluno = data.get('aluno')
        servidor = data.get('servidor')
        usuario_externo = data.get('usuario_externo')
        
        fks = [aluno, servidor, usuario_externo]
        preenchidas = sum(1 for fk in fks if fk is not None)
        
        if preenchidas == 0:
            raise serializers.ValidationError(
                "É necessário informar um dos campos: aluno, servidor ou usuário externo"
            )
        elif preenchidas > 1:
            raise serializers.ValidationError(
                "Apenas um dos campos deve ser preenchido: aluno, servidor ou usuário externo"
            )
        
        if aluno:
            data['tipo_pessoa'] = Atendimento.TipoPessoa.ALUNO
        elif servidor:
            data['tipo_pessoa'] = Atendimento.TipoPessoa.SERVIDOR
        elif usuario_externo:
            data['tipo_pessoa'] = Atendimento.TipoPessoa.USUARIO_EXTERNO
        
        return data


class AtendimentoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem"""
    pessoa_atendida = serializers.SerializerMethodField()
    cargo_ou_curso = serializers.SerializerMethodField()
    
    class Meta:
        model = Atendimento
        fields = [
            'id',
            'tipo_pessoa',
            'pessoa_atendida',
            'cargo_ou_curso',
            'data_atendimento',
            'status',
            'descricao',
            'criado_em',
        ]

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_pessoa_atendida(self, obj):
        """Retorna o nome da pessoa atendida"""
        pessoa = obj.pessoa_atendida()
        return str(pessoa) if pessoa else None

    @extend_schema_field(serializers.CharField(allow_blank=True))
    def get_cargo_ou_curso(self, obj):
        """Retorna o curso do aluno ou cargo do servidor"""
        return obj.cargo_ou_curso()
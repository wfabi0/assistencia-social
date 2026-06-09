import os
import django
import random
from faker import Faker

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from usuarios.models import (
    Endereco,
    Aluno,
    Responsavel,
    Servidor,
    UsuarioExterno
)
from atendimentos.models import Atendimento

fake = Faker("pt_BR")


def gerar_cpf():
    return (
        f"{random.randint(100,999)}."
        f"{random.randint(100,999)}."
        f"{random.randint(100,999)}-"
        f"{random.randint(10,99)}"
    )


print("Criando endereços...")

enderecos = []

for _ in range(100):
    endereco = Endereco.objects.create(
        logradouro=fake.street_name(),
        numero=str(random.randint(1, 999)),
        bairro=fake.bairro(),
        cidade=fake.city(),
        estado="MG",
        cep=fake.postcode()
    )

    enderecos.append(endereco)

print("Criando alunos...")

alunos = []

for i in range(100):
    aluno = Aluno.objects.create(
        ra=f"RA{i+1:05d}",
        nome=fake.name(),
        curso=random.choice([
            "Informática",
            "Administração",
            "Agronomia",
            "Zootecnia",
            "Sistemas de Informação"
        ]),
        email=fake.email(),
        telefone=fake.phone_number(),
        endereco=random.choice(enderecos),
        data_nascimento=fake.date_of_birth(
            minimum_age=16,
            maximum_age=30
        )
    )

    alunos.append(aluno)

print("Criando responsáveis...")

for aluno in alunos:

    quantidade = random.randint(1, 2)

    for _ in range(quantidade):

        Responsavel.objects.create(
            aluno=aluno,
            nome=fake.name(),
            cpf=gerar_cpf(),
            telefone=fake.phone_number(),
            email=fake.email(),
            endereco=random.choice(enderecos),
            parentesco=random.choice([
                "Pai",
                "Mãe",
                "Tio",
                "Avó",
                "Avô"
            ])
        )

print("Criando servidores...")

servidores = []

for i in range(50):

    servidor = Servidor.objects.create(
        siape=f"SIAPE{i+1:06d}",
        nome=fake.name(),
        cargo=random.choice([
            "Professor",
            "Técnico Administrativo",
            "Coordenador",
            "Assistente Social"
        ]),
        email=fake.email(),
        telefone=fake.phone_number(),
        endereco=random.choice(enderecos)
    )

    servidores.append(servidor)

print("Criando usuários externos...")

externos = []

for _ in range(50):

    externo = UsuarioExterno.objects.create(
        nome=fake.name(),
        cpf=gerar_cpf(),
        data_nascimento=fake.date_of_birth(
            minimum_age=18,
            maximum_age=70
        ),
        email=fake.email(),
        telefone=fake.phone_number(),
        endereco=random.choice(enderecos)
    )

    externos.append(externo)

print("Criando atendimentos...")

for _ in range(200):

    tipo = random.choice([
        "ALU",
        "SER",
        "EXT"
    ])

    atendimento = Atendimento(
        data_atendimento=fake.date_time_this_year(),
        descricao=fake.text(max_nb_chars=200),
        status=random.choice([
            "PENDENTE",
            "EM_ANDAMENTO",
            "CONCLUIDO"
        ]),
        tipo_pessoa=tipo
    )

    if tipo == "ALU":
        atendimento.aluno = random.choice(alunos)

    elif tipo == "SER":
        atendimento.servidor = random.choice(servidores)

    else:
        atendimento.usuario_externo = random.choice(externos)

    atendimento.full_clean()
    atendimento.save()

print("Banco populado com sucesso!")
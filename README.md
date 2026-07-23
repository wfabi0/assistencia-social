# Sistema de Registro de Atendimentos

Sistema web para registro e acompanhamento de atendimentos do IFMG Campus São João Evangelista. O projeto centraliza cadastros, históricos e exportação de informações, com autenticação e controle de acesso por permissões do Django.

## Objetivo do sistema

Organizar o registro de alunos, servidores, usuários externos e atendimentos em uma aplicação única, substituindo processos dispersos e facilitando consulta e histórico.

## Requisitos

- Python 3.14 ou superior.
- MySQL 8 ou compatível.
- Ambiente virtual Python.
- Dependências listadas em `requirements.txt`.

## Instalação das dependências

Crie e ative o ambiente virtual e instale os pacotes:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Criação do banco MySQL

Crie o banco antes de executar as migrações:

```sql
CREATE DATABASE assistencia_social
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

## Versão do Python

O projeto foi preparado para Python 3.14+.

## Configuração do `.env`

Existe um template em `.env.example`. Copie-o para `.env` e ajuste os valores:

```bash
copy .env.example .env
```

Conteúdo esperado:

```env
SECRET_KEY=sua-chave-aqui
DEBUG=True
DB_NAME=assistencia_social
DB_USER=root
DB_PASSWORD=senha
DB_HOST=localhost
DB_PORT=3306
ALLOWED_HOSTS=*
```

Não envie o arquivo `.env` para o repositório.

## Execução das migrações

Depois de configurar o banco e o `.env`, execute:

```bash
python manage.py migrate
```

## Criação do superusuário

```bash
python manage.py createsuperuser
```

Use esse usuário para acessar o painel administrativo e configurar grupos, permissões e outros cadastros iniciais.

## Criação de usuário comum

Os usuários comuns devem ser criados pelo painel administrativo.

## Grupos e permissões

O sistema usa permissões padrão do Django nas views de alunos, servidores, usuários externos e atendimentos. Crie os grupos no admin e associe as permissões conforme o perfil.

## Como iniciar o servidor

```bash
python manage.py runserver
```

Depois, acesse `http://127.0.0.1:8000/`.
> Para `http://127.0.0.1:8000/admin` para as configurações iniciais de permissões e usuário inicial sem superuser.

## Como popular o banco de demonstração

O arquivo `popular_banco.py` cria dados fictícios de endereços, alunos, responsáveis, servidores, usuários externos e atendimentos.

```bash
python popular_banco.py
```

Execute esse script somente em ambiente de desenvolvimento, porque ele insere dados de teste em volume.

## Funcionalidades

- Autenticação com login e logout.
- Controle de acesso por permissões do Django.
- CRUD de alunos, servidores e usuários externos.
- Cadastro e listagem de atendimentos.
- Histórico de atendimentos por pessoa.
- Exportação de histórico em PDF.
- Autocomplete de endereço, responsável e curso.
- API REST e documentação Swagger/OpenAPI em `/api/docs/`.

## Equipe

- Fábio Emanuell Pereira Milagres
- Felipe Martins dos Santos
- Leonardo Daglio Teixeira
- Liliane Mariano Lourenço
- Julya Alves Cordeiro de Macedo
- Tayllon Junior Maciel Rodrigues

## Como Contribuir (Fluxo de Trabalho)

Para mantermos o projeto organizado e evitarmos conflitos no código, utilizaremos um padrão estrito para a criação de branches. **Nunca faça alterações diretas na branch `main`.**

### Padrão para nome das Branches

Toda nova branch deve seguir o formato: `seu-nome/nome-da-tarefa`

> **Exemplo Prático:** > `fabio/configuracao-inicial`

### Passo a Passo para Enviar uma Alteração

1. **Atualize sua branch principal** (garanta que você tem a versão mais recente do projeto):

```bash
git checkout main
git pull origin main
```

2. **Crie uma nova branch para sua tarefa**:

```bash
git checkout -b seu-nome/nome-da-tarefa
```

> **Exemplo:**

```bash
git checkout -b fabio/tela-login
```

3. **Realize as alterações necessárias no projeto**.

4. **Adicione os arquivos modificados**:

```bash
git add .
```

5. **Faça o commit das alterações**:

```bash
git commit -m "descrição da alteração"
```

> **Exemplos de commits:**

```bash
git commit -m "adiciona tela de login"
git commit -m "corrige validação de formulário"
git commit -m "melhora estilização da dashboard"
```

6. **Envie sua branch para o GitHub**:

```bash
git push origin seu-nome/nome-da-tarefa
```

7. **Abra um Pull Request (PR)**:

- Acesse o repositório no GitHub.
- Clique em **Compare & Pull Request**.
- Descreva as alterações realizadas.
- Solicite revisão antes do merge.

## Boas Práticas

- Sempre mantenha sua branch atualizada com a `main`.
- Faça commits pequenos e organizados.
- Utilize mensagens de commit claras e padronizadas.
- Revise seu código antes de abrir um Pull Request.
- Nunca envie arquivos desnecessários para o repositório.

## Documentação da API

A documentação da API está disponível em `/api/docs/`.
> Para acessar a documentação é necessário estar logado como super usuário.
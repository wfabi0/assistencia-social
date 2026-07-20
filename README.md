# 📝 Sistema de Registro de Atendimentos

Desenvolvimento do sistema de registro de atendimentos para o IFMG Campus São João Evangelista! Este sistema foi projetado para substituir a antiga base em PHP por uma solução mais eficiente e amigável, utilizando Python. 🚀

---

## 🛠️ Tecnologias Utilizadas

- **Python**: Linguagem principal para o backend.
- **Django**: Framework web para desenvolvimento rápido e seguro.
- **MySQL**: Banco de dados relacional robusto para armazenamento seguro das informações.
- **HTML, CSS e JavaScript**: Para a interface do usuário.

---

## ⚙️ Como Configurar o Projeto

Siga os passos abaixo para configurar o ambiente de desenvolvimento:

1. **Clone o repositório**:

   ```bash
   git clone https://github.com/wfabi0/assistencia-social.git
   ```

2. **Crie e ative um ambiente virtual**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. **Instale as dependências**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente**:

   ```bash
   cp .env.exemple .env
   ```

   Edite o arquivo `.env` e configure as variáveis com suas informações do banco de dados:

   ```env
   SECRET_KEY=sua-chave-aqui
   DEBUG=True
   DB_NAME=assistencia_social
   DB_USER=root
   DB_PASSWORD=sua_senha_aqui
   DB_HOST=localhost
   DB_PORT=3306
   ```

   > **Nota:** Nunca commite o arquivo `.env` com dados sensíveis. Use o `.env.exemple` como template. NÃO APAGUE O `.env.example`.

5. **Realize as migrações do banco de dados**:

   ```bash
   python manage.py migrate
   ```

6. **Inicie o servidor de desenvolvimento**:

   ```bash
   python manage.py runserver
   ```

7. **Acesse o sistema**:
   Abra o navegador e vá para http://127.0.0.1:8000.

---

## 👥 Membros da Equipe

- Fábio Emanuell Pereira Milagres
- Felipe Martins dos Santos
- Leonardo Daglio Teixeira
- Liliane Mariano Lourenço
- Julya Alves Cordeiro de Macedo
- Tayllon Junior Maciel Rodrigues

---

## 🔄 Como Contribuir (Fluxo de Trabalho)

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

---

## 📌 Boas Práticas

- Sempre mantenha sua branch atualizada com a `main`.
- Faça commits pequenos e organizados.
- Utilize mensagens de commit claras e padronizadas.
- Revise seu código antes de abrir um Pull Request.
- Nunca envie arquivos desnecessários para o repositório.

---

## 📚 Documentação da API

Documentação usando Swagger/OpenAPI.

Acesse por `/api/docs/`
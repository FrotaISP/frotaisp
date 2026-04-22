# Frota ISP

Sistema web para gestao de frotas voltado para provedores de internet (ISP), com foco em operacao, rastreabilidade e visibilidade dos custos da frota.

## Sobre o projeto

O Frota ISP organiza o controle operacional de veiculos utilizados por empresas de telecomunicacoes. A aplicacao foi construida em Django com arquitetura modular por apps, cobrindo o fluxo principal da rotina de frota.

Hoje o sistema inclui:

- autenticacao e gestao de usuarios
- cadastro de motoristas e veiculos
- registro de viagens
- controle de abastecimentos
- registro de manutencoes
- dashboard operacional
- relatorios em HTML, PDF e Excel
- endpoints REST iniciais para dashboard e veiculos

## Arquitetura

O projeto segue uma arquitetura modular baseada em apps Django:

```text
apps/
  accounts/      # autenticacao, perfis e usuarios
  core/          # modelos e mixins compartilhados
  dashboard/     # indicadores, visao geral e API resumida
  drivers/       # cadastro e gestao de motoristas
  fuel/          # abastecimentos
  maintenance/   # manutencoes e alertas
  reports/       # relatorios HTML, PDF e Excel
  trips/         # viagens e deslocamentos
  vehicles/      # cadastro e controle de veiculos
config/          # settings, urls, wsgi/asgi
```

## Stack

- Python 3.11+
- Django 4.2
- Django REST Framework
- django-cors-headers
- SQLite para desenvolvimento local
- PostgreSQL por variaveis de ambiente
- WeasyPrint para PDFs
- openpyxl para planilhas Excel

## Como executar

### 1. Clone o repositorio

```bash
git clone https://github.com/FrotaISP/frotaisp.git
cd frotaisp
```

### 2. Crie e ative um ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### 3. Instale as dependencias

```bash
pip install -r requirements.txt
```

### 4. Configure o ambiente

Crie um arquivo `.env` com base em `.env.example`.

Por padrao, se `DB_NAME` estiver vazio, o projeto usa SQLite localmente. Para PostgreSQL, basta preencher as variaveis `DB_*`.

### 5. Aplique as migracoes

```bash
python manage.py migrate
```

### 6. Crie um superusuario

```bash
python manage.py createsuperuser
```

### 7. Rode o servidor

```bash
python manage.py runserver
```

Acesse em [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Testes

Execute a suite com:

```bash
python manage.py test
```

## Variaveis de ambiente principais

```env
DEBUG=True
SECRET_KEY=substitua-por-uma-chave-secreta-longa-e-aleatoria
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432
```

## Funcionalidades atuais

- gestao de usuarios com perfis e papeis
- controle de permissao por perfil
- cadastro completo de motoristas
- cadastro e acompanhamento de veiculos
- registro de viagens com odometro
- abastecimentos com comprovante e custo total calculado
- manutencoes com alertas futuros
- dashboard com cards e alertas operacionais
- exportacao de relatorios em PDF e Excel

## Melhorias futuras

- integracao com APIs externas de rastreamento ou GPS
- ampliacao da cobertura da API REST
- testes de integracao para fluxos principais
- relatorios analiticos adicionais
- pipeline de deploy automatizado

## Contribuicao

Sinta-se a vontade para abrir issues e pull requests com correcoes, melhorias ou novas funcionalidades.

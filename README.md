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
config/
  settings.py        # seletor por ambiente
  settings_base.py   # configuracoes compartilhadas
  settings_dev.py    # desenvolvimento
  settings_prod.py   # producao
```

Importante: o código Django ativo está em `apps/`. Existem pastas legadas duplicadas na raiz do repositório, mas elas não são a fonte principal do projeto atual. Veja `docs/estrutura-projeto.md`.

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

Por padrao, o projeto usa `APP_ENV=dev`. Nesse modo, se `DB_NAME` estiver vazio, o banco local sera SQLite. Para PostgreSQL, basta preencher as variaveis `DB_*`.
Para uma base de producao, use tambem `.env.prod.example` como referencia.

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

## Settings por ambiente

O entrypoint padrao continua sendo `config.settings`, mas ele seleciona o modulo correto conforme `APP_ENV`.

- `APP_ENV=dev`: usa `config.settings_dev`
- `APP_ENV=prod`: usa `config.settings_prod`

Exemplo para producao:

```env
APP_ENV=prod
DEBUG=False
SECRET_KEY=uma-chave-secreta-segura
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com
CSRF_TRUSTED_ORIGINS=https://seu-dominio.com,https://www.seu-dominio.com
```

## Testes

Execute a suite com:

```bash
python manage.py test
```

### Preparacao recomendada para testes

Antes de rodar testes manuais ou de homologacao, valide este checklist:

1. aplique as migracoes em um banco limpo
2. confirme que `APP_ENV=dev` no ambiente local de teste
3. crie um usuario admin e perfis de `manager`, `operator` e `driver`
4. cadastre ao menos um veiculo, um motorista, uma viagem, um abastecimento e uma manutencao
5. valide exportacao de relatorios em HTML, Excel e PDF
6. valide acesso e bloqueios por papel nas telas principais
7. rode `python manage.py test` antes de qualquer teste exploratorio

## Variaveis de ambiente principais

```env
APP_ENV=dev
DEBUG=True
SECRET_KEY=substitua-por-uma-chave-secreta-longa-e-aleatoria
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
CORS_ALLOWED_ORIGINS=
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
- API REST inicial para dashboard e veiculos

## Melhorias futuras

- integracao com APIs externas de rastreamento ou GPS
- ampliacao da cobertura da API REST
- testes de integracao para fluxos principais
- relatorios analiticos adicionais
- pipeline de deploy automatizado

## Contribuicao

Sinta-se a vontade para abrir issues e pull requests com correcoes, melhorias ou novas funcionalidades.

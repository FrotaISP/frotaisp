# Estrutura do Projeto

## Fonte canônica

O código ativo do Django fica em `apps/` e é esse conjunto que está registrado em `INSTALLED_APPS`.

Apps usados atualmente:

- `apps/accounts`
- `apps/core`
- `apps/dashboard`
- `apps/drivers`
- `apps/fuel`
- `apps/maintenance`
- `apps/mobile_api`
- `apps/reports`
- `apps/trips`
- `apps/vehicles`

## Pastas duplicadas na raiz

Existem pastas legadas na raiz do repositório com nomes repetidos, como:

- `accounts/`
- `core/`
- `dashboard/`
- `drivers/`
- `fuel/`
- `maintenance/`
- `trips/`
- `vehicles/`

Essas pastas **não são a fonte principal do projeto atual**. A configuração do Django e as rotas apontam para `apps.*`.

## Regra prática para manutenção

Quando for editar backend Django:

1. procure primeiro em `apps/`
2. confirme a referência em `config/settings_base.py` ou `config/urls.py`
3. evite criar código novo nas pastas duplicadas da raiz

## Limpeza futura recomendada

A remoção física dessas pastas legadas deve ser feita em uma etapa separada, com revisão de histórico e busca por imports antigos, para evitar apagar algo útil por engano.

Fluxo sugerido para essa limpeza:

1. validar que não existem imports ativos para as pastas da raiz
2. mover qualquer arquivo útil remanescente para `apps/`
3. remover as pastas legadas em um commit dedicado
4. rodar `manage.py check`, `manage.py test` e revisão manual das telas principais

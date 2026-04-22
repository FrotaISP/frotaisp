# Arquitetura do Sistema FleetISP

## 1. Visão Geral

O **FleetISP** é um sistema de gerenciamento de frotas desenvolvido para Provedores de Internet (ISP). Ele permite o controle completo de veículos, motoristas, viagens técnicas, consumo de combustível e manutenções, com dashboards gerenciais e relatórios em PDF.

O sistema adota uma **arquitetura modular** baseada no framework Django, separando as responsabilidades em aplicações independentes (apps). Isso facilita a manutenção, testabilidade e evolução do software.

## 2. Pilha Tecnológica

| Camada          | Tecnologias                                  |
|-----------------|----------------------------------------------|
| **Back‑end**    | Python 3.11, Django 4.2, Django REST Framework |
| **Banco de Dados** | PostgreSQL 15 (produção) / SQLite (desenvolvimento) |
| **Front‑end**   | HTML5, CSS3, Bootstrap 5, Chart.js, Leaflet   |
| **APIs**        | REST (Django REST Framework)                 |
| **Relatórios**  | WeasyPrint (PDF), openpyxl (Excel)           |
| **Infraestrutura** | Docker, Docker Compose, Gunicorn, Nginx     |

## 3. Estrutura de Diretórios

frota_ISP/
├── config/ # Configurações globais do Django
├── apps/ # Módulos (apps) do domínio
│ ├── core/ # Modelos abstratos e utilitários
│ ├── accounts/ # Autenticação e perfis de usuário
│ ├── vehicles/ # Gestão de veículos (CRUD + API)
│ ├── drivers/ # Gestão de motoristas
│ ├── trips/ # Registro de viagens / ordens de serviço
│ ├── fuel/ # Controle de abastecimentos
│ ├── maintenance/ # Manutenções e alertas
│ ├── reports/ # Geração de relatórios PDF
│ └── dashboard/ # Painel principal com métricas
├── static/ # Arquivos estáticos (CSS, JS, imagens)
├── media/ # Uploads de usuários (fotos, notas fiscais)
├── templates/ # Templates HTML globais
├── docker/ # Configurações para containerização
├── scripts/ # Scripts utilitários (populate_db.py)
├── docs/ # Documentação
└── manage.py

## 4. Arquitetura Modular (Apps Django)

Cada app é responsável por um domínio específico e pode evoluir independentemente.

### 4.1 App `core`
Fornece classes abstratas reutilizáveis, como `TimeStampedModel` (com campos `created_at` e `updated_at`), herdada por todos os modelos do sistema.

### 4.2 App `accounts`
Gerencia autenticação e registro de usuários. Utiliza o modelo `User` padrão do Django e formulários customizados com classes Bootstrap. As rotas incluem:
- `/accounts/login/`
- `/accounts/logout/`
- `/accounts/registro/`

### 4.3 App `vehicles`
Responsável pelo cadastro e manutenção dos veículos da frota.
- **Modelo**: `Vehicle` (placa, modelo, hodômetro, motorista atual).
- **Views**: CRUD completo com class‑based views.
- **API REST**: `VehicleViewSet` para integração com sistemas externos.

### 4.4 App `drivers`
Gerencia os motoristas associados a usuários do sistema.
- **Modelo**: `Driver` (CNH, validade, telefone, disponibilidade).
- **Relacionamento**: `OneToOneField` com `User`.

### 4.5 App `trips`
Registra as viagens realizadas (ordens de serviço).
- **Modelo**: `Trip` (veículo, motorista, horários, quilometragem, destino).
- **Sinais (`signals.py`)**: Atualiza automaticamente o hodômetro do veículo e libera/associa o motorista ao finalizar/iniciar uma viagem.

### 4.6 App `fuel`
Controle de abastecimentos.
- **Modelo**: `FuelRecord` (litros, preço, posto, hodômetro).
- **Cálculo automático**: `total_cost = liters * price_per_liter`.

### 4.7 App `maintenance`
Gestão de manutenções preventivas e corretivas.
- **Modelo**: `Maintenance` (tipo, custo, oficina, próximos alertas).
- **Alertas**: Baseados em quilometragem ou data futura.

### 4.8 App `reports`
Geração de relatórios gerenciais.
- **Relatório de Combustível**: PDF com totais por período e detalhamento.
- **Relatório de Viagens**: PDF com quilometragem percorrida.
- **Utils (`utils.py`)**: Funções auxiliares para agregação de dados.

### 4.9 App `dashboard`
Painel principal com indicadores chave (KPIs).
- **View**: `dashboard_view` que consolida dados de todos os apps.
- **Template**: `index.html` autocontido (não estende `base.html`).
- **API interna**: `/api/dashboard/summary/` para atualizações assíncronas (opcional).

## 5. Fluxo de Dados da Dashboard

1. O usuário acessa a raiz `/`.
2. A view `dashboard_view` consulta os modelos `Vehicle`, `Driver`, `Trip`, `FuelRecord` e `Maintenance`.
3. Calcula totais, médias e consolida os últimos 7 dias de consumo.
4. Renderiza o template `dashboard/index.html` com o contexto.
5. O template utiliza `json_script` para passar dados de consumo ao JavaScript.
6. O script `dashboard.js` inicializa o gráfico Chart.js e o mapa Leaflet.

## 6. APIs REST

| Endpoint                     | Métodos            | Descrição                         |
|------------------------------|--------------------|-----------------------------------|
| `/api/vehicles/`             | GET, POST          | Lista/cria veículos               |
| `/api/vehicles/{id}/`        | GET, PUT, DELETE   | Detalha/atualiza/exclui veículo   |
| `/api/dashboard/summary/`    | GET                | Retorna resumo em JSON para dashboard |

Futuramente podem ser adicionadas APIs para `drivers`, `trips`, `fuel` e `maintenance`.

## 7. Infraestrutura com Docker

O projeto é containerizado utilizando Docker e Docker Compose, com três serviços principais:

- **db**: PostgreSQL 15, com volume persistente.
- **web**: Aplicação Django servida via Gunicorn (3 workers).
- **nginx**: Proxy reverso que serve arquivos estáticos/mídia e encaminha requisições para o Gunicorn.

### Diagrama simplificado:

[Usuário] → Nginx (porta 80) → Gunicorn (Django) → PostgreSQL
↓
/static/ e /media/

## 8. Decisões de Design

- **Modularidade**: Cada domínio é um app Django independente, permitindo reuso e manutenção isolada.
- **Templates autocontidos**: A dashboard não estende `base.html` para manter flexibilidade visual e evitar conflitos.
- **Uso de `TimeStampedModel`**: Todos os modelos herdam campos de auditoria (`created_at`, `updated_at`).
- **Variáveis de ambiente**: Configurações sensíveis (SECRET_KEY, banco de dados) são gerenciadas via `python-decouple` e arquivo `.env`.
- **Segurança**: Autenticação obrigatória para todas as views (`LoginRequiredMixin`). APIs REST exigem token/sessão (`IsAuthenticated`).

## 9. Considerações de Segurança

- Em produção, `DEBUG=False` e `ALLOWED_HOSTS` restrito ao domínio real.
- O arquivo `.env` **nunca** é versionado.
- CORS é configurado para permitir apenas origens confiáveis em produção.
- Senhas são armazenadas com hash (PBKDF2) pelo Django.

## 10. Testes e População de Dados

O script `scripts/populate_db.py` utiliza a biblioteca `Faker` para gerar dados de teste realistas, incluindo:
- Motoristas com CNH e validade.
- Veículos de diferentes modelos.
- Viagens históricas (algumas em andamento).
- Abastecimentos e manutenções.

Isso permite testar a dashboard e os relatórios rapidamente.

## 11. Possíveis Evoluções

- **Rastreamento GPS**: Integração com APIs de localização em tempo real.
- **App Mobile**: PWA para motoristas registrarem início/fim de viagem e abastecimentos.
- **Relatórios em Excel**: Além do PDF, exportar dados para `.xlsx`.
- **Notificações por e‑mail**: Alertas de manutenção e vencimento de CNH.
- **Internacionalização**: Suporte a múltiplos idiomas.

---

*Documentação gerada em 21/04/2026 – versão 1.0*
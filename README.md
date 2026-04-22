# 🚗 Frota ISP

Sistema web para gestão de frotas voltado para provedores de internet (ISP), permitindo controle de motoristas, abastecimento, operações e visualização de dados em dashboard.

---

## 📌 Sobre o projeto

O **Frota ISP** é uma aplicação desenvolvida com foco em organização e controle operacional de veículos utilizados por empresas de telecomunicações.

O sistema permite:

* Gerenciamento de motoristas
* Controle de abastecimentos
* Monitoramento de uso da frota
* Visualização de dados em dashboards
* Organização modular por apps

---

## 🏗️ Arquitetura

O projeto segue uma arquitetura modular baseada em apps do Django:

```
apps/
  accounts/   # Autenticação e usuários
  core/       # Funcionalidades base e utilidades
  dashboard/  # Visualização e métricas
  drivers/    # Gestão de motoristas
  fuel/       # Controle de abastecimento
```

---

## ⚙️ Tecnologias utilizadas

* Python
* Django
* Django REST Framework (se aplicável)
* SQLite / PostgreSQL (ajustável)
* HTML / CSS / JavaScript

---

## 🚀 Como rodar o projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/SEU-USUARIO/frota-isp.git
cd frota-isp
```

### 2. Criar ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Crie um arquivo `.env` baseado no `.env.example`

---

### 5. Aplicar migrações

```bash
python manage.py migrate
```

---

### 6. Criar superusuário

```bash
python manage.py createsuperuser
```

---

### 7. Rodar o servidor

```bash
python manage.py runserver
```

Acesse em:
👉 http://127.0.0.1:8000

---

## 📊 Funcionalidades

* Cadastro e gestão de motoristas
* Controle de abastecimento
* Organização por módulos (apps)
* Dashboard com visão geral
* Sistema de autenticação

---

## 🔒 Variáveis de ambiente

Exemplo de configuração:

```
DEBUG=True
SECRET_KEY=sua_chave_secreta
DATABASE_URL=sqlite:///db.sqlite3
```

---

## 📁 Estrutura do projeto

```
frota_isp/
  apps/
  manage.py
  requirements.txt
```

---

## 🧠 Melhorias futuras

* Integração com APIs externas (rastreamento/GPS)
* Relatórios avançados
* Controle de manutenção de veículos
* Sistema de permissões mais granular
* Deploy em ambiente cloud

---

## 🤝 Contribuição

Sinta-se livre para abrir issues ou enviar pull requests.

---

## 📄 Licença

Este projeto está sob a licença MIT.

---

## 👨‍💻 Autor

Desenvolvido por João Wittler

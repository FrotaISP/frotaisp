# FleetISP Driver App

Aplicativo mobile inicial para motoristas, construído com Expo/React Native.

## O que esta versão já faz

- login com token na API Django
- carregar perfil do motorista
- ver veículo vinculado e viagens do dia
- iniciar viagem
- finalizar viagem
- enviar checklist rápido
- atualizar localização manualmente
- visualizar documentos próximos do vencimento

## Requisitos

- Node.js 20+
- npm ou yarn
- Expo Go no Android/iPhone ou emulador configurado
- API Django do FleetISP rodando e acessível

## Instalação

```bash
cd mobile/driver-app
npm install
npm start
```

Depois abra o app com:

- `a` para Android
- `i` para iOS
- QR code no Expo Go

## Endereço da API

O app usa por padrão:

```text
http://191.123.65.10:5000/api/mobile
```

Se o backend estiver em outro endereço, altere `src/api/client.js`.

## Backend necessário

No projeto Django principal, rode:

```bash
python manage.py migrate
```

Isso é obrigatório porque a autenticação mobile usa `rest_framework.authtoken`.

## Próximos passos sugeridos

- login por CPF/telefone
- captura real de GPS do aparelho
- upload de foto no checklist e ocorrências
- push notifications
- modo offline com fila de sincronização
- publicação Android

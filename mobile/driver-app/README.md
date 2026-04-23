# FleetISP Driver App

Aplicativo mobile inicial para motoristas, construído com Expo/React Native.

## O que esta versão já faz

- login com token na API Django
- painel inicial com visão rápida do dia
- viagens com iniciar/finalizar
- checklist rápido de saída
- rastreamento manual do veículo
- perfil do motorista
- visualização de documentos próximos do vencimento

## Requisitos

- Node.js 20+
- npm ou yarn
- Expo Go no Android/iPhone ou emulador configurado
- API Django do FleetISP rodando e acessível

## Instalação local

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

O app usa por padrão o valor configurado em `app.json`:

```text
http://191.123.65.10:5000/api/mobile
```

Se o backend estiver em outro endereço, altere o campo `expo.extra.apiBaseUrl` em `app.json`.

## Backend necessário

No projeto Django principal, rode:

```bash
python manage.py migrate
```

Isso é obrigatório porque a autenticação mobile usa `rest_framework.authtoken`.

## Fluxo sugerido de teste

1. Garanta que o usuário tenha `UserProfile.role = 'driver'`.
2. Garanta que exista um `Driver` vinculado ao mesmo `User`.
3. Se quiser restringir o veículo do motorista, preencha `Vehicle.current_driver`.
4. Faça login no app com o mesmo usuário e senha do Django.
5. Teste iniciar viagem, finalizar viagem, checklist e atualização de localização.

## Gerar instalável Android

Instale o EAS CLI:

```bash
npm install -g eas-cli
```

Depois, dentro de `mobile/driver-app`, rode:

```bash
eas login
eas build -p android --profile preview
```

Esse perfil gera um `.apk` para instalar diretamente no celular.

Para produção na Play Store:

```bash
eas build -p android --profile production
```

Esse perfil gera um `.aab`.

## Próximos passos sugeridos

- login por CPF/telefone
- captura real de GPS do aparelho
- upload de foto no checklist e ocorrências
- push notifications
- modo offline com fila de sincronização
- publicação Android

# AlterMe

App utilitário focado na criação de avatares gerados por Inteligência Artificial. A ideia é que você possa transformar suas próprias fotos em personagens de diferentes mundos e estilos.

O Gerador de Alter Ego é o motor principal do app. Ele recebe uma selfie enviada pelo usuário junto de um tema (o "universo" da criação, como Fantasia, Cyberpunk, etc.). O backend envia isso para um modelo de visão e geração via IA que analisa seu rosto e cria uma imagem totalmente nova.

A aplicação roda em Flutter com backend FastAPI que gerencia e cria os alter egos gerados a partir das selfies. O projeto hoje roda com **Flutter + FastAPI + MySQL + MinIO**, substituindo a stack antiga baseada em Supabase.

## Demonstração

<video src="assets/demo.mp4" controls="controls" width="100%"></video>

## Funcionalidades

- autenticação com login e cadastro;
- captura e envio de selfie;
- geração de alter ego por universo;
- upload de imagens no MinIO;
- persistência de dados no MySQL.

## Stack

- Flutter
- BLoC
- go_router
- get_it
- Dio
- FastAPI
- aiomysql
- boto3
- MySQL
- MinIO

## Estrutura do projeto

- `lib/`: app Flutter.
- `lib/core/`: auth, DI, rotas e rede.
- `lib/features/`: features por domínio da interface.
- `backend/app/`: API FastAPI.
- `backend/app/handlers/`: rotas HTTP.
- `backend/app/domain/`: casos de uso e contratos.
- `backend/app/repositories/`: acesso ao MySQL.
- `backend/app/services/`: geração, prompt e visão.
- `backend/tests/`: testes do backend.

## Pré-requisitos

- Flutter instalado.
- Docker Desktop em execução.
- Python 3.11+ se for rodar o backend fora do Docker.

## Como rodar

### Opção 1: subir tudo com Docker

No Windows, rode:

```powershell
./start.ps1
```

Isso sobe MySQL, MinIO e o backend. Quando terminar, o script mostra os endereços úteis:

- API: `http://localhost:8000`
- documentação: `http://localhost:8000/docs`
- MinIO Console: `http://localhost:9001`

Comandos úteis:

```powershell
./start.ps1 -Logs
./start.ps1 -Rebuild
./start.ps1 -Down
```

### Opção 2: rodar o Flutter separado

Instale dependências e execute o app:

```bash
flutter pub get
flutter run
```

Para testes:

```bash
flutter test
```

### Opção 3: rodar o backend separado

Entre na pasta do backend e instale as dependências:

```bash
cd backend
pip install -r requirements.txt
```

Depois rode a API:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Para testes do backend:

```bash
cd backend
python -m pytest tests -q
```

## Variáveis de ambiente

O backend lê as configurações de `backend/.env` e, no Docker, também usa `backend/.env.docker`.

Variáveis esperadas:

- `MYSQL_URL`
- `MINIO_ENDPOINT`
- `MINIO_PUBLIC_ENDPOINT`
- `MINIO_ACCESS_KEY`
- `MINIO_SECRET_KEY`
- `MINIO_BUCKET`
- `JWT_SECRET`
- `JWT_EXPIRE_MINUTES`
- `HF_API_TOKEN`

## Banco e storage

- O esquema do MySQL fica em `backend/schema.sql`.
- O MinIO é usado para armazenar os arquivos de imagem.
- O backend expõe os routers em `backend/app/main.py` e organiza a lógica por camada.

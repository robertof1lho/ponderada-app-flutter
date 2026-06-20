# AlterMe 🎭

App mobile que transforma sua selfie em um alter ego gerado por Inteligência Artificial. Você escolhe um universo — Anime, Medieval, Sci-Fi ou Político BR — e a IA redesenha seu rosto naquele estilo, preservando suas características físicas reais.

Desenvolvido como **Atividade Ponderada 4** do curso de Engenharia de Software do Inteli.

---

## Demonstração

<video src="https://github.com/robertof1lho/ponderada-app-flutter/raw/main/assets/demo.mp4" controls="controls" width="100%"></video>

> Caso o vídeo não carregue, [clique aqui para baixar](https://github.com/robertof1lho/ponderada-app-flutter/raw/main/assets/demo.mp4)

### Sobre os alter egos gerados...

Os resultados são gerados pelo **[FLUX.1-Kontext-Dev](https://huggingface.co/black-forest-labs/FLUX.1-Kontext-dev)** via [Pollinations.ai](https://pollinations.ai) — um modelo open source gratuito. Sendo completamente honesto as imagens geradas pelo modelo ficaram muito feias. Se tivesse usando um google nano banana, com certeza teria resultados 100x mais satisfatórios.

---

## Funcionalidades

- Cadastro e login com autenticação JWT
- Upload de selfie direto da galeria
- Seleção de universo temático (Anime, Medieval, Sci-Fi, Político BR)
- Geração de alter ego por IA preservando características físicas do rosto
- Visualização lado a lado: foto original vs. alter ego gerado
- Galeria pessoal com todas as criações
- Exclusão de alter egos
- Compartilhamento da imagem gerada

---

## Stack

### Frontend
| Tecnologia | Uso |
|---|---|
| Flutter | Framework mobile/web |
| BLoC | Gerenciamento de estado |
| go_router | Navegação |
| get_it | Injeção de dependência |
| Dio | Cliente HTTP |
| cached_network_image | Cache de imagens |

### Backend
| Tecnologia | Uso |
|---|---|
| FastAPI | API REST |
| aiomysql | Acesso async ao MySQL |
| boto3 | Storage S3-compatible (MinIO) |
| python-jose | JWT |
| bcrypt | Hash de senhas |
| Pollinations.ai | Geração de imagens (gratuito) |

### Infraestrutura
| Tecnologia | Uso |
|---|---|
| MySQL 8.0 | Banco de dados relacional |
| MinIO | Storage de imagens (S3-compatible) |
| Docker | Orquestração local |

---

## Arquitetura

```
ponderada-app-flutter/
├── lib/
│   ├── core/
│   │   ├── auth/          # Serviço de autenticação JWT
│   │   ├── di/            # Injeção de dependência (get_it)
│   │   ├── network/       # Cliente HTTP (Dio + interceptors)
│   │   └── router/        # Rotas (go_router)
│   └── features/
│       ├── auth/          # Login e cadastro
│       ├── alter_ego/     # Câmera, geração e resultado
│       └── feed/          # Galeria de criações
└── backend/
    ├── app/
    │   ├── handlers/      # Rotas HTTP (FastAPI)
    │   ├── domain/        # Casos de uso e contratos
    │   ├── repositories/  # Acesso ao MySQL
    │   └── services/      # Geração, prompt e visão
    ├── schema.sql          # DDL do banco
    └── tests/             # Testes unitários
```

---

## Como rodar

### Pré-requisitos

- [Flutter](https://flutter.dev/docs/get-started/install) instalado
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) em execução
- Python 3.11+

### 1. Subir a infraestrutura (MySQL + MinIO)

```powershell
docker-compose up -d mysql minio
```

Aguarde os containers ficarem saudáveis (uns 20 segundos).

### 2. Rodar o backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

A API sobe em `http://localhost:8080`. Documentação interativa: `http://localhost:8080/docs`

### 3. Rodar o frontend

```bash
flutter pub get
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8080
```

Para rodar em dispositivo físico, substitua o `API_BASE_URL` pelo IP da sua máquina na rede local.

### Testes do backend

```bash
cd backend
python -m pytest tests -q
```

---

## Variáveis de ambiente

O backend lê de `backend/.env`. Crie o arquivo com:

```env
MYSQL_URL=mysql+aiomysql://root:password@localhost:3306/alterme
MINIO_ENDPOINT=http://localhost:9000
MINIO_PUBLIC_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=alter-egos
JWT_SECRET=troque-por-uma-string-longa-e-aleatoria
JWT_EXPIRE_MINUTES=10080
HF_API_TOKEN=          # necessário apenas como fallback; Pollinations.ai não precisa de token
```

Para rodar com Docker, use `backend/.env.docker` com os hostnames internos (`mysql`, `minio`).

---

## Endpoints principais

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/auth/register` | Cadastro |
| `POST` | `/auth/login` | Login |
| `POST` | `/upload/selfie` | Upload da selfie |
| `POST` | `/alter-ego/generate` | Gerar alter ego |
| `DELETE` | `/alter-ego/{id}` | Excluir alter ego |
| `GET` | `/feed` | Listar criações do usuário |

---

## Fluxo de geração

```
Selfie → Upload MinIO → VisionService (extrai tom de pele e expressão)
       → PromptService (monta prompt com características físicas)
       → Pollinations.ai FLUX (gera imagem preservando o rosto)
       → Armazena no MinIO → Retorna URL pública
```

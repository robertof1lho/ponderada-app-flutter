# AlterMe — Design Spec

**Data:** 2026-06-12
**Atividade:** Ponderada 4 — Aplicação Mobile Funcional

---

## Problema

Usuários querem se ver de forma divertida e criativa em universos alternativos (anime, medieval, sci-fi, político BR). Não existe uma experiência mobile simples que combine selfie + IA + componente social para isso.

## Solução

**AlterMe** é um app Flutter onde o usuário tira uma selfie, escolhe um universo temático, e a IA gera sua versão naquele universo. Os alter egos são compartilhados numa comunidade, curtidos, e o grafo de estilos conecta usuários com gostos parecidos.

---

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Mobile | Flutter (Dart) |
| Auth + Storage | Supabase |
| Backend | FastAPI (Python) |
| Banco relacional | Supabase Postgres |
| Banco de grafo | Neo4j Aura Free |
| Análise de imagem | Google Vision API |
| Geração de imagem | Replicate API (SDXL) |
| Notificações | flutter_local_notifications |
| Compartilhamento | share_plus |
| Hardware | camera package |

---

## Requisitos atendidos (Ponderada 4)

| Requisito | Como atende |
|-----------|------------|
| Implementação mobile | Flutter |
| Múltiplas telas (>2) | 7 telas com navegação funcional |
| Backend funcional | FastAPI próprio |
| Banco de dados | Supabase Postgres + Neo4j Aura |
| API externa | Google Vision API + Replicate API |
| Sistema de notificações | flutter_local_notifications ao concluir geração |
| Compartilhamento | share_plus com imagem + texto no Result screen |
| Hardware do celular | Câmera (camera package) |

---

## Telas

| Tela | Rota | Descrição |
|------|------|-----------|
| LoginScreen | `/login` | Auth via Supabase (email/senha) |
| RegisterScreen | `/register` | Cadastro de novo usuário |
| HomeScreen | `/home` | Feed da comunidade, alter egos recentes |
| CameraScreen | `/camera` | Captura selfie com camera package |
| UniverseSelectorScreen | `/universe` | Escolha do universo temático |
| GeneratingScreen | `/generating` | Loading animado durante geração |
| ResultScreen | `/result` | Exibe alter ego gerado, salvar e compartilhar |
| ProfileScreen | `/profile` | Alter egos do usuário, usuários similares |

---

## Fluxo Principal

```
1. Usuário faz login (Supabase Auth)
2. HomeScreen exibe feed GET /feed
3. Usuário toca "Criar alter ego"
4. CameraScreen → tira selfie → upload Supabase Storage → selfieUrl
5. UniverseSelectorScreen → escolhe universo
6. GeneratingScreen → POST /alter-ego/generate { selfieUrl, universe, userId }
7. Backend processa (Vision → prompt → Replicate) → retorna imageUrl
8. Notificação local disparada: "Seu alter ego ficou pronto!"
9. ResultScreen → exibe imagem → botão compartilhar (share_plus)
10. Alter ego salvo no grafo (Neo4j) + feed atualizado
```

---

## Backend FastAPI — Estrutura

```
backend/
├── app/
│   ├── main.py                       # instancia FastAPI, registra routers
│   ├── core/
│   │   ├── config.py                 # settings via pydantic-settings (.env)
│   │   └── errors.py                 # exceções tipadas
│   ├── repositories/
│   │   ├── alter_ego_pg_repository.py    # Postgres: INSERT/SELECT alter_egos
│   │   ├── alter_ego_graph_repository.py # Neo4j: nós AlterEgo, arestas HAS_STYLE
│   │   ├── user_pg_repository.py         # Postgres: SELECT profiles
│   │   ├── user_graph_repository.py      # Neo4j: nós User
│   │   ├── feed_repository.py            # Neo4j IDs → Postgres dados (join no Python)
│   │   └── like_repository.py            # Postgres likes + Neo4j aresta LIKED
│   ├── services/
│   │   ├── vision_service.py         # Google Vision API
│   │   ├── generation_service.py     # Replicate API
│   │   └── prompt_service.py         # monta prompt a partir dos traços
│   ├── handlers/
│   │   ├── alter_ego_handler.py      # POST /alter-ego/generate, POST /alter-ego/{id}/like
│   │   ├── feed_handler.py           # GET /feed
│   │   └── profile_handler.py        # GET /profile/{user_id}/similar
│   └── models/
│       └── schemas.py                # Pydantic request/response models
├── tests/
├── .env
└── requirements.txt
```

### Responsabilidades por camada

| Camada | Faz | Não faz |
|--------|-----|---------|
| `handler` | valida request (Pydantic), delega, retorna response HTTP | nenhuma lógica de negócio |
| `service` | orquestra chamadas externas (Vision, Replicate) | não conhece Neo4j/Storage |
| `*_pg_repository` | persiste e lê dados estruturados no Postgres | não chama APIs externas, não conhece Neo4j |
| `*_graph_repository` | persiste e lê nós/arestas no Neo4j (apenas IDs) | não conhece Postgres, não chama APIs externas |
| `feed_repository` | une IDs do Neo4j com dados do Postgres | não chama APIs externas |

### Endpoints

```
POST /alter-ego/generate        body: { selfieUrl, universe, userId }
POST /alter-ego/{id}/like       body: { userId }
GET  /feed                      query: limit, offset
GET  /profile/{userId}/similar  query: limit
```

### Fluxo interno do handler `generate`

```
handler valida body
  → vision_service.extract_traits(selfie_url)
  → prompt_service.build_prompt(traits, universe)
  → generation_service.generate(prompt)
  → alter_ego_repository.save(user_id, image_url, universe, traits)
  → return { imageUrl }
```

---

## Flutter — Clean Architecture

```
lib/
├── core/
│   ├── errors/           # Failures, exceptions tipadas
│   ├── network/          # HTTP client wrapper (Dio)
│   └── utils/            # extensions, formatters
├── features/
│   ├── auth/
│   │   ├── data/         # SupabaseAuthDataSource, AuthRepositoryImpl
│   │   ├── domain/       # AuthRepository (interface), usecases
│   │   └── presentation/ # LoginScreen, RegisterScreen, AuthBloc
│   ├── alter_ego/
│   │   ├── data/         # GenerationRemoteDataSource, AlterEgoRepositoryImpl
│   │   ├── domain/       # AlterEgoRepository, GenerateAlterEgoUseCase
│   │   └── presentation/ # CameraScreen, UniverseSelector, GeneratingScreen, ResultScreen, Bloc
│   ├── feed/
│   │   ├── data/         # FeedRepositoryImpl
│   │   ├── domain/       # FeedRepository, GetCommunityFeedUseCase
│   │   └── presentation/ # HomeScreen, FeedBloc
│   └── profile/
│       ├── data/         # ProfileRepositoryImpl
│       ├── domain/       # ProfileRepository, GetSimilarUsersUseCase
│       └── presentation/ # ProfileScreen, ProfileBloc
└── main.dart
```

---

## Persistência — Polyglot

A aplicação usa dois bancos com responsabilidades distintas.

### Supabase Postgres — dados estruturados

Guarda todas as entidades ricas. Neo4j referencia apenas os IDs.

```sql
-- users (gerenciado pelo Supabase Auth, extendido com perfil)
CREATE TABLE profiles (
  id         UUID PRIMARY KEY REFERENCES auth.users(id),
  username   TEXT NOT NULL UNIQUE,
  avatar_url TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- alter egos com todos os metadados
CREATE TABLE alter_egos (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID NOT NULL REFERENCES profiles(id),
  image_url   TEXT NOT NULL,
  selfie_url  TEXT NOT NULL,
  universe    TEXT NOT NULL,
  traits      JSONB,           -- traços extraídos pela Vision API
  created_at  TIMESTAMPTZ DEFAULT now()
);

-- curtidas (também replicadas como aresta no Neo4j para queries de grafo)
CREATE TABLE likes (
  user_id      UUID REFERENCES profiles(id),
  alter_ego_id UUID REFERENCES alter_egos(id),
  created_at   TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (user_id, alter_ego_id)
);
```

### Neo4j Aura — grafo de relacionamentos

Guarda **apenas IDs** e arestas. Nenhum dado duplicado do Postgres.

#### Nós

```
(:User      { id })           ← UUID do Postgres profiles.id
(:AlterEgo  { id })           ← UUID do Postgres alter_egos.id
(:Style     { name })         ← traço extraído (ex: "anime", "smiling", "black_hair")
```

#### Arestas

```
(:User)-[:CREATED]->(:AlterEgo)
(:User)-[:LIKED]->(:AlterEgo)
(:AlterEgo)-[:HAS_STYLE]->(:Style)
```

#### Como os nós Style são criados

A Vision API retorna traços como `hairColor: "black"`, `expression: "smiling"`. Cada traço vira um nó `Style` (upsert) e uma aresta `HAS_STYLE` no alter ego. O universo escolhido também é adicionado como `Style`.

#### Queries principais

**IDs do feed da comunidade** (Neo4j retorna IDs → Postgres busca dados completos):
```cypher
MATCH (u:User)-[:CREATED]->(a:AlterEgo)
RETURN a.id AS alterEgoId, u.id AS userId
ORDER BY a.id DESC
LIMIT 20
```

**IDs de usuários com estilo similar:**
```cypher
MATCH (me:User {id: $userId})-[:CREATED]->(:AlterEgo)-[:HAS_STYLE]->(s:Style)
      <-[:HAS_STYLE]-(:AlterEgo)<-[:CREATED]-(other:User)
WHERE other.id <> $userId
RETURN other.id AS userId, count(s) AS shared
ORDER BY shared DESC
LIMIT 10
```

**IDs de alter egos mais curtidos num estilo:**
```cypher
MATCH (a:AlterEgo)-[:HAS_STYLE]->(:Style {name: $style})
OPTIONAL MATCH (:User)-[:LIKED]->(a)
RETURN a.id AS alterEgoId, count(*) AS likes
ORDER BY likes DESC
LIMIT 10
```

### Fluxo de escrita (consistência)

O repository executa writes em sequência e trata falhas explicitamente:

```
1. Postgres INSERT alter_egos → retorna UUID
2. Neo4j CREATE nó AlterEgo { id: UUID } + arestas
3. Se Neo4j falhar → log erro + retry (dados do Postgres permanecem íntegros)
```

O Postgres é a fonte de verdade dos dados. O Neo4j é a fonte de verdade dos relacionamentos.

### Fluxo de leitura (join no repository)

```
1. Neo4j retorna lista de UUIDs
2. Postgres SELECT WHERE id = ANY($ids)
3. repository combina e retorna objetos completos ao handler
```

---

## Notificação

- Disparada localmente via `flutter_local_notifications` quando o backend retorna a imagem gerada
- Tap na notificação navega direto para `ResultScreen` com o alter ego

## Compartilhamento

- `share_plus` na `ResultScreen`
- Compartilha imagem gerada + texto: `"Esse é meu alter ego [universo] no AlterMe 🤖"`

## Hardware

- `camera` package na `CameraScreen` para captura da selfie

---

## Tratamento de Erros

- Erros tipados no backend (`VisionError`, `GenerationError`, `Neo4jError`)
- Flutter: `Failure` classes no domain layer, mapeadas para mensagens amigáveis na UI
- Loading states gerenciados via Bloc em todas as telas assíncronas

---

## Autenticação

- Supabase Auth (email/senha)
- JWT do Supabase enviado no header `Authorization: Bearer <token>` para o FastAPI
- FastAPI valida o token via Supabase JWT secret

---

## Fora do Escopo

- Login social (Google/Apple)
- Edição ou exclusão de alter egos
- Chat entre usuários
- Pagamentos ou tiers premium

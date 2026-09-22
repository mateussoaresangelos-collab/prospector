# Prospector AI

Plataforma de prospecção comercial com frontend React + Vite e API FastAPI. O sistema busca empresas por cidade e categoria usando dados abertos do OpenStreetMap, enriquece os leads com website e email, persiste as pesquisas em SQLite e permite acompanhar o funil comercial.

## Arquitetura

- `frontend/`: aplicação React + TypeScript + Vite.
- `backend/`: API FastAPI e contratos HTTP.
- `prospector/modules/`: busca, enriquecimento, persistência e exportação compartilhados.
- `prospector/data/`: SQLite e CSV locais. Esses dados não devem ser versionados.
- `legacy/streamlit/`: interface histórica arquivada, fora do fluxo principal.

Fluxo principal:

```text
React -> FastAPI -> ProspectingService -> módulos Prospector -> SQLite/CSV
```

## Pré-requisitos

- Python 3.12 recomendado. A versão alvo está registrada em `.python-version`.
- Node.js 20 ou superior.
- Docker Desktop, opcional para execução containerizada.

O ambiente local existente pode estar em Python 3.14, mas o desenvolvimento e a execução do projeto devem usar Python 3.12 para manter compatibilidade previsível.

## Execução local

### Backend

Na raiz do projeto:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
python -m uvicorn app.main:app --app-dir backend --reload --port 8000
```

Verificação:

```text
GET http://localhost:8000/health
```

A resposta esperada é `{"status":"ok"}`.

### Frontend

Em outro terminal:

```powershell
cd frontend
npm install
npm run dev
```

Abra `http://localhost:5173`.

A URL da API é configurada por `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

Use `frontend/.env.example` como referência. O arquivo `.env` local não é versionado.

## Docker

Na raiz do projeto:

```powershell
docker compose up --build
```

Serviços:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Health check: `http://localhost:8000/health`

O backend recebe `PYTHONPATH=/app:/workspace` e `PROSPECTOR_DIR=/workspace/prospector`. O volume `./prospector:/workspace/prospector` mantém SQLite e CSV fora do container.

## API principal

- `GET /health`: verifica a API.
- `GET /categories`: lista as categorias oficiais disponíveis.
- `POST /search`: executa ou reutiliza uma pesquisa.
- `GET /search/history`: lista pesquisas salvas.
- `GET /leads`: retorna os leads da pesquisa mais recente.
- `PATCH /leads/{lead_id}`: atualiza status comercial, favorito e observações.

O campo `status` representa somente o funil comercial: `Novo`, `Contatado`, `Em negociação`, `Cliente` ou `Perdido`. Presença de website, email e Instagram é exposta separadamente por indicadores técnicos.

## Desenvolvimento

Antes de enviar alterações:

```powershell
git status
git add .
git commit -m "descreva a alteração"
git push
```

A branch principal é `main` e acompanha `origin/main`.

## Observações

Os serviços externos Nominatim, Overpass e websites dos leads podem limitar requisições ou ficar indisponíveis. O projeto ainda é uma base de produto; autenticação, rate limiting, fila de buscas e PostgreSQL são etapas futuras para produção multiusuário.

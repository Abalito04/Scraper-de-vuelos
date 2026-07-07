# FareRadar

FareRadar es una aplicación web para crear, monitorear y recibir alertas de posibles ofertas de vuelos.

El objetivo principal es permitir que un usuario configure búsquedas personalizadas de vuelos con múltiples orígenes, múltiples destinos, rangos de fechas, tipo de viaje, presupuesto máximo y reglas inteligentes de alerta.

El proyecto está pensado como una plataforma extensible, no como un script simple. Debe poder integrarse con distintos proveedores de vuelos mediante una capa de abstracción llamada `providers`.

Repositorio oficial:

```txt
https://github.com/Abalito04/Scraper-de-vuelos
```

---

## Problema que resuelve

Buscar vuelos baratos manualmente consume mucho tiempo.

El usuario suele tener varias posibilidades:

- Salir desde distintos aeropuertos.
- Viajar a distintos destinos.
- Tener fechas flexibles.
- Aceptar o rechazar escalas.
- Tener un precio máximo en mente.
- Querer enterarse rápido cuando aparece una buena oportunidad.

FareRadar automatiza ese proceso.

---

## Funcionalidades principales

### MVP

- Crear watchlists de vuelos.
- Elegir múltiples orígenes.
- Elegir múltiples destinos.
- Configurar fechas exactas o rangos de fechas.
- Definir duración mínima y máxima del viaje.
- Definir precio máximo.
- Definir cantidad máxima de escalas.
- Ejecutar búsqueda manual.
- Guardar ofertas encontradas.
- Guardar histórico de precios.
- Detectar posibles ofertas.
- Enviar alertas por Telegram.

### Futuro

- Integración real con Amadeus.
- Integración futura con Skyscanner, Duffel u otros providers.
- Búsqueda automática por scheduler.
- Dashboard con gráficos.
- Score de oportunidad.
- Alertas por email.
- Comparación entre aeropuertos alternativos.
- Soporte completo para multi-city.
- Deploy productivo.

---

## Tipos de viaje soportados

Desde el diseño, FareRadar debe soportar:

1. `ONE_WAY`
2. `ROUND_TRIP`
3. `MULTI_CITY`

---

## Stack técnico

### Backend

- Python
- FastAPI
- SQLAlchemy 2
- Alembic
- PostgreSQL
- Pydantic
- httpx
- pytest
- ruff o black

### Workers y scheduler

- Redis
- Celery o RQ
- Celery Beat o scheduler equivalente

### Frontend

- React
- Vite
- TypeScript
- Tailwind CSS
- Recharts

### Infraestructura

- Docker
- Docker Compose
- Variables de entorno
- Deploy objetivo inicial en Railway

### Notificaciones

- Telegram Bot API
- Email SMTP en fase posterior

---

## Arquitectura resumida

```mermaid
flowchart TD
    U[Usuario] --> FE[Frontend React]
    FE --> API[FastAPI Backend]

    API --> DB[(PostgreSQL)]
    API --> REDIS[(Redis)]

    S[Scheduler] --> Q[Job Queue]
    Q --> W[Worker]

    W --> PM[Provider Manager]
    PM --> MOCK[MockFlightProvider]
    PM --> AMA[AmadeusProvider Futuro]

    W --> RULES[Alert Rules Engine]
    RULES --> NOTIF[Notification Service]

    NOTIF --> TG[Telegram]
    NOTIF --> EMAIL[Email Futuro]

    API --> DB
    W --> DB
```

---

## Estructura del proyecto

```txt
fare-radar/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── providers/
│   │   ├── workers/
│   │   ├── notifications/
│   │   └── tests/
│   ├── alembic/
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├── docs/
│   ├── PROJECT_BRIEF.md
│   ├── ARCHITECTURE.md
│   ├── DATABASE_MODEL.md
│   ├── API_CONTRACT.md
│   ├── ROADMAP.md
│   └── PROMPTS_CODEX.md
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Entidades principales

- `User`
- `Watchlist`
- `WatchlistOrigin`
- `WatchlistDestination`
- `WatchlistDateWindow`
- `WatchlistSegment`
- `FlightOffer`
- `PriceSnapshot`
- `Alert`
- `ProviderLog`

---

## Regla de diseño más importante

La lógica de negocio nunca debe depender directamente de Amadeus, Skyscanner, Duffel ni de ningún proveedor externo.

Toda consulta de vuelos debe pasar por:

```txt
FlightSearchService
→ ProviderManager
→ FlightSearchProvider
→ Provider concreto
```

Y toda respuesta externa debe convertirse a un modelo normalizado:

```txt
NormalizedFlightOffer
```

---

## Variables de entorno esperadas

Ver también `.env.example`.

```env
APP_ENV=local
DATABASE_URL=postgresql+psycopg://fare_radar:fare_radar@postgres:5432/fare_radar
REDIS_URL=redis://redis:6379/0
FLIGHT_PROVIDER=mock

TELEGRAM_BOT_TOKEN=
SMTP_HOST=
SMTP_PORT=
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=

AMADEUS_CLIENT_ID=
AMADEUS_CLIENT_SECRET=
AMADEUS_ENV=test
```

---

## Cómo correr localmente

Copiar variables de entorno:

```bash
cp .env.example .env
```

Con Docker Compose:

```bash
docker compose up --build
```

Backend:

```txt
http://localhost:8000
```

Frontend:

```txt
http://localhost:5173
```

Healthcheck:

```txt
GET http://localhost:8000/health
```

Status:

```txt
GET http://localhost:8000/api/v1/status
```

Watchlists:

```txt
POST   http://localhost:8000/api/v1/watchlists
GET    http://localhost:8000/api/v1/watchlists
GET    http://localhost:8000/api/v1/watchlists/{watchlist_id}
PATCH  http://localhost:8000/api/v1/watchlists/{watchlist_id}
DELETE http://localhost:8000/api/v1/watchlists/{watchlist_id}
POST   http://localhost:8000/api/v1/watchlists/{watchlist_id}/run
GET    http://localhost:8000/api/v1/watchlists/{watchlist_id}/alerts
GET    http://localhost:8000/api/v1/alerts
```

### Backend sin Docker

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

Tests:

```bash
cd backend
pytest
```

Migraciones:

```bash
cd backend
alembic upgrade head
```

Lint:

```bash
cd backend
ruff check .
```

### Frontend sin Docker

```bash
cd frontend
npm install
npm run dev
```

---

## Deploy objetivo: Railway

FareRadar se va a preparar para desplegar en Railway.

La topología objetivo inicial es:

```txt
fare-radar-api        FastAPI
fare-radar-worker     Celery worker
fare-radar-scheduler  Celery Beat
fare-radar-frontend   React/Vite
PostgreSQL            Railway Postgres
Redis                 Railway Redis
```

Comandos esperados en Railway:

```txt
API:       uvicorn app.main:app --host 0.0.0.0 --port $PORT
Worker:    celery -A app.workers.celery_app worker --loglevel=info
Scheduler: celery -A app.workers.celery_app beat --loglevel=info
```

`docker-compose.yml` queda como entorno de desarrollo local. En producción, las variables reales deben configurarse desde Railway y nunca commitearse.

---

## Estado inicial del proyecto

El proyecto debe desarrollarse por fases.

Estado actual:

```txt
Fase 0 — Documentación y planificación: completa
Fase 1 — Bootstrap técnico del monorepo: completa
Fase 2 — Modelos de base de datos y migración inicial: completa
Fase 3 — CRUD de watchlists: completa
Fase 4 — Provider abstraction y MockFlightProvider: completa
Fase 5 — Search engine y guardado de snapshots: completa
Fase 6 — Motor de reglas de alerta: completa
Fase 7 — Notificaciones Telegram/Null: completa
```

Orden recomendado:

1. Documentación y arquitectura.
2. Setup del monorepo.
3. Backend base.
4. Base de datos.
5. CRUD de watchlists.
6. MockFlightProvider.
7. Búsqueda manual.
8. Histórico de precios.
9. Motor de alertas.
10. Telegram.
11. Scheduler automático.
12. Frontend.
13. Amadeus real.
14. Deploy.

---

## Objetivo personal

El proyecto nace como una herramienta para monitorear vuelos para un viaje futuro, por ejemplo Argentina a Europa, pero debe poder servir para cualquier destino y combinación de rutas.

---

## Objetivo como portfolio

FareRadar debe demostrar:

- Diseño de arquitectura.
- Backend profesional.
- Integración con APIs externas.
- Workers.
- Scheduler.
- Base de datos relacional.
- Histórico de datos.
- Motor de reglas.
- Notificaciones.
- Frontend con dashboard.
- Documentación técnica.
- Deploy.

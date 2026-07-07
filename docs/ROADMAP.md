# FareRadar — Roadmap

## Objetivo

Construir FareRadar por fases, evitando mezclar demasiadas cosas a la vez.

La prioridad es crear primero el motor real del sistema:

1. Watchlists.
2. Providers.
3. Búsquedas.
4. Histórico.
5. Alertas.

Después se construye el frontend y luego integraciones reales.

---

# Fase 0 — Planificación y documentación

## Objetivo

Documentar el proyecto antes de escribir código.

## Entregables

- `README.md`
- `docs/PROJECT_BRIEF.md`
- `docs/ARCHITECTURE.md`
- `docs/DATABASE_MODEL.md`
- `docs/API_CONTRACT.md`
- `docs/ROADMAP.md`
- `docs/PROMPTS_CODEX.md`
- `.env.example`

## Criterios de aceptación

- El proyecto tiene visión clara.
- La arquitectura está definida.
- El modelo de datos está documentado.
- Los endpoints iniciales están definidos.
- Las fases están separadas.
- Hay prompts listos para Codex.

---

# Fase 1 — Bootstrap técnico del monorepo

## Objetivo

Crear estructura inicial del proyecto.

## Entregables

```txt
backend/
frontend/
docs/
docker-compose.yml
.env.example
README.md
```

## Backend

- FastAPI.
- SQLAlchemy 2.
- Alembic.
- Pydantic.
- PostgreSQL.
- Redis preparado.
- pytest preparado.
- ruff o black.

## Frontend

- React.
- Vite.
- TypeScript.
- Tailwind CSS.

## Infra

- Docker Compose con:
  - backend
  - frontend
  - postgres
  - redis
- Preparación para Railway:
  - API usando `$PORT`.
  - Worker como proceso separado.
  - Scheduler como proceso separado.
  - Variables listas para Railway Postgres y Railway Redis.

## Endpoints mínimos

```txt
GET /health
GET /api/v1/status
```

## Criterios de aceptación

- `docker compose up --build` levanta servicios.
- Backend responde `/health`.
- Frontend muestra página inicial.
- `.env.example` existe.
- No hay credenciales hardcodeadas.

---

# Fase 2 — Modelos de base de datos y migraciones

## Objetivo

Implementar el modelo relacional inicial.

## Entidades

- User.
- Watchlist.
- WatchlistOrigin.
- WatchlistDestination.
- WatchlistDateWindow.
- WatchlistSegment.
- FlightOffer.
- PriceSnapshot.
- Alert.
- ProviderLog.

## Criterios de aceptación

- Migraciones de Alembic funcionan.
- Modelos SQLAlchemy están correctamente relacionados.
- Existen enums o constraints.
- Existen índices importantes.
- Hay tests básicos de creación.

---

# Fase 3 — CRUD de watchlists

## Objetivo

Permitir crear y administrar watchlists.

## Endpoints

```txt
POST /api/v1/watchlists
GET /api/v1/watchlists
GET /api/v1/watchlists/{id}
PATCH /api/v1/watchlists/{id}
DELETE /api/v1/watchlists/{id}
```

## Funcionalidades

- Crear watchlist one-way.
- Crear watchlist round-trip.
- Crear watchlist multi-city.
- Múltiples orígenes.
- Múltiples destinos.
- Ventanas de fecha.
- Segmentos multi-city.
- Activar/desactivar.

## Criterios de aceptación

- Tests de creación.
- Tests de validación.
- Tests de actualización.
- Tests de borrado lógico o desactivación.
- Validación de códigos IATA.
- Validación de fechas.

---

# Fase 4 — Provider abstraction y MockFlightProvider

## Objetivo

Crear capa de proveedores de vuelos.

## Componentes

- `FlightSearchProvider`
- `FlightSearchRequest`
- `NormalizedFlightOffer`
- `ProviderManager`
- `MockFlightProvider`

## Criterios de aceptación

- El provider mock genera ofertas realistas.
- Tests determinísticos.
- El resto del sistema no depende de providers reales.
- Se puede cambiar provider por variable de entorno.

---

# Fase 5 — Search engine y snapshots

## Objetivo

Ejecutar búsquedas y guardar histórico.

## Componentes

- `FlightSearchService`
- `WatchlistExpansionService`
- `PriceSnapshotService`
- `FlightOfferRepository`

## Funcionalidades

- Leer watchlist.
- Expandir combinaciones.
- Consultar provider.
- Guardar FlightOffer.
- Guardar PriceSnapshot.
- Guardar ProviderLog.
- Evitar duplicados obvios.

## Endpoint

```txt
POST /api/v1/watchlists/{id}/run
```

## Criterios de aceptación

- Se puede ejecutar búsqueda manual.
- Se guardan ofertas.
- Se guardan snapshots.
- Hay tests de expansión.
- Hay tests con MockFlightProvider.

---

# Fase 6 — Motor de reglas de alerta

## Objetivo

Detectar si una oferta merece alerta.

## Reglas mínimas

1. Precio menor o igual al máximo configurado.
2. Precio al menos X% debajo del promedio histórico.
3. Nuevo mínimo histórico.
4. No superar máximo de escalas.
5. No superar duración máxima razonable.
6. Cooldown anti-duplicados.

## Componentes

- `AlertRulesEngine`
- `AlertService`
- `AlertRepository`

## Endpoints

```txt
GET /api/v1/alerts
GET /api/v1/watchlists/{id}/alerts
```

## Criterios de aceptación

- Tests de cada regla.
- Tests de cooldown.
- Tests de mínimo histórico.
- Tests de promedio histórico.
- Alertas guardadas en DB.

---

# Fase 7 — Notificaciones por Telegram y email

## Objetivo

Enviar alertas al usuario.

## Primero Telegram

- `TELEGRAM_BOT_TOKEN`
- `telegram_chat_id`
- Mensaje formateado.

## Después email

- SMTP.
- Plantilla de email.

## Componentes

- `NotificationService`
- `TelegramNotificationProvider`
- `EmailNotificationProvider`

## Criterios de aceptación

- Tests con mocks.
- No se envían mensajes reales en tests.
- Manejo de errores.
- Mensaje incluye ruta, fechas, precio, escalas, duración y motivo.

---

# Fase 8 — Workers y scheduler

## Objetivo

Ejecutar watchlists automáticamente.

## Jobs

- `scan_active_watchlists`
- `run_watchlist_search`
- `evaluate_alerts_for_watchlist`
- `send_pending_alerts`

## Requisitos

- No ejecutar watchlists inactivas.
- Respetar `check_frequency_hours`.
- Evitar ejecuciones duplicadas.
- Registrar errores.
- Guardar logs.

## Criterios de aceptación

- Worker corre con Docker Compose.
- Scheduler dispara tareas.
- Se puede ejecutar tarea manualmente.
- Logs claros.

Nota: esta fase debe dejar los comandos listos para Railway aunque el deploy productivo se haga en una fase posterior.

---

# Fase 9 — Frontend dashboard

## Objetivo

Crear interfaz web.

## Pantallas

### Dashboard

- Watchlists activas.
- Últimas ofertas.
- Últimas alertas.
- Precio mínimo detectado.

### Watchlists

- Listado.
- Crear.
- Editar.
- Activar/desactivar.
- Ejecutar búsqueda manual.

### Detalle de watchlist

- Configuración.
- Ofertas.
- Histórico de precios.
- Alertas.

### Settings

- Telegram.
- Email.
- Moneda preferida.

## Criterios de aceptación

- UI limpia.
- Formularios validados.
- Loading states.
- Error states.
- Empty states.
- Tabla de ofertas.
- Tabla de alertas.
- Gráfico histórico con Recharts.

---

# Fase 10 — AmadeusProvider real

## Objetivo

Integrar primer proveedor real.

## Requisitos

- `AMADEUS_CLIENT_ID`
- `AMADEUS_CLIENT_SECRET`
- `AMADEUS_ENV`
- Manejo de OAuth/token.
- Rate limit básico.
- Manejo de errores.
- Normalización a `NormalizedFlightOffer`.

## Primero

- One-way.
- Round-trip.

## Después

- Multi-city.
- Fechas flexibles.
- Múltiples destinos.

## Criterios de aceptación

- Tests con respuestas mockeadas.
- No llamar API real en tests.
- Documentación de credenciales.
- Selección por `FLIGHT_PROVIDER=mock|amadeus`.

---

# Fase 11 — Deploy en Railway

## Objetivo

Preparar producción.

## Entregables

- Dockerfiles optimizados.
- Variables documentadas.
- Healthchecks.
- Logging.
- Migraciones.
- Worker.
- Scheduler.
- README de deploy.

## Plataforma objetivo

- Railway.

## Servicios Railway esperados

```txt
fare-radar-api
fare-radar-worker
fare-radar-scheduler
fare-radar-frontend
PostgreSQL
Redis
```

## Comandos esperados

```txt
API:       uvicorn app.main:app --host 0.0.0.0 --port $PORT
Worker:    celery -A app.workers.celery_app worker --loglevel=info
Scheduler: celery -A app.workers.celery_app beat --loglevel=info
```

## Criterios de aceptación

- Backend corre en producción.
- Worker corre en producción.
- Scheduler corre en producción.
- Migraciones pueden ejecutarse.
- No hay secretos en el repo.
- Variables de Railway documentadas.

---

# Fase 12 — Mejoras inteligentes

## Objetivo

Hacer que el sistema se destaque.

## Funcionalidades

- Score de oportunidad.
- Comparación entre aeropuertos alternativos.
- Detección de rutas con mejor relación precio/duración.
- Reporte semanal.
- Reglas personalizadas.
- Monitoreo de proveedores.
- Dashboard avanzado.

## Score sugerido

```txt
offer_score =
  precio_score * 0.50 +
  duracion_score * 0.20 +
  escalas_score * 0.15 +
  historico_score * 0.15
```

---

# Prioridad real de implementación

Orden recomendado:

```txt
1. Docs y arquitectura
2. Backend base
3. Base de datos
4. CRUD watchlists
5. Mock provider
6. Búsqueda manual
7. Histórico
8. Alertas
9. Telegram
10. Scheduler
11. Frontend
12. Amadeus
13. Deploy
```

---

# Qué no hacer al principio

No arrancar por:

- UI compleja.
- Machine learning.
- WhatsApp.
- Scraping.
- Login avanzado.
- Multi-tenant.
- Pagos.
- Muchos providers reales al mismo tiempo.

Primero debe funcionar el núcleo.

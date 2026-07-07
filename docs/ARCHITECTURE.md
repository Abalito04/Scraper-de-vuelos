# FareRadar — Architecture

## Objetivo de arquitectura

FareRadar debe ser una aplicación web extensible para monitorear vuelos y generar alertas inteligentes.

La arquitectura debe permitir:

- Agregar nuevos proveedores de vuelos sin reescribir la lógica principal.
- Ejecutar búsquedas manuales y automáticas.
- Guardar histórico de precios.
- Evaluar reglas de alerta.
- Enviar notificaciones por distintos canales.
- Escalar de un MVP simple a una plataforma más completa.

---

## Principios de diseño

1. Separar lógica de negocio de infraestructura.
2. No acoplar el dominio a APIs externas.
3. Usar providers intercambiables.
4. Guardar respuestas normalizadas y payload crudo.
5. Tener tests desde fases tempranas.
6. Usar configuración por variables de entorno.
7. Evitar scraping en el MVP.
8. Diseñar para múltiples orígenes y destinos.
9. Soportar one-way, round-trip y multi-city desde el modelo.
10. Evitar alertas duplicadas.

---

## Diagrama de componentes

```mermaid
flowchart TD
    U[Usuario] --> FE[Frontend React + Vite]
    FE --> API[FastAPI Backend]

    API --> AUTH[User/Profile Service]
    API --> WLS[Watchlist Service]
    API --> FSS[Flight Search Service]
    API --> ALS[Alert Service]

    API --> DB[(PostgreSQL)]
    API --> REDIS[(Redis)]

    S[Scheduler] --> Q[Job Queue]
    Q --> WORKER[Worker]

    WORKER --> WLS
    WORKER --> FSS
    WORKER --> ALS

    FSS --> EXP[Watchlist Expansion Service]
    FSS --> PM[Provider Manager]

    PM --> MOCK[MockFlightProvider]
    PM --> AMA[AmadeusProvider]
    PM --> SKY[SkyscannerProvider Futuro]
    PM --> DUFF[DuffelProvider Futuro]

    FSS --> DB
    ALS --> RULES[Alert Rules Engine]
    RULES --> DB

    ALS --> NOTIF[Notification Service]
    NOTIF --> TG[Telegram Provider]
    NOTIF --> EMAIL[Email Provider]

    WORKER --> DB
```

### Explicación

El backend expone la API REST. Las búsquedas pueden ejecutarse manualmente desde el frontend o automáticamente desde workers. Los providers externos están aislados detrás de `ProviderManager`.

---

## Flujo de búsqueda manual

```mermaid
sequenceDiagram
    participant User as Usuario
    participant FE as Frontend
    participant API as FastAPI
    participant FSS as FlightSearchService
    participant WLS as WatchlistService
    participant EXP as ExpansionService
    participant PM as ProviderManager
    participant Provider as FlightProvider
    participant DB as PostgreSQL
    participant Rules as AlertRulesEngine
    participant Notif as NotificationService

    User->>FE: Ejecutar búsqueda manual
    FE->>API: POST /api/v1/watchlists/{id}/run
    API->>FSS: run_manual_search(watchlist_id)
    FSS->>WLS: Obtener watchlist
    WLS->>DB: Leer configuración
    DB-->>WLS: Watchlist
    WLS-->>FSS: Watchlist
    FSS->>EXP: Expandir combinaciones
    EXP-->>FSS: FlightSearchRequests
    FSS->>PM: Ejecutar búsquedas
    PM->>Provider: search(request)
    Provider-->>PM: NormalizedFlightOffer[]
    PM-->>FSS: Ofertas normalizadas
    FSS->>DB: Guardar FlightOffer
    FSS->>DB: Guardar PriceSnapshot
    FSS->>Rules: Evaluar ofertas
    Rules->>DB: Consultar histórico y alertas previas
    Rules-->>FSS: Alertas candidatas
    FSS->>DB: Guardar Alert
    FSS->>Notif: Enviar si corresponde
    Notif-->>User: Telegram / Email
    FSS-->>API: Resultado de búsqueda
    API-->>FE: Resultado de búsqueda
```

El router solo valida la entrada HTTP y delega el caso de uso. La orquestación queda en `FlightSearchService`.

---

## Deploy en Railway

Railway es el objetivo inicial de despliegue.

Servicios esperados:

```txt
fare-radar-api
fare-radar-worker
fare-radar-scheduler
fare-radar-frontend
PostgreSQL
Redis
```

Comandos esperados:

```txt
API:       uvicorn app.main:app --host 0.0.0.0 --port $PORT
Worker:    celery -A app.workers.celery_app worker --loglevel=info
Scheduler: celery -A app.workers.celery_app beat --loglevel=info
```

Notas:

- La API debe respetar `$PORT`.
- PostgreSQL y Redis deben venir de variables de entorno de Railway.
- Las migraciones de Alembic deben tener un comando documentado y ejecutarse de forma controlada.
- `docker-compose.yml` se mantiene solo para desarrollo local.

---

## Flujo de búsqueda automática

```mermaid
sequenceDiagram
    participant Scheduler
    participant Queue as Job Queue
    participant Worker
    participant DB as PostgreSQL
    participant PM as ProviderManager
    participant Provider as FlightProvider
    participant Rules as AlertRulesEngine
    participant Notif as NotificationService
    participant User as Usuario

    Scheduler->>Queue: scan_active_watchlists
    Queue->>Worker: Ejecutar job
    Worker->>DB: Obtener watchlists activas
    DB-->>Worker: Watchlists
    Worker->>DB: Filtrar por frecuencia
    Worker->>PM: Consultar provider
    PM->>Provider: search(request)
    Provider-->>PM: Ofertas normalizadas
    PM-->>Worker: Resultados
    Worker->>DB: Guardar ofertas y snapshots
    Worker->>Rules: Evaluar reglas
    Rules->>DB: Consultar histórico
    Rules-->>Worker: Alertas
    Worker->>DB: Guardar alertas
    Worker->>Notif: Enviar alertas pendientes
    Notif-->>User: Telegram / Email
```

---

## Diagrama entidad-relación conceptual

```mermaid
erDiagram
    USER ||--o{ WATCHLIST : owns
    WATCHLIST ||--o{ WATCHLIST_ORIGIN : has
    WATCHLIST ||--o{ WATCHLIST_DESTINATION : has
    WATCHLIST ||--o{ WATCHLIST_DATE_WINDOW : has
    WATCHLIST ||--o{ WATCHLIST_SEGMENT : has
    WATCHLIST ||--o{ FLIGHT_OFFER : produces
    WATCHLIST ||--o{ PRICE_SNAPSHOT : tracks
    WATCHLIST ||--o{ ALERT : generates

    FLIGHT_OFFER ||--o{ PRICE_SNAPSHOT : has
    FLIGHT_OFFER ||--o{ ALERT : triggers

    USER {
        int id
        string name
        string email
        string telegram_chat_id
        datetime created_at
    }

    WATCHLIST {
        int id
        int user_id
        string name
        string trip_type
        string currency
        decimal max_price
        int max_stops
        string cabin_class
        int adults
        bool active
        int check_frequency_hours
        datetime created_at
        datetime updated_at
    }

    WATCHLIST_ORIGIN {
        int id
        int watchlist_id
        string origin_code
    }

    WATCHLIST_DESTINATION {
        int id
        int watchlist_id
        string destination_code
    }

    WATCHLIST_DATE_WINDOW {
        int id
        int watchlist_id
        date departure_date_from
        date departure_date_to
        date return_date_from
        date return_date_to
        int min_trip_days
        int max_trip_days
    }

    WATCHLIST_SEGMENT {
        int id
        int watchlist_id
        int segment_order
        string origin_code
        string destination_code
        date date_from
        date date_to
    }

    FLIGHT_OFFER {
        int id
        int watchlist_id
        string provider
        string origin_code
        string destination_code
        string trip_type
        date departure_date
        date return_date
        decimal total_price
        string currency
        string airline_codes
        int stops
        int duration_minutes
        string deep_link
        json raw_payload
        datetime found_at
    }

    PRICE_SNAPSHOT {
        int id
        int watchlist_id
        int flight_offer_id
        decimal price
        string currency
        datetime checked_at
    }

    ALERT {
        int id
        int watchlist_id
        int flight_offer_id
        string alert_type
        string status
        string message
        string sent_to
        datetime sent_at
    }
```

---

## Estados de una alerta

```mermaid
stateDiagram-v2
    [*] --> candidate
    candidate --> skipped_rule_mismatch
    candidate --> skipped_duplicate
    candidate --> pending
    pending --> sent
    pending --> failed
    failed --> pending
    sent --> [*]
    skipped_rule_mismatch --> [*]
    skipped_duplicate --> [*]
```

### Estados

- `candidate`: oferta que podría generar alerta.
- `pending`: alerta aprobada por reglas y pendiente de envío.
- `sent`: alerta enviada correctamente.
- `failed`: falló el envío.
- `skipped_duplicate`: ignorada por cooldown o duplicado.
- `skipped_rule_mismatch`: ignorada porque no cumple reglas.

---

## Capas del backend

```txt
app/
├── api/              # Routers FastAPI
├── core/             # Configuración, settings, seguridad
├── db/               # Session, base, conexión
├── models/           # Modelos SQLAlchemy
├── schemas/          # Schemas Pydantic
├── repositories/     # Acceso a datos
├── services/         # Lógica de negocio
├── providers/        # Providers de vuelos
├── notifications/    # Notificaciones
├── workers/          # Jobs y scheduler
└── tests/            # Tests
```

---

## Provider abstraction

Todos los proveedores deben implementar una interfaz común:

```txt
FlightSearchProvider
```

Método esperado:

```txt
search(request: FlightSearchRequest) -> list[NormalizedFlightOffer]
```

---

## Providers

### MockFlightProvider

Primer provider obligatorio.

Sirve para:

- Desarrollar sin APIs externas.
- Testear reglas.
- Generar datos falsos realistas.
- Construir frontend sin depender de Amadeus.

### AmadeusProvider

Primer provider real.

Debe implementarse después de tener funcionando:

- Watchlists.
- Mock provider.
- Search engine.
- Motor de alertas.
- Snapshots.
- Tests.

### Otros providers futuros

- Skyscanner.
- Duffel.
- Kiwi/Tequila.
- APIs de agencias.
- Feeds internos.

---

## Servicios principales

### WatchlistService

Responsabilidades:

- Crear watchlists.
- Editar watchlists.
- Activar/desactivar.
- Validar configuración.
- Obtener watchlists activas.

### WatchlistExpansionService

Responsabilidades:

- Convertir una watchlist en múltiples requests de búsqueda.
- Expandir orígenes contra destinos.
- Expandir fechas.
- Expandir duraciones de viaje.
- Crear requests multi-city.

### FlightSearchService

Responsabilidades:

- Ejecutar una búsqueda.
- Llamar al provider.
- Normalizar ofertas.
- Guardar resultados.
- Registrar logs.

### AlertRulesEngine

Responsabilidades:

- Evaluar si una oferta merece alerta.
- Comparar contra precio máximo.
- Comparar contra promedio histórico.
- Detectar mínimo histórico.
- Evitar duplicados.
- Aplicar cooldown.

### NotificationService

Responsabilidades:

- Formatear mensajes.
- Enviar Telegram.
- Enviar email.
- Registrar errores.

---

## Decisiones técnicas

### FastAPI en lugar de Flask

FastAPI es mejor para este proyecto porque:

- Tiene validación fuerte con Pydantic.
- Genera documentación automática.
- Encaja bien con una API REST separada del frontend.
- Tiene mejor experiencia para schemas y typing.

### PostgreSQL

Se elige PostgreSQL porque:

- Es robusto.
- Maneja relaciones complejas.
- Permite JSON para raw payloads.
- Es ideal para histórico de precios.

### Redis + workers

Se necesitan workers porque:

- Las búsquedas pueden tardar.
- Las APIs externas tienen latencia.
- El scheduler debe correr en segundo plano.
- Las alertas no deben bloquear requests HTTP.

### ProviderManager

Se usa para evitar acoplamiento.

El sistema no debe saber si la búsqueda viene de Mock, Amadeus, Skyscanner o Duffel.

---

## Riesgos de arquitectura

### Explosión de combinaciones

Múltiples orígenes, destinos, fechas y duraciones pueden generar demasiadas consultas.

Mitigación:

- Limitar máximo de combinaciones por ejecución.
- Agregar validaciones.
- Dividir trabajos.
- Priorizar fechas.
- Usar scheduler.

### Costo de APIs

Las APIs reales pueden tener límites o costos.

Mitigación:

- Mock provider.
- Rate limit.
- Caché.
- Control de frecuencia.

### Datos inconsistentes

Cada provider devuelve campos distintos.

Mitigación:

- NormalizedFlightOffer.
- raw_payload.
- campos opcionales.
- tests por provider.

---

## Regla de oro

Nunca llamar APIs externas directamente desde routers.

Correcto:

```txt
Router
→ Service
→ ProviderManager
→ Provider
```

Incorrecto:

```txt
Router
→ Amadeus API
```

# FareRadar — .env.example

Este archivo documenta las variables de entorno recomendadas.

Cuando se cree el proyecto real, este contenido debería convertirse en un archivo llamado:

```txt
.env.example
```

---

```env
# App
APP_NAME=FareRadar
APP_ENV=local
APP_DEBUG=true
APP_VERSION=0.1.0

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
API_PREFIX=/api/v1

# Database
POSTGRES_DB=fare_radar
POSTGRES_USER=fare_radar
POSTGRES_PASSWORD=fare_radar
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg://fare_radar:fare_radar@postgres:5432/fare_radar

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_URL=redis://redis:6379/0

# Flight provider
# Valid values: mock, amadeus
FLIGHT_PROVIDER=mock

# Mock provider
MOCK_PROVIDER_SEED=12345
MOCK_PROVIDER_MIN_PRICE=500
MOCK_PROVIDER_MAX_PRICE=1800

# Telegram
NOTIFICATION_PROVIDER=null
TELEGRAM_BOT_TOKEN=
TELEGRAM_DEFAULT_CHAT_ID=

# Email SMTP
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=
SMTP_USE_TLS=true

# Amadeus
AMADEUS_CLIENT_ID=
AMADEUS_CLIENT_SECRET=
AMADEUS_ENV=test

# Scheduler
DEFAULT_CHECK_FREQUENCY_HOURS=12
MAX_COMBINATIONS_PER_WATCHLIST=200
ALERT_COOLDOWN_HOURS=24

# Frontend
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## Notas

- Nunca commitear `.env` real.
- Sí commitear `.env.example`.
- Las claves reales deben configurarse en el entorno local o plataforma de deploy.
- En tests no deben usarse credenciales reales.
- En Railway, `DATABASE_URL`, `REDIS_URL` y `PORT` deben venir del entorno de la plataforma.
- La API debe escuchar en `0.0.0.0` y usar `$PORT`.
- Los procesos de worker y scheduler deben usar las mismas variables de entorno que la API, pero no exponer puertos públicos.

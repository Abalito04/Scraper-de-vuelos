# FareRadar — API Contract

## Base URL

```txt
/api/v1
```

---

## Formato de errores

Todos los errores deberían tener este formato:

```json
{
  "detail": "Descripción clara del error",
  "code": "ERROR_CODE",
  "fields": {
    "field_name": "Detalle opcional"
  }
}
```

---

# Health

## GET /health

Verifica que el backend esté vivo.

### Response 200

```json
{
  "status": "ok"
}
```

---

## GET /api/v1/status

Devuelve estado general de la API.

### Response 200

```json
{
  "app": "FareRadar",
  "version": "0.1.0",
  "environment": "local",
  "provider": "mock"
}
```

---

# Watchlists

## POST /api/v1/watchlists

Crea una watchlist.

### Request — ROUND_TRIP

```json
{
  "name": "Europa 2027",
  "trip_type": "ROUND_TRIP",
  "origins": ["EZE", "AEP", "MVD"],
  "destinations": ["DUB", "MAD", "BCN"],
  "date_windows": [
    {
      "departure_date_from": "2027-03-01",
      "departure_date_to": "2027-06-30",
      "return_date_from": null,
      "return_date_to": null,
      "min_trip_days": 14,
      "max_trip_days": 35
    }
  ],
  "currency": "USD",
  "max_price": 900,
  "max_stops": 2,
  "max_duration_minutes": 2400,
  "cabin_class": "ECONOMY",
  "adults": 1,
  "active": true,
  "check_frequency_hours": 12,
  "alert_rules": {
    "below_max_price": true,
    "below_historical_average_percent": 20,
    "new_historical_minimum": true,
    "cooldown_hours": 24
  }
}
```

### Request — ONE_WAY

```json
{
  "name": "Solo ida a Dublín",
  "trip_type": "ONE_WAY",
  "origins": ["EZE"],
  "destinations": ["DUB"],
  "date_windows": [
    {
      "departure_date_from": "2027-05-01",
      "departure_date_to": "2027-05-31",
      "return_date_from": null,
      "return_date_to": null,
      "min_trip_days": null,
      "max_trip_days": null
    }
  ],
  "currency": "USD",
  "max_price": 700,
  "max_stops": 2,
  "cabin_class": "ECONOMY",
  "adults": 1,
  "active": true,
  "check_frequency_hours": 12
}
```

### Request — MULTI_CITY

```json
{
  "name": "Europa multi-city",
  "trip_type": "MULTI_CITY",
  "segments": [
    {
      "origin_code": "EZE",
      "destination_code": "MAD",
      "date_from": "2027-04-01",
      "date_to": "2027-04-10"
    },
    {
      "origin_code": "MAD",
      "destination_code": "DUB",
      "date_from": "2027-04-15",
      "date_to": "2027-04-20"
    },
    {
      "origin_code": "DUB",
      "destination_code": "EZE",
      "date_from": "2027-05-01",
      "date_to": "2027-05-10"
    }
  ],
  "currency": "USD",
  "max_price": 1200,
  "max_stops": 2,
  "cabin_class": "ECONOMY",
  "adults": 1,
  "active": true,
  "check_frequency_hours": 12
}
```

### Response 201

```json
{
  "id": 1,
  "name": "Europa 2027",
  "trip_type": "ROUND_TRIP",
  "active": true,
  "created_at": "2026-07-07T12:00:00Z"
}
```

### Validaciones

- `name` requerido.
- `trip_type` debe ser `ONE_WAY`, `ROUND_TRIP` o `MULTI_CITY`.
- `origins` y `destinations` solo aplican a `ONE_WAY` y `ROUND_TRIP`.
- `segments` solo aplica a `MULTI_CITY`.
- Códigos IATA deben tener 3 letras.
- `max_price` debe ser mayor a 0.
- `adults` debe ser mayor o igual a 1.
- `check_frequency_hours` debe ser mayor o igual a 1.
- `min_trip_days` no puede ser mayor que `max_trip_days`.
- Multi-city debe tener al menos 2 segmentos.

---

## GET /api/v1/watchlists

Lista watchlists.

### Query params

```txt
active=true|false
trip_type=ONE_WAY|ROUND_TRIP|MULTI_CITY
limit=20
offset=0
```

### Response 200

```json
{
  "items": [
    {
      "id": 1,
      "name": "Europa 2027",
      "trip_type": "ROUND_TRIP",
      "active": true,
      "currency": "USD",
      "max_price": 900,
      "last_checked_at": null
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

---

## GET /api/v1/watchlists/{watchlist_id}

Obtiene una watchlist completa.

### Response 200

```json
{
  "id": 1,
  "name": "Europa 2027",
  "trip_type": "ROUND_TRIP",
  "origins": ["EZE", "AEP", "MVD"],
  "destinations": ["DUB", "MAD", "BCN"],
  "date_windows": [
    {
      "departure_date_from": "2027-03-01",
      "departure_date_to": "2027-06-30",
      "min_trip_days": 14,
      "max_trip_days": 35
    }
  ],
  "currency": "USD",
  "max_price": 900,
  "max_stops": 2,
  "active": true,
  "check_frequency_hours": 12,
  "created_at": "2026-07-07T12:00:00Z",
  "updated_at": "2026-07-07T12:00:00Z"
}
```

---

## PATCH /api/v1/watchlists/{watchlist_id}

Actualiza una watchlist.

### Request

```json
{
  "name": "Europa primavera 2027",
  "max_price": 850,
  "active": true,
  "check_frequency_hours": 6
}
```

### Response 200

```json
{
  "id": 1,
  "name": "Europa primavera 2027",
  "max_price": 850,
  "active": true,
  "updated_at": "2026-07-07T13:00:00Z"
}
```

---

## DELETE /api/v1/watchlists/{watchlist_id}

Desactiva o elimina una watchlist.

Recomendación para MVP:

- Hacer soft delete o marcar `active = false`.

### Response 204

Sin body.

---

# Ejecución de búsqueda

## POST /api/v1/watchlists/{watchlist_id}/run

Ejecuta manualmente una búsqueda.

### Response 200

```json
{
  "watchlist_id": 1,
  "provider": "MOCK",
  "offers_found": 12,
  "snapshots_created": 12,
  "alerts_created": 2,
  "alerts_sent": 1
}
```

### Errores posibles

```txt
404 WATCHLIST_NOT_FOUND
400 WATCHLIST_INACTIVE
400 TOO_MANY_COMBINATIONS
502 PROVIDER_ERROR
```

---

# Flight offers

## GET /api/v1/watchlists/{watchlist_id}/offers

Lista ofertas encontradas para una watchlist.

### Query params

```txt
limit=20
offset=0
sort=price_asc|price_desc|found_at_desc
```

### Response 200

```json
{
  "items": [
    {
      "id": 101,
      "provider": "MOCK",
      "origin_code": "EZE",
      "destination_code": "DUB",
      "trip_type": "ROUND_TRIP",
      "departure_date": "2027-05-10",
      "return_date": "2027-05-30",
      "total_price": 820,
      "currency": "USD",
      "airline_codes": ["IB", "EI"],
      "stops": 1,
      "duration_minutes": 1060,
      "deep_link": "https://example.com/mock-flight",
      "found_at": "2026-07-07T14:00:00Z"
    }
  ],
  "total": 1
}
```

---

# Price snapshots

## GET /api/v1/watchlists/{watchlist_id}/price-history

Devuelve histórico de precios para gráficos.

### Response 200

```json
{
  "watchlist_id": 1,
  "currency": "USD",
  "items": [
    {
      "checked_at": "2026-07-07T14:00:00Z",
      "min_price": 820,
      "avg_price": 930,
      "max_price": 1200
    }
  ]
}
```

---

# Alerts

## GET /api/v1/alerts

Lista alertas globales.

### Query params

```txt
status=PENDING|SENT|FAILED
limit=20
offset=0
```

### Response 200

```json
{
  "items": [
    {
      "id": 501,
      "watchlist_id": 1,
      "flight_offer_id": 101,
      "alert_type": "BELOW_MAX_PRICE",
      "status": "SENT",
      "message": "Posible oferta detectada...",
      "sent_channel": "TELEGRAM",
      "sent_at": "2026-07-07T14:01:00Z"
    }
  ],
  "total": 1
}
```

---

## GET /api/v1/watchlists/{watchlist_id}/alerts

Lista alertas de una watchlist.

### Response 200

```json
{
  "items": [
    {
      "id": 501,
      "alert_type": "BELOW_MAX_PRICE",
      "status": "SENT",
      "sent_at": "2026-07-07T14:01:00Z"
    }
  ]
}
```

---

# Settings

## GET /api/v1/settings

Devuelve configuración actual del usuario o app.

### Response 200

```json
{
  "preferred_currency": "USD",
  "telegram_configured": true,
  "email_configured": false,
  "flight_provider": "MOCK"
}
```

---

## PATCH /api/v1/settings

Actualiza configuración.

### Request

```json
{
  "telegram_chat_id": "123456789",
  "preferred_currency": "USD"
}
```

### Response 200

```json
{
  "preferred_currency": "USD",
  "telegram_configured": true
}
```

---

# Códigos de error sugeridos

```txt
VALIDATION_ERROR
WATCHLIST_NOT_FOUND
WATCHLIST_INACTIVE
TOO_MANY_COMBINATIONS
PROVIDER_ERROR
PROVIDER_UNAVAILABLE
DUPLICATE_ALERT
NOTIFICATION_ERROR
DATABASE_ERROR
UNAUTHORIZED
FORBIDDEN
```

---

# Criterios generales de API

- Usar JSON.
- Usar códigos HTTP correctos.
- Validar con Pydantic.
- No exponer secretos.
- No devolver raw_payload por defecto salvo endpoint debug.
- Paginar listados.
- Manejar errores de providers con mensajes claros.
- Mantener endpoints versionados bajo `/api/v1`.

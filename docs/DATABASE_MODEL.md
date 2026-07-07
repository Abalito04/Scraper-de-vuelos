# FareRadar — Database Model

## Objetivo

El modelo de datos debe permitir:

- Usuarios.
- Watchlists flexibles.
- Múltiples orígenes.
- Múltiples destinos.
- Rangos de fechas.
- Viajes multi-city.
- Ofertas normalizadas.
- Histórico de precios.
- Alertas.
- Logs de proveedores.

---

## Convenciones

- Usar `created_at` y `updated_at` donde corresponda.
- Usar timezone UTC en timestamps.
- Usar `numeric` para precios.
- Usar `jsonb` para payloads crudos.
- Indexar campos usados para filtros frecuentes.
- No borrar datos históricos salvo decisión explícita.

---

## Enums recomendados

### trip_type

```txt
ONE_WAY
ROUND_TRIP
MULTI_CITY
```

### cabin_class

```txt
ECONOMY
PREMIUM_ECONOMY
BUSINESS
FIRST
```

### provider

```txt
MOCK
AMADEUS
SKYSCANNER
DUFFEL
```

### alert_type

```txt
BELOW_MAX_PRICE
BELOW_HISTORICAL_AVERAGE
NEW_HISTORICAL_MINIMUM
CUSTOM_RULE
```

### alert_status

```txt
CANDIDATE
PENDING
SENT
FAILED
SKIPPED_DUPLICATE
SKIPPED_RULE_MISMATCH
```

---

# Tablas

## users

Representa un usuario de la aplicación.

Campos:

```txt
id
name
email
telegram_chat_id
preferred_currency
created_at
updated_at
```

Notas:

- En el MVP puede existir un usuario único o sistema sin autenticación completa.
- `telegram_chat_id` se usa para notificaciones.
- `preferred_currency` puede ser `USD` por defecto.

Índices:

```txt
email unique
```

---

## watchlists

Representa una búsqueda configurada por el usuario.

Campos:

```txt
id
user_id
name
trip_type
currency
max_price
max_stops
max_duration_minutes
cabin_class
adults
active
check_frequency_hours
alert_below_max_price
alert_below_average_percent
alert_on_new_minimum
alert_cooldown_hours
last_checked_at
created_at
updated_at
```

Relaciones:

```txt
users 1:N watchlists
watchlists 1:N watchlist_origins
watchlists 1:N watchlist_destinations
watchlists 1:N watchlist_date_windows
watchlists 1:N watchlist_segments
watchlists 1:N flight_offers
watchlists 1:N price_snapshots
watchlists 1:N alerts
```

Validaciones:

- `name` requerido.
- `trip_type` requerido.
- `max_price` debe ser mayor a 0 si se define.
- `max_stops` debe ser mayor o igual a 0.
- `adults` debe ser mayor o igual a 1.
- `check_frequency_hours` debe ser mayor o igual a 1.
- Si `trip_type = MULTI_CITY`, debe tener al menos 2 segmentos.
- Si `trip_type != MULTI_CITY`, debe tener origins, destinations y date windows.

Índices:

```txt
user_id
active
trip_type
last_checked_at
```

---

## watchlist_origins

Orígenes posibles para una watchlist one-way o round-trip.

Campos:

```txt
id
watchlist_id
origin_code
created_at
```

Validaciones:

- `origin_code` debe ser código IATA de 3 letras.
- Ejemplo: `EZE`, `AEP`, `MVD`, `SCL`.

Índices:

```txt
watchlist_id
origin_code
unique(watchlist_id, origin_code)
```

---

## watchlist_destinations

Destinos posibles para una watchlist one-way o round-trip.

Campos:

```txt
id
watchlist_id
destination_code
created_at
```

Validaciones:

- `destination_code` debe ser código IATA de 3 letras.
- Ejemplo: `DUB`, `MAD`, `BCN`, `LON`.

Índices:

```txt
watchlist_id
destination_code
unique(watchlist_id, destination_code)
```

---

## watchlist_date_windows

Ventanas de fecha para viajes one-way o round-trip.

Campos:

```txt
id
watchlist_id
departure_date_from
departure_date_to
return_date_from
return_date_to
min_trip_days
max_trip_days
created_at
```

Reglas:

- Para `ONE_WAY`, `return_date_from`, `return_date_to`, `min_trip_days` y `max_trip_days` pueden ser nulos.
- Para `ROUND_TRIP`, debe existir una forma de calcular o definir la vuelta.
- `departure_date_from <= departure_date_to`.
- Si hay vuelta, `return_date_from <= return_date_to`.
- `min_trip_days <= max_trip_days`.

Índices:

```txt
watchlist_id
departure_date_from
departure_date_to
```

---

## watchlist_segments

Segmentos para viajes multi-city.

Campos:

```txt
id
watchlist_id
segment_order
origin_code
destination_code
date_from
date_to
created_at
```

Reglas:

- Usar solo para `MULTI_CITY`.
- Debe haber al menos 2 segmentos.
- `segment_order` empieza en 1.
- `date_from <= date_to`.
- Los segmentos deberían tener fechas coherentes entre sí.

Índices:

```txt
watchlist_id
segment_order
origin_code
destination_code
unique(watchlist_id, segment_order)
```

---

## flight_offers

Oferta de vuelo normalizada.

Campos:

```txt
id
watchlist_id
provider
provider_offer_id
origin_code
destination_code
trip_type
departure_date
return_date
total_price
currency
airline_codes
stops
duration_minutes
deep_link
raw_payload
found_at
created_at
```

Notas:

- `raw_payload` guarda la respuesta original del provider.
- `airline_codes` puede ser texto separado por coma o JSON, según decisión de implementación.
- `provider_offer_id` puede ser nulo si el provider no lo entrega.

Índices:

```txt
watchlist_id
provider
origin_code
destination_code
departure_date
return_date
total_price
found_at
```

Posible constraint anti-duplicados:

```txt
unique(
  watchlist_id,
  provider,
  origin_code,
  destination_code,
  departure_date,
  return_date,
  total_price,
  airline_codes,
  stops
)
```

---

## price_snapshots

Histórico de precios.

Campos:

```txt
id
watchlist_id
flight_offer_id
price
currency
checked_at
```

Uso:

- Calcular promedio histórico.
- Detectar mínimos.
- Mostrar gráficos.
- Evaluar descuentos.

Índices:

```txt
watchlist_id
flight_offer_id
checked_at
price
```

---

## alerts

Alertas generadas por el sistema.

Campos:

```txt
id
watchlist_id
flight_offer_id
alert_type
status
message
sent_to
sent_channel
sent_at
error_message
created_at
updated_at
```

Reglas:

- Una alerta puede ser generada pero no enviada.
- `status` permite controlar retry.
- `sent_channel` puede ser `TELEGRAM` o `EMAIL`.

Índices:

```txt
watchlist_id
flight_offer_id
alert_type
status
sent_at
created_at
```

Constraint recomendada para evitar duplicados:

```txt
unique(
  watchlist_id,
  flight_offer_id,
  alert_type,
  sent_channel
)
```

O manejar duplicados por lógica usando cooldown.

---

## provider_logs

Logs de llamadas a proveedores.

Campos:

```txt
id
provider
watchlist_id
request_hash
status
status_code
error_message
duration_ms
created_at
```

Uso:

- Debug.
- Auditoría.
- Rate limit.
- Métricas.

Índices:

```txt
provider
watchlist_id
status
created_at
request_hash
```

---

# Reglas de integridad

## Watchlist one-way

Debe tener:

```txt
trip_type = ONE_WAY
origins >= 1
destinations >= 1
date_windows >= 1
segments = 0
```

## Watchlist round-trip

Debe tener:

```txt
trip_type = ROUND_TRIP
origins >= 1
destinations >= 1
date_windows >= 1
segments = 0
min_trip_days y max_trip_days definidos
```

## Watchlist multi-city

Debe tener:

```txt
trip_type = MULTI_CITY
segments >= 2
origins opcional o vacío
destinations opcional o vacío
date_windows opcional o vacío
```

---

# Consultas importantes

## Watchlists activas para escanear

```sql
SELECT *
FROM watchlists
WHERE active = true
  AND (
    last_checked_at IS NULL
    OR last_checked_at <= now() - (check_frequency_hours || ' hours')::interval
  );
```

## Mínimo histórico de una watchlist

```sql
SELECT MIN(price)
FROM price_snapshots
WHERE watchlist_id = :watchlist_id;
```

## Promedio histórico de una watchlist

```sql
SELECT AVG(price)
FROM price_snapshots
WHERE watchlist_id = :watchlist_id;
```

## Últimas alertas

```sql
SELECT *
FROM alerts
ORDER BY created_at DESC
LIMIT 20;
```

---

# Consideraciones futuras

## Autenticación

En una fase futura puede agregarse:

- JWT.
- OAuth.
- Auth.js.
- Clerk.
- Supabase Auth.

## Multi-tenant

Si el proyecto crece a SaaS, agregar:

- Organization.
- Team.
- Subscription.
- Plan limits.
- Usage tracking.

## Monedas

Inicialmente usar una sola moneda por watchlist.

Futuro:

- Tabla de exchange rates.
- Conversión automática.
- Mostrar precio original y precio convertido.

## Aeropuertos y ciudades

Inicialmente validar IATA por regex.

Futuro:

- Tabla `airports`.
- Tabla `cities`.
- Search autocomplete.
- Country.
- Timezone.

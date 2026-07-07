# FareRadar — Prompts para Codex

Este archivo contiene prompts listos para usar con Codex.

La idea es trabajar por fases. No conviene pegar todos los prompts juntos. Usá uno por vez y revisá los cambios antes de avanzar.

---

# Prompt maestro

```txt
Actuá como un desarrollador senior full-stack especializado en Python, FastAPI, PostgreSQL, arquitectura limpia, APIs externas, automatización con workers, testing y buenas prácticas de producto.

Vamos a desarrollar un proyecto llamado FareRadar.

FareRadar es una aplicación web para crear, monitorear y recibir alertas de ofertas de vuelos. No debe estar limitada a un origen o destino fijo. El usuario debe poder crear watchlists con múltiples orígenes, múltiples destinos, rangos de fechas, duración mínima/máxima del viaje, precio máximo, cantidad máxima de escalas, tipo de viaje y reglas de alerta.

Tipos de viaje que debe soportar el diseño:
1. One-way.
2. Round-trip.
3. Multi-city.

El objetivo del proyecto es crear una plataforma sólida y extensible, no un script improvisado. Debe estar preparada para usar distintos proveedores de vuelos mediante una capa de abstracción llamada providers.

Stack obligatorio:
- Backend: Python + FastAPI.
- Base de datos: PostgreSQL.
- ORM: SQLAlchemy 2.
- Migraciones: Alembic.
- Validación: Pydantic.
- Workers/scheduler: Redis + Celery o RQ.
- Frontend: React + Vite + TypeScript + Tailwind CSS.
- Gráficos: Recharts.
- Infra local: Docker Compose.
- Deploy objetivo inicial: Railway.
- Testing: pytest para backend.
- Calidad: ruff o black.
- Notificaciones: Telegram primero, email después.

Reglas importantes:
- Antes de implementar una fase, explicá brevemente el plan.
- No mezcles fases sin avisar.
- Si aparece una decisión importante de arquitectura, seguridad, modelo de datos, proveedor externo, pricing o UX, preguntame antes de decidir.
- No inventes credenciales.
- No hardcodees API keys.
- Usá variables de entorno.
- Mantené el código limpio, tipado y modular.
- Separá lógica de negocio, modelos, schemas, routers, services, repositories y providers.
- Todo lo que dependa de APIs externas debe estar detrás de interfaces/adapters.
- Primero debe existir un MockFlightProvider para desarrollar sin depender de APIs reales.
- Después se agregará Amadeus como provider real.
- No hagas scraping de Google Flights ni de sitios que puedan bloquear el proyecto. El diseño debe priorizar APIs.
- El sistema debe guardar histórico de precios para poder detectar mínimos, promedios y descuentos reales.

Modelo conceptual:
- User: usuario de la app.
- Watchlist: configuración de búsqueda.
- WatchlistOrigin: orígenes posibles.
- WatchlistDestination: destinos posibles.
- WatchlistDateWindow: ventana de fechas para viajes one-way o round-trip.
- WatchlistSegment: segmentos ordenados para viajes multi-city.
- FlightOffer: oferta de vuelo normalizada.
- PriceSnapshot: registro histórico de precio.
- Alert: alerta generada/enviada.
- ProviderLog: logs de consultas a proveedores externos.

Reglas de alerta mínimas:
1. Alertar si el precio encontrado es menor o igual al precio máximo configurado.
2. Alertar si el precio está al menos X% por debajo del promedio histórico.
3. Alertar si el precio es un nuevo mínimo histórico para esa watchlist.
4. No alertar si supera el máximo de escalas.
5. No alertar si la duración del viaje es absurda o supera el límite configurado.
6. Evitar alertas duplicadas dentro de una ventana de cooldown.

Entregables esperados:
- Código funcional.
- README claro.
- .env.example.
- docker-compose.yml.
- Migraciones de base de datos.
- Tests básicos.
- Documentación en /docs.
- Instrucciones para correr localmente.
- Diagrama de arquitectura en Mermaid.
- Diagrama de flujo de alerta en Mermaid.

Primera tarea:
No escribas código todavía. Generá la planificación completa del proyecto, estructura de carpetas, fases de desarrollo, decisiones técnicas, entidades principales, endpoints iniciales, riesgos y orden recomendado de implementación.
```

---

# Fase 0 — Planificación y documentación

```txt
Actuá como arquitecto de software senior. Antes de escribir código, creá la documentación base del proyecto FareRadar.

Objetivo:
Documentar una aplicación web para alertas de ofertas de vuelos multi-destino y multi-city.

Generá estos archivos:

1. README.md
Debe incluir:
- Qué es FareRadar.
- Problema que resuelve.
- Funcionalidades principales.
- Stack.
- Cómo correr el proyecto localmente.
- Estado del proyecto.
- Roadmap resumido.

2. docs/PROJECT_BRIEF.md
Debe incluir:
- Visión del producto.
- Usuarios objetivo.
- Casos de uso.
- Qué problema personal resuelve.
- Qué problema comercial podría resolver si luego se convierte en SaaS.

3. docs/ARCHITECTURE.md
Debe incluir:
- Arquitectura general.
- Diagrama Mermaid de componentes.
- Diagrama Mermaid del flujo de búsqueda y alerta.
- Separación backend/frontend/workers/providers.
- Decisiones técnicas justificadas.

4. docs/DATABASE_MODEL.md
Debe incluir:
- Entidades.
- Relaciones.
- Campos sugeridos.
- Reglas de integridad.
- Índices recomendados.

5. docs/API_CONTRACT.md
Debe incluir:
- Endpoints REST iniciales.
- Payloads esperados.
- Respuestas esperadas.
- Códigos de error.
- Validaciones.

6. docs/ROADMAP.md
Debe incluir:
- Fases del proyecto.
- Entregables por fase.
- Criterios de aceptación.
- Qué queda fuera del MVP.

Restricciones:
- No escribas código de implementación todavía.
- No agregues dependencias innecesarias.
- El proyecto debe estar diseñado para soportar múltiples providers de vuelos.
- El primer provider debe ser MockFlightProvider.
- Amadeus debe quedar planificado como provider real futuro.
- El sistema debe soportar one-way, round-trip y multi-city desde el diseño.
```

---

# Fase 1 — Setup del monorepo

```txt
Creá la estructura inicial del proyecto FareRadar.

Objetivo:
Configurar un monorepo con backend, frontend, documentación, infraestructura local y preparación para Railway.

Estructura deseada:

fare-radar/
- backend/
  - app/
    - api/
    - core/
    - db/
    - models/
    - schemas/
    - services/
    - repositories/
    - providers/
    - workers/
    - notifications/
    - tests/
  - alembic/
  - pyproject.toml
  - Dockerfile
- frontend/
  - src/
  - package.json
  - Dockerfile
- docs/
- docker-compose.yml
- .env.example
- README.md

Backend:
- FastAPI.
- SQLAlchemy 2.
- Alembic.
- Pydantic.
- PostgreSQL.
- Redis preparado.
- pytest preparado.
- ruff o black configurado.

Frontend:
- React.
- Vite.
- TypeScript.
- Tailwind CSS.
- Estructura base limpia.

Docker Compose:
- backend.
- frontend.
- postgres.
- redis.

Railway:
- Preparar la API para escuchar en $PORT.
- Documentar servicios esperados: api, worker, scheduler, frontend, PostgreSQL y Redis.
- Documentar comandos esperados para API, worker y scheduler.
- No hacer deploy todavía.

Endpoints mínimos:
- GET /health
- GET /api/v1/status

Criterios de aceptación:
- docker compose up debe levantar servicios.
- El backend debe responder /health.
- El frontend debe mostrar una página inicial simple.
- No debe haber credenciales hardcodeadas.
- Debe existir .env.example.
- README debe incluir notas de Railway.

Antes de modificar archivos, explicá el plan y la estructura que vas a crear.
```

---

# Fase 2 — Modelos de base de datos y migraciones

```txt
Implementá el modelo de datos inicial de FareRadar.

Entidades:
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

Requisitos:
- Usar SQLAlchemy 2.
- Crear migraciones con Alembic.
- Usar UUID o IDs enteros consistentes.
- Agregar created_at y updated_at donde corresponda.
- Crear relaciones correctas.
- Agregar índices para búsquedas frecuentes:
  - watchlist_id.
  - provider.
  - found_at.
  - checked_at.
  - origin_code.
  - destination_code.
- Agregar enums o constraints para:
  - trip_type: ONE_WAY, ROUND_TRIP, MULTI_CITY.
  - cabin_class: ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST.
  - alert_type.
  - provider.
  - alert_status.

Criterios de aceptación:
- Las migraciones deben correr correctamente.
- Los modelos deben estar importados correctamente.
- Debe existir documentación breve del modelo.
- Agregar tests básicos de creación de entidades principales.

Antes de implementar, revisá si la estructura actual coincide con lo documentado. Si encontrás una decisión importante, preguntame antes.
```

---

# Fase 3 — CRUD de watchlists

```txt
Implementá endpoints REST para gestionar watchlists.

Endpoints:
- POST /api/v1/watchlists
- GET /api/v1/watchlists
- GET /api/v1/watchlists/{watchlist_id}
- PATCH /api/v1/watchlists/{watchlist_id}
- DELETE /api/v1/watchlists/{watchlist_id}

Debe soportar:
- Watchlist one-way.
- Watchlist round-trip.
- Watchlist multi-city.
- Múltiples orígenes.
- Múltiples destinos.
- Ventanas de fecha.
- Precio máximo.
- Moneda.
- Máximo de escalas.
- Adultos.
- Clase de cabina.
- Frecuencia de chequeo.
- Activar/desactivar watchlist.

Validaciones:
- IATA codes de 3 letras.
- max_price mayor a 0.
- adults mayor o igual a 1.
- fechas válidas.
- si trip_type es MULTI_CITY, debe haber al menos 2 segmentos.
- si trip_type no es MULTI_CITY, debe haber origins, destinations y date_windows.
- min_trip_days no puede ser mayor a max_trip_days.

Arquitectura obligatoria:
- Router.
- Schemas Pydantic.
- Service.
- Repository.
- Modelos SQLAlchemy.

Criterios de aceptación:
- Tests de creación.
- Tests de validación.
- Tests de listado.
- Tests de actualización.
- Tests de borrado lógico o desactivación.
```

---

# Fase 4 — Provider abstraction y MockFlightProvider

```txt
Implementá la capa de providers de vuelos.

Objetivo:
Que el sistema pueda consultar vuelos sin depender todavía de APIs reales.

Crear:
- FlightSearchProvider como interfaz/base class.
- FlightSearchRequest como schema interno normalizado.
- NormalizedFlightOffer como schema interno normalizado.
- ProviderManager para elegir provider activo.
- MockFlightProvider que devuelva ofertas falsas pero realistas.

El provider debe soportar:
- one-way.
- round-trip.
- multi-city.
- múltiples orígenes y destinos mediante expansión de combinaciones.
- moneda.
- adultos.
- clase de cabina.
- máximo de resultados.

NormalizedFlightOffer debe incluir:
- provider.
- origin_code.
- destination_code.
- trip_type.
- departure_date.
- return_date opcional.
- total_price.
- currency.
- airline_codes.
- stops.
- duration_minutes.
- deep_link.
- raw_payload.

Criterios de aceptación:
- El MockFlightProvider debe generar precios variados.
- Debe ser determinístico en tests.
- Debe haber tests del provider.
- Ninguna lógica de negocio debe depender directamente de Amadeus, Skyscanner o Duffel.
```

---

# Fase 5 — Search engine y guardado de snapshots

```txt
Implementá el motor que ejecuta búsquedas de vuelos para una watchlist.

Objetivo:
Tomar una watchlist activa, generar combinaciones de búsqueda, consultar el provider, normalizar ofertas y guardar resultados.

Crear:
- FlightSearchService.
- WatchlistExpansionService.
- PriceSnapshotService.
- FlightOfferRepository.

Debe:
- Leer una watchlist.
- Expandir combinaciones:
  - cada origen contra cada destino.
  - cada fecha válida dentro de la ventana.
  - cada duración válida para round-trip.
  - cada segmento para multi-city.
- Consultar ProviderManager.
- Guardar FlightOffer.
- Guardar PriceSnapshot.
- Evitar duplicados obvios.
- Guardar ProviderLog.

Endpoint:
- POST /api/v1/watchlists/{id}/run

Criterios de aceptación:
- Ejecutar búsqueda manual por endpoint.
- Guardar ofertas en DB.
- Guardar snapshots en DB.
- Tests de expansión.
- Tests de persistencia.
- Tests con MockFlightProvider.
```

---

# Fase 6 — Motor de reglas de alerta

```txt
Implementá AlertRulesEngine.

Reglas mínimas:
1. below_max_price:
   Alertar si total_price <= watchlist.max_price.
2. below_historical_average:
   Alertar si total_price está al menos X% debajo del promedio histórico de esa watchlist.
3. new_historical_minimum:
   Alertar si total_price es el precio más bajo registrado para esa watchlist.
4. max_stops:
   No alertar si stops > watchlist.max_stops.
5. cooldown:
   No repetir alerta equivalente dentro de X horas.
6. duration:
   No alertar si duration_minutes supera un límite razonable configurable.

Crear:
- AlertRulesEngine.
- AlertService.
- AlertRepository.

Endpoints:
- GET /api/v1/watchlists/{id}/alerts
- GET /api/v1/alerts

Criterios de aceptación:
- Tests unitarios de cada regla.
- Tests de cooldown.
- Tests de mínimo histórico.
- Tests de promedio histórico.
- Alertas guardadas en DB.
```

---

# Fase 7 — Notificaciones por Telegram y email

```txt
Implementá sistema de notificaciones.

Primero Telegram:
- Configurar TELEGRAM_BOT_TOKEN.
- Guardar telegram_chat_id en User.
- Enviar alerta formateada.

Después email:
- SMTP_HOST.
- SMTP_PORT.
- SMTP_USER.
- SMTP_PASSWORD.
- SMTP_FROM.

Mensaje de alerta debe incluir:
- Nombre de watchlist.
- Ruta.
- Fechas.
- Precio.
- Moneda.
- Aerolínea/códigos.
- Escalas.
- Duración.
- Motivo de alerta.
- Link/deep_link si existe.

Criterios de aceptación:
- NotificationService abstracto.
- TelegramNotificationProvider.
- EmailNotificationProvider.
- Tests con mocks.
- No enviar mensajes reales en tests.
- Manejo de errores.
```

---

# Fase 8 — Workers, scheduler y ejecución automática

```txt
Implementá ejecución automática de watchlists.

Objetivo:
Que las watchlists activas se consulten según su frecuencia configurada.

Usar:
- Redis.
- Celery o RQ.
- Scheduler.

Crear jobs:
- scan_active_watchlists.
- run_watchlist_search.
- evaluate_alerts_for_watchlist.
- send_pending_alerts.

Requisitos:
- No ejecutar watchlists inactivas.
- Respetar check_frequency_hours.
- Registrar errores sin romper todo el worker.
- Guardar ProviderLog.
- Evitar ejecuciones duplicadas simultáneas de la misma watchlist.

Criterios de aceptación:
- Worker levanta con Docker Compose.
- Scheduler dispara tareas.
- Se puede ejecutar una tarea manualmente.
- Logs claros.
- Tests básicos de scheduling o servicios asociados.
```

---

# Fase 9 — Frontend dashboard

```txt
Implementá dashboard web.

Pantallas:
1. Home/Dashboard:
   - cantidad de watchlists activas.
   - últimas ofertas.
   - últimas alertas.
   - precio mínimo detectado.

2. Watchlists:
   - listado.
   - crear.
   - editar.
   - activar/desactivar.
   - ejecutar búsqueda manual.

3. Detalle de watchlist:
   - configuración.
   - ofertas encontradas.
   - histórico de precios.
   - alertas enviadas.

4. Crear watchlist:
   - nombre.
   - tipo de viaje.
   - orígenes.
   - destinos.
   - fechas.
   - segmentos multi-city.
   - precio máximo.
   - reglas.

5. Settings:
   - Telegram chat id.
   - email.
   - moneda preferida.

Usar:
- React.
- TypeScript.
- Tailwind.
- Recharts.
- Fetch/Axios.
- Componentes reutilizables.

Criterios de aceptación:
- UI limpia.
- Formularios validados.
- Manejo de loading/error/empty states.
- Gráfico de evolución de precios.
- Tabla de ofertas.
- Tabla de alertas.
```

---

# Fase 10 — AmadeusProvider real

```txt
Implementá integración real con Amadeus.

Requisitos:
- AMADEUS_CLIENT_ID.
- AMADEUS_CLIENT_SECRET.
- AMADEUS_ENV=test|production.
- Cliente HTTP aislado.
- Manejo de OAuth/token.
- Rate limit básico.
- Manejo de errores.
- Normalización de respuesta a NormalizedFlightOffer.
- No romper el MockFlightProvider.

Implementar primero:
- one-way.
- round-trip.

Luego:
- multi-city mediante POST.
- soporte para máximo de resultados.
- currency.
- adults.
- cabin class.

Criterios de aceptación:
- Tests con respuestas mockeadas.
- No llamar API real en tests.
- Documentar cómo conseguir credenciales.
- Documentar limitaciones.
- Permitir seleccionar provider por variable de entorno:
  FLIGHT_PROVIDER=mock|amadeus
```

---

# Fase 11 — Deploy en Railway y producción

```txt
Prepará el proyecto para deploy en Railway.

Requisitos:
- Dockerfiles optimizados.
- Variables de entorno documentadas.
- Comando para migraciones.
- Configuración de backend.
- Configuración de frontend.
- Configuración de worker.
- Configuración de scheduler.
- Logging.
- Healthcheck.
- README de deploy.

Railway:
- Crear o documentar servicios separados para API, worker, scheduler y frontend.
- Usar Railway Postgres.
- Usar Railway Redis.
- La API debe escuchar en $PORT.
- Documentar comandos:
  - API: uvicorn app.main:app --host 0.0.0.0 --port $PORT
  - Worker: celery -A app.workers.celery_app worker --loglevel=info
  - Scheduler: celery -A app.workers.celery_app beat --loglevel=info

Criterios de aceptación:
- El proyecto puede correr localmente con Docker Compose.
- El backend puede correr en producción.
- El worker puede correr en producción.
- Las migraciones pueden ejecutarse de forma segura.
- No hay secretos en el repo.
- Existe checklist de producción.
```

---

# Prompt para doble revisión de cambios

```txt
Revisá los cambios hechos en FareRadar, pero asumí explícitamente que la revisión automática puede equivocarse.

Objetivo:
Hacer una revisión técnica crítica de los cambios recientes sin tratarlos como correctos por defecto.

Reglas:
- No asumas que el código generado previamente está bien.
- No asumas que una revisión anterior fue completa.
- Señalá riesgos, bugs, omisiones, inconsistencias y decisiones dudosas.
- Marcá qué cosas necesitan doble revisión humana o una segunda pasada técnica.
- Si algo parece correcto pero no fue probado, indicá el riesgo.
- Si una conclusión depende de una suposición, decilo claramente.
- No hagas cambios todavía salvo que te lo pida explícitamente.

Revisá especialmente:
- Arquitectura router/service/repository/provider.
- Dependencias indebidas entre capas.
- Validaciones.
- Manejo de errores.
- Migraciones.
- Tests.
- Variables de entorno.
- Compatibilidad con Railway.
- Riesgo de llamadas reales a providers o notificaciones durante tests.
- Riesgo de alertas duplicadas.

Devolvé:
1. Hallazgos ordenados por severidad.
2. Cambios que parecen correctos pero requieren doble revisión.
3. Tests faltantes.
4. Riesgos para Railway.
5. Preguntas antes de corregir.
```

---

# Prompt para revisar código

```txt
Revisá el estado actual del proyecto FareRadar como desarrollador senior.

Objetivo:
Detectar problemas de arquitectura, bugs, deuda técnica, acoplamientos indebidos, falta de tests, problemas de nombres, validaciones incompletas y riesgos de producción.

Revisá especialmente:
- Separación router/service/repository/provider.
- Uso correcto de SQLAlchemy.
- Uso correcto de Pydantic.
- Validaciones de watchlists.
- Manejo de errores.
- Variables de entorno.
- Tests.
- Docker Compose.
- Acoplamiento a providers externos.
- Posibles alertas duplicadas.
- Posible explosión de combinaciones.

No implementes cambios todavía. Primero devolvé:
1. Diagnóstico.
2. Problemas encontrados.
3. Prioridad de arreglo.
4. Plan de cambios.
5. Preguntas importantes antes de tocar código.
```

---

# Prompt para pedir implementación incremental

```txt
Implementá solamente la siguiente fase del proyecto FareRadar: [NOMBRE_DE_LA_FASE].

Restricciones:
- No avances a fases futuras.
- No cambies decisiones ya documentadas salvo que sea necesario.
- Si necesitás cambiar arquitectura, preguntame primero.
- Agregá o actualizá tests.
- Actualizá documentación si cambia el comportamiento.
- Mantené el código simple y modular.
- No agregues dependencias innecesarias.
- No uses credenciales reales.
- No rompas Docker Compose.

Al terminar, devolvé:
1. Archivos modificados.
2. Qué se implementó.
3. Cómo probarlo.
4. Tests agregados.
5. Pendientes.
```

---

# Prompt para pedir tests

```txt
Agregá tests para la funcionalidad actual de FareRadar.

Objetivo:
Aumentar cobertura de tests sin cambiar comportamiento.

Priorizar:
- Validaciones de watchlists.
- CRUD de watchlists.
- WatchlistExpansionService.
- MockFlightProvider.
- AlertRulesEngine.
- Cooldown de alertas.
- Persistencia de snapshots.
- Manejo de errores de provider.

Restricciones:
- No llamar APIs externas.
- No enviar notificaciones reales.
- Usar mocks/fakes donde corresponda.
- No cambiar comportamiento productivo.
- Si encontrás un bug, marcá primero el bug y proponé fix.
```

---

# Prompt para mejorar documentación

```txt
Mejorá la documentación del proyecto FareRadar.

Objetivo:
Que una persona nueva pueda entender, correr y contribuir al proyecto.

Revisá y actualizá:
- README.md.
- docs/PROJECT_BRIEF.md.
- docs/ARCHITECTURE.md.
- docs/DATABASE_MODEL.md.
- docs/API_CONTRACT.md.
- docs/ROADMAP.md.

Debe quedar claro:
- Qué problema resuelve.
- Cómo correr localmente.
- Cómo funciona la arquitectura.
- Cómo se ejecutan búsquedas.
- Cómo se generan alertas.
- Cómo se agregan nuevos providers.
- Qué variables de entorno existen.
- Qué está dentro y fuera del MVP.
```

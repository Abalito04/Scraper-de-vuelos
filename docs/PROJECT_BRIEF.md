# FareRadar — Project Brief

## Visión del producto

FareRadar es una aplicación web para crear alertas inteligentes de vuelos.

El usuario puede configurar búsquedas flexibles y recibir notificaciones cuando aparezcan precios interesantes, descuentos, mínimos históricos o vuelos que cumplan reglas personalizadas.

La aplicación no está limitada a una ruta fija. Debe soportar múltiples orígenes, múltiples destinos y distintos tipos de viaje.

---

## Problema

Buscar vuelos baratos manualmente es repetitivo, lento y poco confiable.

El usuario suele revisar muchas veces:

- Google Flights.
- Skyscanner.
- Kayak.
- Sitios de aerolíneas.
- Agencias online.
- Promociones aisladas.

Pero puede perder una oferta si no revisa en el momento correcto.

FareRadar automatiza el monitoreo y permite tomar mejores decisiones.

---

## Usuario objetivo inicial

El usuario inicial es una persona que quiere viajar al exterior el año siguiente y necesita encontrar buenas oportunidades de pasajes.

Ejemplos:

- Alguien que quiere viajar a Dublín.
- Alguien que tiene varios destinos posibles en Europa.
- Alguien que puede salir desde Buenos Aires, Montevideo, Santiago o São Paulo.
- Alguien que tiene fechas flexibles.
- Alguien que quiere que el sistema le avise cuando conviene comprar.

---

## Usuarios potenciales futuros

Si se convierte en SaaS, FareRadar podría servir para:

- Viajeros frecuentes.
- Nómadas digitales.
- Estudiantes que viajan al exterior.
- Personas que planean vacaciones.
- Agencias de viaje pequeñas.
- Creadores de contenido de viajes.
- Equipos que necesitan monitorear rutas corporativas.

---

## Caso de uso principal

El usuario crea una watchlist:

```txt
Nombre: Europa 2027
Orígenes: EZE, AEP, MVD
Destinos: DUB, MAD, BCN, LON
Tipo: ROUND_TRIP
Fecha salida: entre 2027-03-01 y 2027-06-30
Duración: entre 14 y 35 días
Precio máximo: USD 900
Escalas máximas: 2
Alertar si:
- precio menor o igual a USD 900
- precio 20% menor al promedio histórico
- precio es nuevo mínimo histórico
```

El sistema consulta periódicamente, guarda precios y avisa cuando aparece una oportunidad.

---

## Tipos de viaje

### One-way

Viaje de ida.

Ejemplo:

```txt
EZE → DUB
Fecha: 2027-05-10
```

### Round-trip

Viaje de ida y vuelta.

Ejemplo:

```txt
EZE → DUB
DUB → EZE
Salida: 2027-05-10
Vuelta: 2027-05-30
```

### Multi-city

Viaje con varios tramos.

Ejemplo:

```txt
EZE → MAD
MAD → DUB
DUB → EZE
```

---

## Propuesta de valor

FareRadar no solo busca precios. También interpreta si una oferta es relevante.

Debe evaluar:

- Precio absoluto.
- Precio contra presupuesto del usuario.
- Precio contra histórico.
- Precio contra mínimo histórico.
- Cantidad de escalas.
- Duración total.
- Aeropuertos alternativos.
- Repetición de alertas.

---

## MVP

El MVP debe incluir:

- Backend funcional.
- CRUD de watchlists.
- MockFlightProvider.
- Ejecución manual de búsquedas.
- Guardado de ofertas.
- Guardado de snapshots de precios.
- Motor básico de alertas.
- Telegram como canal de notificación.
- Documentación.
- Tests básicos.

---

## Fuera del MVP

No incluir inicialmente:

- Scraping de Google Flights.
- Compra de pasajes.
- Gestión de pagos.
- Usuarios multi-tenant avanzados.
- Login social.
- Integración real con muchas APIs.
- Machine learning complejo.
- App mobile.
- WhatsApp.
- Predicción real de precios.

---

## Riesgos principales

### APIs externas

Las APIs de vuelos pueden tener límites, costos, reglas de uso o disponibilidad limitada.

Mitigación:

- Crear primero MockFlightProvider.
- Aislar proveedores detrás de interfaces.
- Permitir cambiar provider por configuración.

### Datos incompletos

No todos los proveedores devuelven los mismos campos.

Mitigación:

- Normalizar respuestas.
- Guardar `raw_payload`.
- Diseñar campos opcionales.

### Alertas duplicadas

El sistema podría enviar demasiadas alertas.

Mitigación:

- Implementar cooldown.
- Comparar alertas equivalentes.
- Permitir configurar frecuencia.

### Complejidad de fechas flexibles

Combinar múltiples orígenes, destinos y fechas puede explotar en muchas consultas.

Mitigación:

- Limitar rangos.
- Usar expansión controlada.
- Agregar límites por watchlist.
- Programar búsquedas gradualmente.

---

## Objetivo técnico

El proyecto debe demostrar capacidad para construir software real:

- Diseño modular.
- Buen modelo de datos.
- API REST clara.
- Integración con servicios externos.
- Workers.
- Scheduler.
- Tests.
- Docker.
- Documentación.
- Frontend con visualización.
- Deploy.

---

## Nombre del proyecto

Nombre principal:

```txt
FareRadar
```

Alternativas:

```txt
FlightRadar Deals
TravelDeal Watcher
SkyAlert
FlyScout
FareScout
```

# Configuración del Proyecto ANJOS Django

## Pasarela de Pago (Stripe)

### Variables de Entorno Requeridas en Railway

Ir a: Railway Dashboard → Variables (o Settings → Variables)

Agregar estas variables:

| Variable | Valor (modo prueba) | Descripción |
|----------|---------------------|-------------|
| `STRIPE_SECRET_KEY` | `sk_test_...` | Clave secreta de Stripe (empieza con sk_test_ o sk_live_) |
| `STRIPE_PUBLISHABLE_KEY` | `pk_test_...` | Clave pública de Stripe (empieza con pk_test_ o pk_live_) |
| `STRIPE_WEBHOOK_SECRET` | `whsec_...` | Clave de firma del webhook (opcional pero recomendado) |
| `RAILWAY_PUBLIC_URL` | `https://anjosdjango-production.up.railway.app` | URL pública del deploy |

### Flujo de Pago Implementado

1. Usuario agrega productos al carrito real (base de datos)
2. Va a `/orders/checkout/` → ingresa dirección y método de pago
3. Al confirmar con TARJETA:
   - Se crea la orden en BD con estado PENDING
   - Se reduce el stock de los productos
   - Se limpia el carrito
   - Se crea una sesión de Stripe Checkout con los productos reales
   - El usuario es redirigido a Stripe para pagar
4. Si el pago es exitoso:
   - Stripe redirige a `/orders/stripe/success/?order_id=X`
   - La orden cambia a PROCESSING
   - Se muestra página de confirmación profesional
5. Si el usuario cancela:
   - Stripe redirige a `/orders/stripe/cancel/?order_id=X`
   - La orden queda en PENDING (puede reintentarse)
6. Webhook asincrónico:
   - Stripe envía eventos a `/webhooks/stripe/`
   - Actualiza el estado de la orden independientemente del navegador del usuario

### URLs Principales

- `/orders/checkout/` — Checkout con dirección de envío
- `/orders/stripe/success/` — Éxito de pago Stripe
- `/orders/stripe/cancel/` — Cancelación de pago Stripe
- `/webhooks/stripe/` — Webhook de Stripe (POST)

### Notas Técnicas

- `BASE_URL` en settings.py se lee de `RAILWAY_PUBLIC_URL`
- El servicio Stripe verifica que las claves empiecen con `sk_` y `pk_` para considerarse configurado
- Moneda: COP (pesos colombianos)
- Stripe Checkout solicita dirección de facturación, dirección de envío (solo Colombia) y teléfono

## Build / Deploy

- Framework: Django 4.2
- Base de datos: PostgreSQL en Railway (vía DATABASE_URL)
- Static files: WhiteNoise
- Media files: Cloudinary

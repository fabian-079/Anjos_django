# Configuración del Proyecto ANJOS Django

## Pasarela de Pago (Stripe + Wompi PSE)

### Variables de Entorno Requeridas en Railway

Ir a: Railway Dashboard → Variables (o Settings → Variables)

#### Stripe (Tarjeta de crédito/débito)

| Variable | Valor (modo prueba) | Descripción |
|----------|---------------------|-------------|
| `STRIPE_SECRET_KEY` | `sk_test_...` | Clave secreta de Stripe (empieza con sk_test_ o sk_live_) |
| `STRIPE_PUBLISHABLE_KEY` | `pk_test_...` | Clave pública de Stripe (empieza con pk_test_ o pk_live_) |
| `STRIPE_WEBHOOK_SECRET` | `whsec_...` | Clave de firma del webhook (opcional) |

#### Wompi (PSE - Transferencia bancaria)

| Variable | Valor (modo prueba) | Descripción |
|----------|---------------------|-------------|
| `WOMPI_PUBLIC_KEY` | `pub_test_...` o `pub_prod_...` | Clave pública de Wompi |
| `WOMPI_PRIVATE_KEY` | `prv_test_...` o `prv_prod_...` | Clave privada de Wompi |
| `WOMPI_INTEGRITY_KEY` | `test_integrity_...` | Clave de integridad para firmar transacciones |

#### General

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `RAILWAY_PUBLIC_URL` | `https://anjosdjango-production.up.railway.app` | URL pública del deploy |

### Flujo de Pago Implementado

#### Tarjeta (Stripe)
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

#### PSE (Wompi)
1. Usuario agrega productos al carrito real
2. Va a `/orders/checkout/` → selecciona PSE
3. Ingresa: tipo de persona, tipo de documento, número de documento, banco
4. Al confirmar:
   - Se crea la orden en BD con estado PENDING
   - Se crea una transacción PSE en Wompi
   - El usuario es redirigido al portal PSE de su banco
5. El usuario autoriza la transferencia en el portal de su banco
6. El banco redirige a `/orders/wompi/callback/?id=...&status=...`
7. Webhook de Wompi en `/webhooks/wompi/` confirma el estado asincrónicamente
8. La orden cambia a PROCESSING cuando el pago es aprobado

#### Efectivo (Contra entrega)
1. Usuario selecciona EFECTIVO en el checkout
2. Se crea la orden en BD con estado PENDING
3. El pago se realiza al momento de recibir el pedido

### URLs Principales

- `/orders/checkout/` — Checkout con dirección de envío
- `/orders/stripe/success/` — Éxito de pago Stripe
- `/orders/stripe/cancel/` — Cancelación de pago Stripe
- `/webhooks/stripe/` — Webhook de Stripe (POST)
- `/orders/wompi/callback/` — Callback de Wompi después de PSE
- `/webhooks/wompi/` — Webhook de Wompi (POST)

### Notas Técnicas

- `BASE_URL` en settings.py se lee de `RAILWAY_PUBLIC_URL`
- El servicio Stripe verifica que las claves empiecen con `sk_` y `pk_` para considerarse configurado
- El servicio Wompi verifica que las claves empiecen con `pub_` y `prv_` para considerarse configurado
- Moneda: COP (pesos colombianos)
- Stripe Checkout solicita dirección de facturación, dirección de envío (solo Colombia) y teléfono
- Wompi PSE usa sandbox por defecto; cambiar a producción cuando esté listo

### Obtener credenciales de Wompi

1. Crear cuenta en https://comercios.wompi.co/
2. Ir a Configuración → Llaves API
3. Copiar Llave pública y Llave privada
4. Para el ambiente de pruebas (sandbox), las claves empiezan con `pub_test_` y `prv_test_`

## Build / Deploy

- Framework: Django 4.2
- Base de datos: PostgreSQL en Railway (vía DATABASE_URL)
- Static files: WhiteNoise
- Media files: Cloudinary

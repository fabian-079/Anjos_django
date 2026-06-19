# Configuración del Proyecto ANJOS Django

## Pasarela de Pago (Wompi)

### Variables de Entorno Requeridas en Railway

Ir a: Railway Dashboard → Variables (o Settings → Variables)

#### Wompi (Tarjeta + PSE)

| Variable | Valor (modo prueba) | Descripción |
|----------|---------------------|-------------|
| `WOMPI_PUBLIC_KEY` | `pub_test_...` o `pub_prod_...` | Clave pública de Wompi |
| `WOMPI_PRIVATE_KEY` | `prv_test_...` o `prv_prod_...` | Clave privada de Wompi |
| `WOMPI_INTEGRITY_KEY` | `test_integrity_...` | Clave de integridad para firmar transacciones |

#### Email (para notificaciones de registro, ordenes, etc.)

| Variable | Valor (ejemplo Gmail) | Descripción |
|----------|----------------------|-------------|
| `EMAIL_HOST` | `smtp.gmail.com` | Servidor SMTP |
| `EMAIL_PORT` | `587` | Puerto SMTP (587 para TLS) |
| `EMAIL_HOST_USER` | `tu_email@gmail.com` | Usuario SMTP |
| `EMAIL_HOST_PASSWORD` | `tu_app_password` | Contraseña de aplicación (no la normal de Gmail) |
| `DEFAULT_FROM_EMAIL` | `Anjos Jewelry <noreply@anjos.com>` | Remitente por defecto |

> **Nota Gmail:** Para usar Gmail como SMTP, debes generar una "Contraseña de aplicación" en tu cuenta de Google (Configuración de cuenta → Seguridad → Verificación en dos pasos → Contraseñas de aplicación). No uses tu contraseña normal de Gmail.

#### General

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `RAILWAY_PUBLIC_URL` | `https://anjosdjango-production.up.railway.app` | URL pública del deploy |

### Flujo de Pago Implementado

#### Tarjeta (Wompi)
1. Usuario agrega productos al carrito real (base de datos)
2. Va a `/orders/checkout/` → ingresa dirección y método de pago
3. Al confirmar con TARJETA:
   - Se crea la orden en BD con estado PENDING
   - Se tokeniza la tarjeta con Wompi (seguro, datos no tocan nuestro servidor)
   - Se crea la transacción con el token en Wompi
   - Si es aprobada: la orden cambia a PROCESSING inmediatamente
   - Si requiere 3D Secure: redirige a Wompi para autenticación
4. Si el pago es exitoso:
   - Se muestra página de confirmación profesional
   - La orden cambia a PROCESSING
5. Si es rechazada:
   - Se muestra mensaje de error al usuario
   - La orden queda en PENDING (puede reintentarse desde Mis Órdenes)

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
- `/orders/wompi/callback/` — Callback de Wompi después de PSE
- `/webhooks/wompi/` — Webhook de Wompi (POST)

### Notas Técnicas

- `BASE_URL` en settings.py se lee de `RAILWAY_PUBLIC_URL`
- El servicio Wompi verifica que las claves empiecen con `pub_` y `prv_` para considerarse configurado
- Moneda: COP (pesos colombianos)
- Wompi PSE usa sandbox por defecto; cambiar a producción cuando esté listo
- El envío de emails usa Django SMTP; si no está configurado, los emails se intentan enviar pero no bloquean el flujo

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

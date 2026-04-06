# ANJOS - Sistema de Gestión de Joyería ⭐ 10/10

Sistema de gestión completo para joyería desarrollado con Django y arquitectura hexagonal.

## 🎯 Proyecto Nivel 10/10

Este proyecto incluye **todas las funcionalidades avanzadas** requeridas:

✅ **Carga inicial de datos** - 12 productos, 6 categorías, usuarios de prueba  
✅ **Envío de correos masivos** - Sistema completo con personalización  
✅ **Reportes estadísticos en PDF** - Ventas, inventario, usuarios  
✅ **Consumo de Web Services** - APIs externas en tiempo real  

## Arquitectura Hexagonal

Este proyecto sigue los principios de arquitectura hexagonal (puertos y adaptadores):

- **Domain**: Entidades de negocio y repositorios abstractos
- **Application**: Casos de uso (lógica de negocio)
- **Infrastructure**: Implementaciones concretas (modelos Django, repositorios)
- **Adapters**: Interfaces externas (vistas, APIs)

## Requisitos

- Python 3.8+
- MySQL 5.7+
- pip

## Instalación Rápida

```bash
# 1. Crear entorno virtual
python -m venv venv
.\venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear base de datos MySQL
# En MySQL: CREATE DATABASE anjos_db;

# 4. Ejecutar migraciones
python manage.py migrate

# 5. Cargar datos iniciales
python init_db.py

# 6. Ejecutar servidor
python manage.py runserver
```

## Credenciales por Defecto

- **Email**: admin@anjos.com
- **Contraseña**: admin123

## Funcionalidades

### Para Clientes
- Catálogo de productos con filtros avanzados
- Carrito de compras con validación de stock
- Gestión de pedidos con seguimiento
- Solicitudes de reparación
- Solicitudes de personalización
- Favoritos
- Notificaciones en tiempo real
- **Consulta de tasas de cambio**
- **Calculadora de envíos**

### Para Administradores
- Gestión de productos y categorías
- Gestión de usuarios y roles
- Gestión de pedidos con estados
- Gestión de reparaciones y asignación de técnicos
- Gestión de personalizaciones con cotizaciones
- Dashboard con estadísticas en tiempo real
- **📧 Envío de correos masivos con personalización**
- **📊 Generación de reportes estadísticos en PDF**
- **🌐 Integración con Web Services externos**
- **💱 Consulta de precios en diferentes monedas**
- **📈 Reportes de ventas, inventario y usuarios**

## Estructura del Proyecto

```
anjos_django/
├── domain/              # Capa de dominio
│   ├── entities/        # Entidades de negocio
│   └── repositories/    # Interfaces de repositorios
├── application/         # Capa de aplicación
│   └── use_cases/       # Casos de uso
├── infrastructure/      # Capa de infraestructura
│   ├── models/          # Modelos Django
│   ├── repositories/    # Implementaciones de repositorios
│   └── container.py     # Inyección de dependencias
├── adapters/            # Capa de adaptadores
│   └── api/             # Vistas y controladores
├── templates/           # Plantillas HTML
├── static/              # Archivos estáticos
└── uploads/             # Archivos subidos
```

## 🚀 Nuevas Funcionalidades Implementadas

### 1. Carga Inicial de Datos
- Script automatizado `init_db.py`
- 6 categorías de productos
- 12 productos de ejemplo con datos realistas
- Usuarios de prueba (admin y cliente)

### 2. Sistema de Correos Masivos
- Envío masivo a todos los usuarios o por rol
- Personalización con nombre del usuario
- Correos de bienvenida, confirmaciones, notificaciones
- Interfaz web en `/emails/mass-send/`

### 3. Reportes Estadísticos en PDF
- **Reporte de Ventas**: Estadísticas, top órdenes, filtros por fecha
- **Reporte de Inventario**: Stock, productos con alerta, valor total
- **Reporte de Usuarios**: Lista completa con roles y contactos
- Acceso en `/reports/`

### 4. Consumo de Web Services
- **Exchange Rate API**: Tasas de cambio en tiempo real
- **Metals Live API**: Precio del oro actualizado
- **IP Geolocation**: Información de ubicación
- **Weather API**: Datos meteorológicos
- **Shipping Calculator**: Cálculo de costos de envío
- Dashboard interactivo en `/webservices/`

## 📚 Documentación Adicional

- **`NUEVAS_FUNCIONALIDADES.md`** - Guía completa de las nuevas funcionalidades
- **`ARQUITECTURA.md`** - Explicación detallada de arquitectura hexagonal
- **`INSTALACION.md`** - Guía paso a paso de instalación
- **`CAMBIOS_REALIZADOS.md`** - Resumen de todas las mejoras

## Notas Técnicas

- La arquitectura hexagonal separa la lógica de negocio de los detalles de implementación
- Los casos de uso no dependen de Django directamente
- Los repositorios abstraen el acceso a datos
- El contenedor de dependencias (`container.py`) gestiona la creación de objetos
- **Nuevos casos de uso**: EmailUseCases, ReportUseCases, WebServiceUseCases
- **APIs REST** disponibles para integración externa

# API de Transacciones Financieras - Covalto

API REST para gestión de transacciones financieras con flujo de aprobación Operador-Aprobador.

## Características

- Autenticación con headers (v1) y JWT (v2)
- Flujo de aprobación maker-checker
- Máquina de estados para transacciones
- Referencias únicas y autogeneradas
- PostgreSQL en Render
- Documentación interactiva con Swagger UI

## Tecnologías

- **FastAPI** - Framework web moderno
- **SQLAlchemy** - ORM para base de datos
- **PostgreSQL** - Base de datos en Render
- **JWT** - Autenticación segura
- **Pydantic** - Validación de datos

## Arquitectura

```
app/
├── api/
│   ├── v1/          # API con autenticación por headers
│   └── v2/          # API con JWT y referencias autogeneradas
├── models/          # Modelos de dominio (Transaction, Usuario)
├── schemas/         # Schemas Pydantic para validación
├── services/        # Lógica de negocio (5 reglas de Covalto)
├── crud/            # Operaciones CRUD
├── deps/            # Dependencias (auth, db)
├── core/            # Configuración y seguridad
└── db/              # Configuración de base de datos
```

## Instalación Local

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/fastapi-cap.git
cd fastapi-cap
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la carpeta `app/`:

```env
SECRET_KEY=tu-clave-super-secreta-cambiar-en-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

### 5. Inicializar la base de datos

```bash
cd app
python init_db.py
```

### 6. Ejecutar el servidor

```bash
uvicorn main:app --reload
```

La API estará disponible en: http://localhost:8000

## Documentación

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints Principales

### API v1 (Headers: X-User-Role, X-User-Id)

```
POST   /api/v1/transactions              # Crear transacción
POST   /api/v1/transactions/{id}/submit  # Enviar a aprobación
POST   /api/v1/transactions/{id}/approve # Aprobar
POST   /api/v1/transactions/{id}/reject  # Rechazar
POST   /api/v1/transactions/{id}/execute # Ejecutar
GET    /api/v1/transactions/{id}         # Consultar
GET    /api/v1/transactions              # Listar todas
```

### API v2 (JWT Authentication)

```
POST   /api/v2/transactions              # Crear con reference auto
POST   /api/v2/transactions/{id}/submit  # Enviar a aprobación
POST   /api/v2/transactions/{id}/approve # Aprobar
POST   /api/v2/transactions/{id}/reject  # Rechazar
POST   /api/v2/transactions/{id}/execute # Ejecutar
GET    /api/v2/transactions/{id}         # Consultar
GET    /api/v2/transactions              # Listar (filtrado por usuario)
```

### Autenticación

```
POST   /api/v1/auth/usuarios             # Registrar usuario
POST   /api/v1/auth/login                # Login (obtener JWT)
```

## Ejemplo de Uso (v1)

### 1. Crear transacción (OPERADOR)

```bash
curl -X POST "http://localhost:8000/api/v1/transactions" \
  -H "X-User-Role: OPERADOR" \
  -H "X-User-Id: op-001" \
  -H "Content-Type: application/json" \
  -d '{
    "reference": "PAY-001",
    "amount": 1000.50,
    "currency": "USD"
  }'
```

### 2. Enviar a aprobación (OPERADOR)

```bash
curl -X POST "http://localhost:8000/api/v1/transactions/{transaction_id}/submit" \
  -H "X-User-Role: OPERADOR"
```

### 3. Aprobar (APROBADOR)

```bash
curl -X POST "http://localhost:8000/api/v1/transactions/{transaction_id}/approve" \
  -H "X-User-Role: APROBADOR" \
  -H "X-User-Id: ap-001"
```

### 4. Ejecutar

```bash
curl -X POST "http://localhost:8000/api/v1/transactions/{transaction_id}/execute"
```

## Reglas de Negocio

1. Solo **OPERADOR** puede crear transacciones (estado inicial: DRAFT)
2. Solo **OPERADOR** puede enviar a aprobación (DRAFT → PENDING_APPROVAL)
3. Solo **APROBADOR** puede aprobar (PENDING_APPROVAL → APPROVED)
4. Solo **APROBADOR** puede rechazar (PENDING_APPROVAL → REJECTED)
5. Solo transacciones **APPROVED** pueden ejecutarse (→ EXECUTED)

## Despliegue en Render

### 1. Crear Web Service en Render

1. Ve a https://dashboard.render.com
2. Click en "New +" → "Web Service"
3. Conecta tu repositorio de GitHub

### 2. Configuración del servicio

```yaml
Name: fastapi-cap
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 3. Variables de entorno en Render

En la sección "Environment":

```
SECRET_KEY=tu-clave-super-secreta-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=postgresql://... (usa Internal Database URL de Render)
```

### 4. Deploy

Click en "Create Web Service" y espera a que se despliegue.

Tu API estará disponible en: `https://tu-servicio.onrender.com`

## Estructura de la Base de Datos

### Tabla: `transactions`

| Campo          | Tipo          | Descripción                                           |
| -------------- | ------------- | ----------------------------------------------------- |
| transaction_id | UUID          | ID único (PK)                                         |
| reference      | String        | Referencia única (ej: PAY-001, TRX-001)               |
| amount         | Numeric(18,2) | Monto de la transacción                               |
| currency       | String(3)     | Código de moneda (USD, EUR, etc.)                     |
| status         | Enum          | DRAFT, PENDING_APPROVAL, APPROVED, REJECTED, EXECUTED |
| created_by     | String        | ID del operador (op-001, op-002)                      |
| approved_by    | String        | ID del aprobador (ap-001, ap-002)                     |
| created_at     | DateTime      | Fecha de creación                                     |
| updated_at     | DateTime      | Última actualización                                  |

### Tabla: `usuarios`

| Campo           | Tipo    | Descripción               |
| --------------- | ------- | ------------------------- |
| id              | Integer | ID numérico (PK)          |
| user_id         | String  | ID único (op-001, ap-001) |
| nombre          | String  | Nombre completo           |
| email           | String  | Email único               |
| hashed_password | String  | Contraseña hasheada       |
| role            | Enum    | OPERADOR o APROBADOR      |

## Testing

Puedes probar la API directamente desde Swagger UI:

```
http://localhost:8000/docs
```

## Realizado

### Santiago Millan

## Notas

testO@example.com (operador)
testo1@example.com (operador)
adan@covalto.com (APROBADOR) - ap-001
dbonansea@covalto.com (APROBADOR) - ap-002
querys
select _ from transactions
select _ from usuarios

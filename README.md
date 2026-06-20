# Sistema de Soporte

Aplicacion web para gestionar tickets de soporte. El sistema permite iniciar sesion, crear tickets, consultar tickets segun el rol del usuario, actualizar estado y prioridad, eliminar tickets, invitar nuevos usuarios y recibir actualizaciones en tiempo real mediante eventos SSE.

## Tecnologias

- Backend: Python, Flask, Flask-SQLAlchemy, PyMySQL y Flasgger.
- Frontend: HTML, CSS y JavaScript.
- Base de datos: MySQL 8.
- Contenedores: Docker Compose.
- Administracion de base de datos: phpMyAdmin.

## Estructura del proyecto

```text
.
|-- backend/
|   |-- app.py
|   |-- config.py
|   |-- models.py
|   |-- controllers/
|   |-- services/
|   `-- swagger/
|-- frontend/
|   |-- index.html
|   |-- login.html
|   |-- register.html
|   |-- dashboard.html
|   |-- css/
|   `-- js/
|-- docker-compose.yml
|-- .env.example
`-- README.md
```

## Funcionalidades principales

- Inicio y cierre de sesion.
- Registro de usuarios por invitacion.
- Roles de usuario: `admin` y `cliente`.
- Creacion, listado, consulta, actualizacion y eliminacion de tickets.
- Los clientes solo ven sus propios tickets.
- Los administradores ven todos los tickets y pueden cambiar estado y prioridad.
- Eventos en tiempo real para cambios de tickets y actividad del sistema.
- Documentacion interactiva de la API con Swagger.

## Configuracion

Copia el archivo de ejemplo y ajusta las variables necesarias:

```bash
cp .env.example .env
```

Variables principales:

```env
APP_URL=http://localhost:5001
SECRET_KEY=replace-with-a-random-secret

DB_NAME=soporte_db
DB_USER=root
MYSQL_ROOT_PASSWORD=replace-with-a-strong-password
MYSQL_PORT=3307

BACKEND_PORT=5001
PHPMYADMIN_PORT=8080

MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-app-password
MAIL_USE_TLS=true
MAIL_SENDER=your-email@example.com
```

## Ejecucion con Docker

Levanta los servicios:

```bash
docker compose up --build
```

Servicios disponibles:

- Aplicacion: `http://localhost:5001`
- Swagger: `http://localhost:5001/docs/`
- phpMyAdmin: `http://localhost:8080`
- MySQL local: puerto `3307`

Al iniciar, la aplicacion crea automaticamente las tablas con `db.create_all()`, sincroniza columnas nuevas del modelo `Ticket` y crea usuarios iniciales si no existen.

## Usuarios iniciales

| Rol | Correo | Contrasena |
| --- | --- | --- |
| Admin | `admin@gmail.com` | `1234` |
| Cliente | `cliente@gmail.com` | `1234` |

## API principal

La API se expone bajo el prefijo `/api`.

| Metodo | Ruta | Descripcion |
| --- | --- | --- |
| `POST` | `/api/login` | Inicia sesion. |
| `GET` | `/api/session` | Consulta la sesion activa. |
| `POST` | `/api/logout` | Cierra sesion. |
| `POST` | `/api/invitations` | Crea una invitacion de usuario. Solo admin. |
| `GET` | `/api/invitations/<token>` | Consulta una invitacion valida. |
| `POST` | `/api/register` | Registra un usuario invitado. |
| `GET` | `/api/tickets` | Lista tickets visibles para el usuario. |
| `GET` | `/api/tickets/stream` | Stream SSE de eventos de tickets. |
| `GET` | `/api/tickets/<id>` | Obtiene un ticket por ID. |
| `POST` | `/api/tickets` | Crea un ticket. |
| `PUT` | `/api/tickets/<id>` | Actualiza un ticket. |
| `DELETE` | `/api/tickets/<id>` | Elimina un ticket. |

## Base de datos

La base de datos se llama `soporte_db` por defecto. El proyecto usa tres tablas principales:

### Tabla `usuario`

Guarda los usuarios que pueden iniciar sesion en el sistema.

| Campo | Tipo | Restricciones |
| --- | --- | --- |
| `id` | `INT` | Llave primaria, autoincremental |
| `nombre` | `VARCHAR(100)` | Opcional |
| `email` | `VARCHAR(100)` | Unico |
| `password` | `VARCHAR(200)` | Opcional |
| `rol` | `VARCHAR(50)` | Opcional |

### Tabla `ticket`

Guarda los tickets creados por los usuarios.

| Campo | Tipo | Restricciones |
| --- | --- | --- |
| `id` | `INT` | Llave primaria, autoincremental |
| `titulo` | `VARCHAR(200)` | Opcional |
| `descripcion` | `TEXT` | Opcional |
| `tipo_ticket` | `VARCHAR(100)` | Valor por defecto: `General` |
| `observacion` | `TEXT` | Opcional |
| `reportado_por` | `VARCHAR(100)` | Opcional |
| `area` | `VARCHAR(100)` | Opcional |
| `departamento` | `VARCHAR(100)` | Opcional |
| `prioridad` | `VARCHAR(50)` | Valor por defecto: `media` |
| `usuario_id` | `INT` | Llave foranea hacia `usuario.id` |
| `estado` | `VARCHAR(50)` | Valor por defecto: `pendiente` |
| `creado_en` | `DATETIME` | No nulo, valor por defecto: fecha actual |

### Tabla `invitacion_usuario`

Guarda invitaciones para registrar nuevos usuarios.

| Campo | Tipo | Restricciones |
| --- | --- | --- |
| `id` | `INT` | Llave primaria, autoincremental |
| `email` | `VARCHAR(100)` | No nulo |
| `rol` | `VARCHAR(50)` | No nulo, valor por defecto: `cliente` |
| `token` | `VARCHAR(120)` | No nulo, unico |
| `usada` | `BOOLEAN` | Valor por defecto: `false` |
| `creada_en` | `DATETIME` | No nulo |
| `expira_en` | `DATETIME` | No nulo |
| `usada_en` | `DATETIME` | Opcional |

## SQL exacto de la base de datos

Este script crea la base de datos y las tablas equivalentes a los modelos definidos en `backend/models.py`.

```sql
CREATE DATABASE IF NOT EXISTS soporte_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE soporte_db;

CREATE TABLE IF NOT EXISTS usuario (
  id INT NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(100) NULL,
  email VARCHAR(100) NULL,
  password VARCHAR(200) NULL,
  rol VARCHAR(50) NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_usuario_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ticket (
  id INT NOT NULL AUTO_INCREMENT,
  titulo VARCHAR(200) NULL,
  descripcion TEXT NULL,
  tipo_ticket VARCHAR(100) NULL DEFAULT 'General',
  observacion TEXT NULL,
  reportado_por VARCHAR(100) NULL,
  area VARCHAR(100) NULL,
  departamento VARCHAR(100) NULL,
  prioridad VARCHAR(50) NULL DEFAULT 'media',
  usuario_id INT NULL,
  estado VARCHAR(50) NULL DEFAULT 'pendiente',
  creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY ix_ticket_usuario_id (usuario_id),
  CONSTRAINT fk_ticket_usuario
    FOREIGN KEY (usuario_id)
    REFERENCES usuario (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS invitacion_usuario (
  id INT NOT NULL AUTO_INCREMENT,
  email VARCHAR(100) NOT NULL,
  rol VARCHAR(50) NOT NULL DEFAULT 'cliente',
  token VARCHAR(120) NOT NULL,
  usada BOOLEAN NULL DEFAULT false,
  creada_en DATETIME NOT NULL,
  expira_en DATETIME NOT NULL,
  usada_en DATETIME NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_invitacion_usuario_token (token)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

Datos iniciales que crea el seeder de la aplicacion:

```sql
INSERT INTO usuario (nombre, email, password, rol)
VALUES
  ('Admin', 'admin@gmail.com', '1234', 'admin'),
  ('Cliente', 'cliente@gmail.com', '1234', 'cliente');
```

## Notas de permisos

- `admin`: puede ver todos los tickets, crear invitaciones, cambiar estado y definir prioridad.
- `cliente`: puede crear tickets y ver o editar solo sus propios tickets.
- Estados validos: `pendiente`, `proceso`, `resuelto`.
- Prioridades validas: `baja`, `media`, `alta`, `critica`.

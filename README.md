# Sistema de Soporte

Aplicacion web para gestionar tickets de soporte. El sistema permite iniciar sesion, crear tickets, consultar tickets segun el rol del usuario, actualizar estado y prioridad, eliminar tickets, invitar nuevos usuarios y recibir actualizaciones en tiempo real mediante eventos SSE.

## Tecnologias

- Backend: Python, Flask, Flask-SQLAlchemy, PyMySQL y Flasgger.
- Frontend: HTML, CSS, JavaScript y Nginx para servir archivos estaticos.
- Base de datos: MySQL 8.
- Contenedores: Docker Compose con servicios separados para frontend, backend, MySQL y phpMyAdmin.
- Administracion de base de datos: phpMyAdmin.

## Patrones y arquitectura

El proyecto esta organizado con una arquitectura MVC por capas:

- Modelo: [`backend/models.py`](backend/models.py) define las entidades ORM `Usuario`, `Ticket`, `TicketHistorial` e `InvitacionUsuario`.
- Controlador: [`backend/controllers/`](backend/controllers/) define las rutas HTTP y coordina las respuestas de la API.
- Servicio: [`backend/services/`](backend/services/) concentra la logica de negocio, autenticacion, tickets, invitaciones, correo, eventos y sincronizacion de esquema.
- Vista/frontend: [`frontend/`](frontend/) contiene las paginas HTML, estilos CSS y JavaScript del navegador.

La infraestructura se separa por servicios con Docker Compose:

- `frontend`: contenedor Nginx que sirve la interfaz y reenvia `/api` al backend.
- `backend`: aplicacion Flask con las rutas REST, servicios de negocio, modelos y Swagger.
- `mysql`: base de datos MySQL 8.
- `phpmyadmin`: herramienta web para administrar la base de datos.

Esto permite explicar el sistema como una arquitectura de servicios contenerizados. La logica de negocio sigue siendo un backend monolitico organizado por capas, mientras que frontend, API y base de datos se ejecutan como servicios independientes.

Tambien se usa un enfoque orientado a eventos mediante Server-Sent Events (SSE). El backend publica eventos de creacion, actualizacion, eliminacion y actividad de tickets; el frontend los escucha con `EventSource` para actualizar la interfaz en tiempo real.

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
|   |-- Dockerfile
|   |-- nginx.conf
|   |-- index.html
|   |-- login.html
|   |-- register.html
|   |-- dashboard.html
|   |-- css/
|   `-- js/
|-- docker-compose.yml
|-- .env.example
|-- datyabase.sql
`-- README.md
```

## Funcionalidades principales

- Inicio y cierre de sesion.
- Registro de usuarios por invitacion.
- Roles de usuario: `admin` y `cliente`.
- Creacion, listado, consulta, actualizacion y eliminacion de tickets.
- Los clientes solo ven sus propios tickets.
- Los administradores ven todos los tickets y pueden cambiar estado y prioridad.
- Los administradores pueden asignar un responsable a un ticket mediante `asignado_a_id`.
- Historial auditable de creacion, actualizacion, cambios de estado, prioridad, asignacion y eliminacion de tickets.
- Eventos en tiempo real para cambios de tickets y actividad del sistema.
- Documentacion interactiva de la API con Swagger.

## Modulos desarrollados

- Autenticacion: login, consulta de sesion y logout.
- Perfil: actualizacion de datos personales, informacion adicional y foto de perfil.
- Invitaciones: creacion de invitaciones por administrador y registro de usuarios invitados.
- Tickets: CRUD completo para crear, listar, consultar, actualizar y eliminar tickets.
- Reportes: vista administrativa para revisar casos, prioridad y estado.
- Historial: registro auditable de acciones realizadas sobre cada ticket.
- Eventos: canal SSE para notificar actividad y cambios en tiempo real.
- Swagger: documentacion interactiva de endpoints y cuerpos JSON.

## Principios de POO aplicados

- Encapsulamiento: cada clase concentra una responsabilidad concreta, por ejemplo `TicketService` gestiona reglas de tickets y `AuthService` valida credenciales.
- Abstraccion: los controladores no manipulan directamente toda la logica de negocio; delegan en servicios.
- Composicion: controladores como `TicketController` reciben servicios (`TicketService`, `AuthService`) para coordinar operaciones.
- Clases y objetos: los modelos ORM (`Usuario`, `Ticket`, `TicketHistorial`, `InvitacionUsuario`) representan entidades del dominio.
- Metodos de instancia: funciones como `to_dict()`, `is_admin()`, `belongs_to()` e `is_available()` encapsulan comportamiento asociado a cada objeto.

## Analisis y mejoras aplicadas

El proyecto tenia una base funcional para mesa de ayuda, pero el esquema original estaba muy abierto: varios campos importantes permitian nulos, no existian marcas de auditoria para actualizaciones o cierres, las invitaciones no guardaban quien las habia creado y faltaban indices para consultas comunes.

Mejoras implementadas:

- Auditoria en `usuario` y `ticket` con `creado_en` y `actualizado_en`.
- Cierre trazable de tickets con `cerrado_en` cuando el estado pasa a `resuelto`.
- Asignacion opcional de responsable con `ticket.asignado_a_id`.
- Usuarios activables/desactivables mediante `usuario.activo`.
- Invitaciones auditables con `invitado_por_id` y `creada_ip`.
- Trazabilidad de tickets en `ticket_historial` para saber que cambio, quien lo hizo y cuando.
- Indices para busquedas por rol, usuario, estado, prioridad, fecha, responsable, correo de invitacion y expiracion.
- Restricciones SQL recomendadas para roles, estados y prioridades en el script `datyabase.sql`.
- Seeder actualizado para crear las contrasenas iniciales con hash de Werkzeug en instalaciones nuevas.

Mejoras escalables recomendadas para una siguiente etapa:

- Normalizar `departamento`, `area` y `tipo_ticket` en tablas propias si se administraran desde la interfaz.
- Agregar paginacion y filtros en `GET /api/tickets` cuando aumente el volumen de tickets.
- Migrar de `db.create_all()`/sincronizacion manual a Flask-Migrate/Alembic para cambios controlados por version.
- Reemplazar sesiones simples por autenticacion con expiracion fuerte si el sistema se expone fuera de red local.

## Configuracion

Copia el archivo de ejemplo y ajusta las variables necesarias:

```bash
cp .env.example .env
```

Variables principales:

```env
APP_URL=http://localhost:8081
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
MAIL_USE_SSL=false
MAIL_TIMEOUT=20
MAIL_SENDER=your-email@example.com
```

## Ejecucion con Docker

Levanta los servicios:

```bash
docker compose up --build
```

Servicios disponibles:

- Aplicacion frontend: `http://localhost:8081`
- Backend/API directa: `http://localhost:5001`
- Swagger: `http://localhost:5001/docs/`
- phpMyAdmin: `http://localhost:8080`
- MySQL local: puerto `3307`

Al iniciar, la aplicacion crea automaticamente las tablas con `db.create_all()`, sincroniza columnas e indices nuevos para tablas existentes y crea usuarios iniciales si no existen.

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
| `PUT` | `/api/profile` | Actualiza datos del perfil autenticado. |
| `POST` | `/api/invitations` | Crea una invitacion de usuario. Solo admin. |
| `GET` | `/api/invitations/<token>` | Consulta una invitacion valida. |
| `POST` | `/api/register` | Registra un usuario invitado. |
| `GET` | `/api/tickets` | Lista tickets visibles para el usuario. |
| `GET` | `/api/tickets/stream` | Stream SSE de eventos de tickets. |
| `GET` | `/api/tickets/<id>` | Obtiene un ticket por ID. |
| `GET` | `/api/tickets/<id>/history` | Lista el historial auditable del ticket. |
| `POST` | `/api/tickets` | Crea un ticket. |
| `PUT` | `/api/tickets/<id>` | Actualiza un ticket. |
| `DELETE` | `/api/tickets/<id>` | Elimina un ticket. |

En la actualizacion de tickets, un administrador tambien puede enviar `asignado_a_id` para asignar el caso a un usuario activo. Cuando `estado` cambia a `resuelto`, el backend guarda automaticamente `cerrado_en`; si el ticket vuelve a `pendiente` o `proceso`, el cierre se limpia.

## Base de datos

La base de datos se llama `soporte_db` por defecto. El proyecto usa cuatro tablas principales:

### Tabla `usuario`

Guarda los usuarios que pueden iniciar sesion en el sistema.

| Campo | Tipo | Restricciones |
| --- | --- | --- |
| `id` | `INT` | Llave primaria, autoincremental |
| `nombre` | `VARCHAR(100)` | Opcional |
| `email` | `VARCHAR(100)` | No nulo, unico |
| `password` | `VARCHAR(200)` | No nulo |
| `rol` | `VARCHAR(50)` | No nulo, valor por defecto: `cliente` |
| `activo` | `BOOLEAN` | No nulo, valor por defecto: `true` |
| `telefono` | `VARCHAR(30)` | Opcional |
| `cargo` | `VARCHAR(100)` | Opcional |
| `bio` | `TEXT` | Opcional |
| `foto_perfil` | `LONGTEXT` | Opcional, imagen codificada desde el frontend |
| `creado_en` | `DATETIME` | No nulo, valor por defecto: fecha actual |
| `actualizado_en` | `DATETIME` | No nulo, se actualiza automaticamente |

### Tabla `ticket`

Guarda los tickets creados por los usuarios.

| Campo | Tipo | Restricciones |
| --- | --- | --- |
| `id` | `INT` | Llave primaria, autoincremental |
| `titulo` | `VARCHAR(200)` | No nulo |
| `descripcion` | `TEXT` | No nulo |
| `tipo_ticket` | `VARCHAR(100)` | No nulo, valor por defecto: `General` |
| `observacion` | `TEXT` | Opcional |
| `reportado_por` | `VARCHAR(100)` | Opcional |
| `area` | `VARCHAR(100)` | No nulo |
| `departamento` | `VARCHAR(100)` | No nulo |
| `prioridad` | `VARCHAR(50)` | No nulo, valor por defecto: `media` |
| `usuario_id` | `INT` | No nulo, llave foranea hacia `usuario.id` |
| `asignado_a_id` | `INT` | Opcional, llave foranea hacia `usuario.id` |
| `estado` | `VARCHAR(50)` | No nulo, valor por defecto: `pendiente` |
| `creado_en` | `DATETIME` | No nulo, valor por defecto: fecha actual |
| `actualizado_en` | `DATETIME` | No nulo, se actualiza automaticamente |
| `cerrado_en` | `DATETIME` | Opcional, fecha de resolucion |

### Tabla `ticket_historial`

Guarda la trazabilidad de acciones realizadas sobre cada ticket.

| Campo | Tipo | Restricciones |
| --- | --- | --- |
| `id` | `INT` | Llave primaria, autoincremental |
| `ticket_id` | `INT` | Opcional, llave foranea hacia `ticket.id` |
| `usuario_id` | `INT` | Opcional, llave foranea hacia `usuario.id` |
| `accion` | `VARCHAR(50)` | No nulo. Valores: `creado`, `actualizado`, `eliminado` |
| `campo` | `VARCHAR(100)` | Opcional, campo modificado |
| `valor_anterior` | `TEXT` | Opcional |
| `valor_nuevo` | `TEXT` | Opcional |
| `detalle` | `JSON` | Opcional, datos adicionales de la accion |
| `creado_en` | `DATETIME` | No nulo, valor por defecto: fecha actual |

### Tabla `invitacion_usuario`

Guarda invitaciones para registrar nuevos usuarios.

| Campo | Tipo | Restricciones |
| --- | --- | --- |
| `id` | `INT` | Llave primaria, autoincremental |
| `email` | `VARCHAR(100)` | No nulo |
| `rol` | `VARCHAR(50)` | No nulo, valor por defecto: `cliente` |
| `token` | `VARCHAR(120)` | No nulo, unico |
| `usada` | `BOOLEAN` | No nulo, valor por defecto: `false` |
| `invitado_por_id` | `INT` | Opcional, llave foranea hacia `usuario.id` |
| `creada_en` | `DATETIME` | No nulo |
| `expira_en` | `DATETIME` | No nulo |
| `usada_en` | `DATETIME` | Opcional |
| `creada_ip` | `VARCHAR(45)` | Opcional |

## SQL exacto de la base de datos

El script actualizado esta en [`datyabase.sql`](datyabase.sql). Crea la base `soporte_db`, las cuatro tablas principales, llaves foraneas, restricciones, indices y usuarios iniciales con contrasenas hasheadas.

Datos iniciales que crea el seeder de la aplicacion:

```sql
INSERT INTO usuario (nombre, email, password, rol, activo)
VALUES
  ('Admin', 'admin@gmail.com', '<hash de 1234>', 'admin', true),
  ('Cliente', 'cliente@gmail.com', '<hash de 1234>', 'cliente', true);
```

## Notas de permisos

- `admin`: puede ver todos los tickets, crear invitaciones, cambiar estado y definir prioridad.
- `cliente`: puede crear tickets y ver o editar solo sus propios tickets.
- Estados validos: `pendiente`, `proceso`, `resuelto`.
- Prioridades validas: `baja`, `media`, `alta`, `critica`.

CREATE DATABASE IF NOT EXISTS soporte_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE soporte_db;

CREATE TABLE IF NOT EXISTS usuario (
  id INT NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(100) NULL,
  email VARCHAR(100) NOT NULL,
  password VARCHAR(200) NOT NULL,
  rol VARCHAR(50) NOT NULL DEFAULT 'cliente',
  activo BOOLEAN NOT NULL DEFAULT true,
  telefono VARCHAR(30) NULL,
  cargo VARCHAR(100) NULL,
  bio TEXT NULL,
  foto_perfil LONGTEXT NULL,
  creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_usuario_email (email),
  KEY ix_usuario_rol (rol),
  KEY ix_usuario_activo (activo),
  CONSTRAINT chk_usuario_rol CHECK (rol IN ('admin', 'cliente'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ticket (
  id INT NOT NULL AUTO_INCREMENT,
  titulo VARCHAR(200) NOT NULL,
  descripcion TEXT NOT NULL,
  tipo_ticket VARCHAR(100) NOT NULL DEFAULT 'General',
  observacion TEXT NULL,
  reportado_por VARCHAR(100) NULL,
  area VARCHAR(100) NOT NULL,
  departamento VARCHAR(100) NOT NULL,
  prioridad VARCHAR(50) NOT NULL DEFAULT 'media',
  usuario_id INT NOT NULL,
  asignado_a_id INT NULL,
  estado VARCHAR(50) NOT NULL DEFAULT 'pendiente',
  creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  cerrado_en DATETIME NULL,
  PRIMARY KEY (id),
  KEY ix_ticket_usuario_id (usuario_id),
  KEY ix_ticket_asignado_a_id (asignado_a_id),
  KEY ix_ticket_estado (estado),
  KEY ix_ticket_prioridad (prioridad),
  KEY ix_ticket_creado_en (creado_en),
  KEY ix_ticket_usuario_estado (usuario_id, estado),
  CONSTRAINT fk_ticket_usuario
    FOREIGN KEY (usuario_id)
    REFERENCES usuario (id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,
  CONSTRAINT fk_ticket_asignado_a
    FOREIGN KEY (asignado_a_id)
    REFERENCES usuario (id)
    ON UPDATE CASCADE
    ON DELETE SET NULL,
  CONSTRAINT chk_ticket_estado CHECK (estado IN ('pendiente', 'proceso', 'resuelto')),
  CONSTRAINT chk_ticket_prioridad CHECK (prioridad IN ('baja', 'media', 'alta', 'critica'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ticket_historial (
  id INT NOT NULL AUTO_INCREMENT,
  ticket_id INT NULL,
  usuario_id INT NULL,
  accion VARCHAR(50) NOT NULL,
  campo VARCHAR(100) NULL,
  valor_anterior TEXT NULL,
  valor_nuevo TEXT NULL,
  detalle JSON NULL,
  creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY ix_ticket_historial_ticket_id (ticket_id),
  KEY ix_ticket_historial_usuario_id (usuario_id),
  KEY ix_ticket_historial_accion (accion),
  KEY ix_ticket_historial_creado_en (creado_en),
  CONSTRAINT fk_ticket_historial_ticket
    FOREIGN KEY (ticket_id)
    REFERENCES ticket (id)
    ON UPDATE CASCADE
    ON DELETE SET NULL,
  CONSTRAINT fk_ticket_historial_usuario
    FOREIGN KEY (usuario_id)
    REFERENCES usuario (id)
    ON UPDATE CASCADE
    ON DELETE SET NULL,
  CONSTRAINT chk_ticket_historial_accion CHECK (accion IN ('creado', 'actualizado', 'eliminado'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS invitacion_usuario (
  id INT NOT NULL AUTO_INCREMENT,
  email VARCHAR(100) NOT NULL,
  rol VARCHAR(50) NOT NULL DEFAULT 'cliente',
  token VARCHAR(120) NOT NULL,
  usada BOOLEAN NOT NULL DEFAULT false,
  invitado_por_id INT NULL,
  creada_en DATETIME NOT NULL,
  expira_en DATETIME NOT NULL,
  usada_en DATETIME NULL,
  creada_ip VARCHAR(45) NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_invitacion_usuario_token (token),
  KEY ix_invitacion_usuario_email (email),
  KEY ix_invitacion_usuario_expira_en (expira_en),
  KEY ix_invitacion_usuario_invitado_por_id (invitado_por_id),
  CONSTRAINT fk_invitacion_usuario_invitado_por
    FOREIGN KEY (invitado_por_id)
    REFERENCES usuario (id)
    ON UPDATE CASCADE
    ON DELETE SET NULL,
  CONSTRAINT chk_invitacion_usuario_rol CHECK (rol IN ('admin', 'cliente'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO usuario (nombre, email, password, rol, activo)
VALUES
  (
    'Admin',
    'admin@gmail.com',
    'scrypt:32768:8:1$5PgnhBh9cgdSNZEl$c042d869b9cdb5fe34be765723f7000bf809583065e7a657d1eeedb7b7ce29ef423367533ae4c9a279bdc33d8cfe4d4bf24c659a77e0dfab69a2f2db0dcfb7f7',
    'admin',
    true
  ),
  (
    'Cliente',
    'cliente@gmail.com',
    'scrypt:32768:8:1$bNqshzTtITUPfpQQ$c3959857e189d1b008a20eac4ccee3d9bd29c83fcee927d876d5eabf24275f37a0fa99b77b23e6e9154d3f3a193917af61c4853d9a361f148624dbca899cde04',
    'cliente',
    true
  )
ON DUPLICATE KEY UPDATE
  nombre = VALUES(nombre),
  rol = VALUES(rol),
  activo = VALUES(activo);

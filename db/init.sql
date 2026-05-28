CREATE DATABASE IF NOT EXISTS soporte_db;
USE soporte_db;

-- TABLA USUARIO
CREATE TABLE usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    email VARCHAR(100),
    password VARCHAR(200),
    rol VARCHAR(50)
);

-- TABLA TICKET
CREATE TABLE ticket (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(200),
    descripcion TEXT,
    usuario_id INT,
    estado VARCHAR(50) DEFAULT 'pendiente',
    FOREIGN KEY (usuario_id) REFERENCES usuario(id)
);

-- USUARIO ADMIN
INSERT INTO usuario (nombre, email, password, rol)
VALUES ('Admin', 'admin@gmail.com', '1234', 'admin');

-- USUARIO CLIENTE
INSERT INTO usuario (nombre, email, password, rol)
VALUES ('Cliente', 'cliente@gmail.com', '1234', 'cliente');
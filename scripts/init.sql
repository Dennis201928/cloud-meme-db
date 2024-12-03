CREATE
DATABASE IF NOT EXISTS aplicación_web;
USE
aplicación_web;

CREATE TABLE memes
(
    id          CHAR(36) PRIMARY KEY,
    descripcion TEXT,
    ruta        TEXT,
    usuario     TEXT,
    cargada     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE etiquetas
(
    id        CHAR(36) PRIMARY KEY,
    meme_id   CHAR(36),
    etiqueta  TEXT,
    confianza FLOAT,
    FOREIGN KEY (meme_id) REFERENCES memes (id)
);
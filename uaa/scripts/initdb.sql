-- Schema and tables only (no seed data)
CREATE SCHEMA IF NOT EXISTS uaa;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS uaa.users (
    id                   BIGSERIAL PRIMARY KEY,
    username             VARCHAR(100) NOT NULL UNIQUE,
    password             BYTEA NOT NULL,
    userlocked           BOOLEAN NOT NULL DEFAULT FALSE,
    name_display         VARCHAR(100),
    data_permission_id   INTEGER,
    last_signon_datetime TIMESTAMPTZ,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS uaa.roles (
    id        BIGSERIAL PRIMARY KEY,
    code      VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255),
    last_update_username VARCHAR(50),
    last_update_datetime TIMESTAMPTZ DEFAULT NOW()
);

drop table if exists uaa.permissions cascade;

CREATE TABLE IF NOT EXISTS uaa.permissions (
    id        BIGSERIAL PRIMARY KEY,
    code      VARCHAR(100) NOT NULL,
    permission_type VARCHAR(50) NOT NULL,
    description VARCHAR(255),
    last_update_username VARCHAR(50),
    last_update_datetime TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(code, permission_type)
);

CREATE TABLE IF NOT EXISTS uaa.role_permissions (
    id            BIGSERIAL PRIMARY KEY,
    role_id       BIGINT NOT NULL,
    permission_id BIGINT NOT NULL,
    description   VARCHAR(255),
    last_update_username VARCHAR(50),
    last_update_datetime TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(role_id, permission_id)
);

CREATE TABLE IF NOT EXISTS uaa.user_roles (
    id            BIGSERIAL PRIMARY KEY,
    user_id       BIGINT NOT NULL,
    role_id       BIGINT NOT NULL,
    description   VARCHAR(255),
    last_update_username VARCHAR(50),
    last_update_datetime TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, role_id)
);

CREATE TABLE IF NOT EXISTS uaa.url_permissions (
    id            BIGSERIAL PRIMARY KEY,
    permission_id BIGINT NOT NULL,
    url           TEXT NOT NULL,
    method        VARCHAR(10) DEFAULT 'GET',
    type          VARCHAR(20) DEFAULT 'ROLE',
    last_update_datetime TIMESTAMPTZ DEFAULT NOW()
);

-- Page permissions: minimal mapping page <-> permission_id for UI/menu
CREATE TABLE IF NOT EXISTS uaa.page_permissions (
    id            BIGSERIAL PRIMARY KEY,
    permission_id BIGINT NOT NULL,
    page          TEXT NOT NULL,
    last_update_datetime TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(permission_id, page)
);

CREATE TABLE IF NOT EXISTS uaa.sets (
    id        BIGSERIAL PRIMARY KEY,
    setname   TEXT NOT NULL,
    services  TEXT NOT NULL,
    setcode   TEXT NOT NULL,
    UNIQUE(setname, services, setcode)
);

CREATE TABLE IF NOT EXISTS uaa.data_permissions (
    id              BIGSERIAL PRIMARY KEY,
    permission_id   BIGINT NOT NULL,
    set_id          BIGINT NOT NULL,
    last_update_datetime TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(permission_id, set_id)
);

CREATE TABLE IF NOT EXISTS uaa.datasets (
    id        BIGSERIAL PRIMARY KEY,
    set_id    BIGINT NOT NULL,
    tablename TEXT NOT NULL,
    colname   TEXT NOT NULL,
    colval    TEXT NOT NULL,
    UNIQUE(set_id, tablename, colname, colval)
);

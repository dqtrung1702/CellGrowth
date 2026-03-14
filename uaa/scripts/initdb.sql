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

-- Self-service access requests (role/data scope)
CREATE TABLE IF NOT EXISTS uaa.access_requests (
    id               BIGSERIAL PRIMARY KEY,
    requester_id     BIGINT NOT NULL,
    requester        TEXT,
    request_type     VARCHAR(20) NOT NULL, -- ROLE | DATA
    status           VARCHAR(20) NOT NULL DEFAULT 'SUBMITTED', -- SUBMITTED/APPROVED/REJECTED/CANCELLED/EXPIRED
    reason           TEXT,
    ttl_hours        INTEGER,
    approved_by      BIGINT,
    approved_at      TIMESTAMPTZ,
    rejected_reason  TEXT,
    apply_result_json JSONB,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_access_requests_requester ON uaa.access_requests(requester_id);
CREATE INDEX IF NOT EXISTS idx_access_requests_status ON uaa.access_requests(status);

CREATE TABLE IF NOT EXISTS uaa.access_request_items (
    id                  BIGSERIAL PRIMARY KEY,
    request_id          BIGINT NOT NULL,
    role_id             BIGINT,
    data_permission_id  BIGINT,
    set_id              BIGINT,
    note                TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(request_id, role_id, data_permission_id, set_id)
);

CREATE INDEX IF NOT EXISTS idx_access_request_items_req ON uaa.access_request_items(request_id);

CREATE TABLE IF NOT EXISTS uaa.access_request_logs (
    id          BIGSERIAL PRIMARY KEY,
    request_id  BIGINT NOT NULL,
    actor_id    BIGINT,
    action      VARCHAR(30), -- SUBMIT/APPROVE/REJECT/CANCEL/APPLY/EXPIRE
    note        TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_access_request_logs_req ON uaa.access_request_logs(request_id);

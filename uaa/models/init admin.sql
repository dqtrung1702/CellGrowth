CREATE SCHEMA IF NOT EXISTS uaa;

CREATE TABLE IF NOT EXISTS uaa.users (
    id                   BIGSERIAL PRIMARY KEY,
    username             VARCHAR(100) NOT NULL UNIQUE,
    password             BYTEA NOT NULL,              -- lưu bcrypt hash hoặc plaintext tùy bạn
    userlocked           BOOLEAN NOT NULL DEFAULT FALSE,
    name_display         VARCHAR(100),
    data_permission_id   INTEGER,
    last_signon_datetime TIMESTAMPTZ,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE EXTENSION IF NOT EXISTS pgcrypto;

INSERT INTO uaa.users (username, password, userlocked)
VALUES (
  'admin',
  crypt('admin', gen_salt('bf', 12))::bytea,
  FALSE
)
ON CONFLICT (username) DO NOTHING;

-- Roles
CREATE TABLE IF NOT EXISTS uaa.roles (
    id        BIGSERIAL PRIMARY KEY,
    code      VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255),
    last_update_username VARCHAR(50),
    last_update_datetime TIMESTAMPTZ DEFAULT NOW()
);

-- Permissions
CREATE TABLE IF NOT EXISTS uaa.permissions (
    id        BIGSERIAL PRIMARY KEY,
    code      VARCHAR(100) NOT NULL UNIQUE,
    permission_type VARCHAR(50) NOT NULL, -- 'ROLE', 'DATA', etc.
    description VARCHAR(255),
    last_update_username VARCHAR(50),
    last_update_datetime TIMESTAMPTZ DEFAULT NOW()
);

-- Role - Permission mapping
CREATE TABLE IF NOT EXISTS uaa.role_permissions (
    id            BIGSERIAL PRIMARY KEY,
    role_id       BIGINT NOT NULL REFERENCES uaa.roles(id) ON DELETE CASCADE,
    permission_id BIGINT NOT NULL REFERENCES uaa.permissions(id) ON DELETE CASCADE,
    description   VARCHAR(255),
    last_update_username VARCHAR(50),
    last_update_datetime TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(role_id, permission_id)
);

-- User - Role mapping
CREATE TABLE IF NOT EXISTS uaa.user_roles (
    id            BIGSERIAL PRIMARY KEY,
    user_id       BIGINT NOT NULL REFERENCES uaa.users(id) ON DELETE CASCADE,
    role_id       BIGINT NOT NULL REFERENCES uaa.roles(id) ON DELETE CASCADE,
    description   VARCHAR(255),
    last_update_username VARCHAR(50),
    last_update_datetime TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, role_id)
);

-- URL Permission list (optional)
CREATE TABLE IF NOT EXISTS uaa.url_permissions (
    id            BIGSERIAL PRIMARY KEY,
    permission_id BIGINT NOT NULL REFERENCES uaa.permissions(id) ON DELETE CASCADE,
    url           TEXT NOT NULL,
    method        VARCHAR(10) DEFAULT 'GET',
    type          VARCHAR(20) DEFAULT 'ROLE', -- ROLE / DATA / PAGE
    last_update_datetime TIMESTAMPTZ DEFAULT NOW()
);

-- seed an admin role/permission and map to admin user
INSERT INTO uaa.roles (code, description) VALUES ('Admin', 'Administrator') ON CONFLICT (code) DO NOTHING;
INSERT INTO uaa.permissions (code, permission_type, description)
VALUES ('ALL', 'ROLE', 'Full access') ON CONFLICT (code) DO NOTHING;

-- Data permission sets
CREATE TABLE IF NOT EXISTS uaa.sets (
    id        BIGSERIAL PRIMARY KEY,
    setname   TEXT NOT NULL,
    settbl    TEXT NOT NULL,
    setcol    TEXT NOT NULL,
    setval    TEXT NOT NULL,
    UNIQUE(setname, settbl, setcol, setval)
);

CREATE TABLE IF NOT EXISTS uaa.data_permissions (
    id              BIGSERIAL PRIMARY KEY,
    permission_id   BIGINT NOT NULL REFERENCES uaa.permissions(id) ON DELETE CASCADE,
    set_id          BIGINT NOT NULL REFERENCES uaa.sets(id) ON DELETE CASCADE,
    last_update_datetime TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(permission_id, set_id)
);

-- seed a DATA permission and an ALL dataset
INSERT INTO uaa.permissions (code, permission_type, description)
VALUES ('ALL_DATA', 'DATA', 'Full data access') ON CONFLICT (code) DO NOTHING;
INSERT INTO uaa.sets (setname, settbl, setcol, setval)
VALUES ('ALL', '*', '*', '*') ON CONFLICT (setname, settbl, setcol, setval) DO NOTHING;

DO $$
DECLARE
    rid BIGINT;
    pid BIGINT;
    pid_data BIGINT;
    uid BIGINT;
    upid BIGINT;
    dsid BIGINT;
BEGIN
    SELECT id INTO rid FROM uaa.roles WHERE code = 'Admin';
    SELECT id INTO pid FROM uaa.permissions WHERE code = 'ALL';
    SELECT id INTO pid_data FROM uaa.permissions WHERE code = 'ALL_DATA';
    SELECT id INTO uid FROM uaa.users WHERE username = 'admin';
    SELECT id INTO dsid FROM uaa.sets WHERE setname='ALL' AND settbl='*' AND setcol='*' AND setval='*';

    IF rid IS NOT NULL AND pid IS NOT NULL THEN
        INSERT INTO uaa.role_permissions (role_id, permission_id) VALUES (rid, pid)
        ON CONFLICT (role_id, permission_id) DO NOTHING;
    END IF;

    IF rid IS NOT NULL AND pid_data IS NOT NULL THEN
        INSERT INTO uaa.role_permissions (role_id, permission_id) VALUES (rid, pid_data)
        ON CONFLICT (role_id, permission_id) DO NOTHING;
    END IF;

    IF rid IS NOT NULL AND uid IS NOT NULL THEN
        INSERT INTO uaa.user_roles (user_id, role_id) VALUES (uid, rid)
        ON CONFLICT (user_id, role_id) DO NOTHING;
    END IF;

    IF pid IS NOT NULL THEN
        -- Khai báo đầy đủ các API (method, url) mà admin được phép gọi
        INSERT INTO uaa.url_permissions (permission_id, url, method, type)
        VALUES
            (pid, '/login', 'POST', 'ROLE'),
            (pid, '/register', 'POST', 'ROLE'),
            (pid, '/check_auth_ext', 'POST', 'ROLE'),
            (pid, '/getUserList', 'POST', 'ROLE'),
            (pid, '/getUserInfo', 'POST', 'ROLE'),
            (pid, '/updateUser', 'POST', 'ROLE'),
            (pid, '/updateUserRole', 'POST', 'ROLE'),
            (pid, '/getRoleList', 'POST', 'ROLE'),
            (pid, '/getRoleInfo', 'POST', 'ROLE'),
            (pid, '/addRole', 'POST', 'ROLE'),
            (pid, '/updateRole', 'POST', 'ROLE'),
            (pid, '/deleteRoleById', 'POST', 'ROLE'),
            (pid, '/getPermissionByRole', 'POST', 'ROLE'),
            (pid, '/getUserByRole', 'POST', 'ROLE'),
            (pid, '/getRoleByUser', 'POST', 'ROLE'),
            (pid, '/getPermissionList', 'POST', 'ROLE'),
            (pid, '/getPermissionInfo', 'POST', 'ROLE'),
            (pid, '/addPermission', 'POST', 'ROLE'),
            (pid, '/updatePermission', 'POST', 'ROLE'),
            (pid, '/deletePermissionById', 'POST', 'ROLE'),
            (pid, '/getURLbyPermission', 'POST', 'ROLE'),
            (pid, '/getURLbyPermissionList', 'POST', 'ROLE'),
            (pid, '/getRoleByPermission', 'POST', 'ROLE'),
            (pid, '/getDataPermissionList', 'POST', 'ROLE'),
            (pid, '/getRolePermissionList', 'POST', 'ROLE')
        ON CONFLICT DO NOTHING;

        IF pid_data IS NOT NULL AND dsid IS NOT NULL THEN
            INSERT INTO uaa.data_permissions (permission_id, set_id)
            VALUES (pid_data, dsid)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;
END$$;

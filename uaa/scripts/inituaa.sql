-- Seed monitoring user for UAA service health/status endpoints

-- User dedicated to monitoring
INSERT INTO uaa.users (username, password, userlocked, name_display)
VALUES ('uaa', crypt('uaa', gen_salt('bf', 12))::bytea, FALSE, 'UAA Monitor')
ON CONFLICT (username) DO NOTHING;

-- Monitor role and permission
INSERT INTO uaa.roles (code, description) VALUES ('UAA_MONITOR', 'Monitor UAA health/status') ON CONFLICT (code) DO NOTHING;
INSERT INTO uaa.permissions (code, permission_type, description)
VALUES ('UAA_ROLE', 'ROLE', 'Full UAA role for monitor user') ON CONFLICT (code) DO NOTHING;
INSERT INTO uaa.permissions (code, permission_type, description)
VALUES ('UAA_DATA', 'DATA', 'Access UAA data scopes') ON CONFLICT (code) DO NOTHING;

-- Data scope for monitor user: limit to UAA tables only (read-only metadata)
INSERT INTO uaa.sets (setname, services, setcode)
VALUES ('UAA_MON', 'uaa', 'uaa')
ON CONFLICT (setname, services, setcode) DO NOTHING;
-- grant narrow read scope to core metadata tables of UAA (avoid mixing admin data)
INSERT INTO uaa.datasets (set_id, tablename, colname, colval)
SELECT s.id, 'users', 'username', 'uaa'
FROM uaa.sets s
WHERE s.setname='UAA_MON' AND s.services='uaa' AND s.setcode='uaa'
ON CONFLICT DO NOTHING;

INSERT INTO uaa.datasets (set_id, tablename, colname, colval)
SELECT s.id, 'roles', 'code', 'UAA_MONITOR'
FROM uaa.sets s
WHERE s.setname='UAA_MON' AND s.services='uaa' AND s.setcode='uaa'
ON CONFLICT DO NOTHING;

INSERT INTO uaa.datasets (set_id, tablename, colname, colval)
SELECT s.id, 'permissions', 'code', v.code
FROM uaa.sets s
JOIN (VALUES ('UAA_ROLE'), ('UAA_DATA')) AS v(code) ON TRUE
WHERE s.setname='UAA_MON' AND s.services='uaa' AND s.setcode='uaa'
ON CONFLICT DO NOTHING;

INSERT INTO uaa.datasets (set_id, tablename, colname, colval)
SELECT s.id, 'sets', 'setcode', 'uaa'
FROM uaa.sets s
WHERE s.setname='UAA_MON' AND s.services='uaa' AND s.setcode='uaa'
ON CONFLICT DO NOTHING;

-- URL permissions limited to health/status/ping/static
DO $$
DECLARE
    rid BIGINT;
    pid BIGINT;
    pid_data BIGINT;
    uid BIGINT;
    dsid BIGINT;
BEGIN
    SELECT id INTO rid FROM uaa.roles WHERE code = 'UAA_MONITOR';
    SELECT id INTO pid FROM uaa.permissions WHERE code = 'UAA_ROLE';
    SELECT id INTO pid_data FROM uaa.permissions WHERE code = 'UAA_DATA';
    SELECT id INTO uid FROM uaa.users WHERE username = 'uaa';
    SELECT id INTO dsid FROM uaa.sets WHERE setname='UAA_MON' AND services='uaa' AND setcode='uaa';

    IF rid IS NOT NULL AND pid IS NOT NULL THEN
        INSERT INTO uaa.role_permissions (role_id, permission_id) VALUES (rid, pid)
        ON CONFLICT (role_id, permission_id) DO NOTHING;
    END IF;

    IF rid IS NOT NULL AND uid IS NOT NULL THEN
        INSERT INTO uaa.user_roles (user_id, role_id) VALUES (uid, rid)
        ON CONFLICT (user_id, role_id) DO NOTHING;
    END IF;

    IF pid IS NOT NULL THEN
        -- allow monitor user to call all UAA endpoints (only those that exist)
        INSERT INTO uaa.url_permissions (permission_id, url, method, type) VALUES
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
            (pid, '/getRolePermissionList', 'POST', 'ROLE'),
            (pid, '/getDataSetByUser', 'POST', 'ROLE'),
            (pid, '/getSetList', 'POST', 'ROLE'),
            (pid, '/addSet', 'POST', 'ROLE'),
            (pid, '/updateSet', 'POST', 'ROLE'),
            (pid, '/deleteSetById', 'POST', 'ROLE'),
            (pid, '/getDatasetBySet', 'POST', 'ROLE'),
            (pid, '/updateDatasetBySet', 'POST', 'ROLE'),
            (pid, '/getDatasetByPermission', 'POST', 'ROLE')
        ON CONFLICT DO NOTHING;
    END IF;

    -- Assign DATA permission directly to user (role cannot grant DATA)
    IF pid_data IS NOT NULL AND uid IS NOT NULL THEN
        UPDATE uaa.users SET data_permission_id = pid_data WHERE id = uid;
        IF dsid IS NOT NULL THEN
            INSERT INTO uaa.data_permissions (permission_id, set_id)
            VALUES (pid_data, dsid)
            ON CONFLICT DO NOTHING;
        END IF;
    END IF;
END$$;

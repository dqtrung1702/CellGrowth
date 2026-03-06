-- Seed superuser admin, base roles/permissions, URL permissions, and data scopes

-- Admin user
INSERT INTO uaa.users (username, password, userlocked)
VALUES ('admin', crypt('admin', gen_salt('bf', 12))::bytea, FALSE),
('uaa', crypt('uaa', gen_salt('bf', 12))::bytea, FALSE),
('trung', crypt('trung', gen_salt('bf', 12))::bytea, FALSE)
ON CONFLICT (username) DO NOTHING;

-- Core roles/permissions
INSERT INTO uaa.roles (code, description) 
VALUES 
('Admin', 'Administrator'),
('UAA', 'UAA'),
('PROFILE', 'PROFILE') 
ON CONFLICT (code) DO NOTHING;
INSERT INTO uaa.permissions (code, permission_type, description)
VALUES 
('ALL_ROLE', 'ROLE', 'Full access'),
('UAA', 'ROLE', 'uaa access'),
('FULL_DATA', 'DATA', 'Full data access'),
('UAA_DATA', 'DATA', 'Scope for UAA user')
ON CONFLICT (code, permission_type) DO NOTHING;

-- Data scopes
INSERT INTO uaa.sets (setname, services, setcode)
VALUES 
('ALL', '*', '*'),
('UAA', 'UAA', 'UAA'),
('PERSON', 'PERSON', 'PERSON')
ON CONFLICT (setname, services, setcode) DO NOTHING;

INSERT INTO uaa.datasets (set_id, tablename, colname, colval)
WITH DT AS (
    SELECT 'UAA' AS SETCODE, 'USERS' AS TABLENAME, 'USERNAME' AS COLNAME, '*' AS COLVAL
    UNION ALL
    SELECT 'UAA', 'ROLES', 'CODE', '*'
    UNION ALL
    SELECT 'UAA', 'PERMISSIONS', 'CODE', '*'
    UNION ALL
    SELECT 'UAA', 'SETS', 'SETCODE', '*'
    union all
    SELECT 'ALL', '*', '*', '*'
    UNION ALL
    SELECT 'PERSON', 'PERSON', 'CODE', '*'
)
SELECT s.id, DT.tablename, DT.colname, DT.colval
FROM uaa.sets s
join DT ON s.setcode = DT.SETCODE
ON CONFLICT DO NOTHING;


DO $$
DECLARE
    rid BIGINT;
    pid BIGINT;
    pid_data BIGINT;
    uid BIGINT;
    dsid BIGINT;
BEGIN
    SELECT id INTO rid FROM uaa.roles WHERE code = 'Admin';
    SELECT id INTO pid FROM uaa.permissions WHERE code = 'ALL_ROLE' AND permission_type = 'ROLE';
    SELECT id INTO pid_data FROM uaa.permissions WHERE code = 'FULL_DATA';
    SELECT id INTO uid FROM uaa.users WHERE username = 'admin';
    SELECT id INTO dsid FROM uaa.sets WHERE setname='ALL' AND services='*' AND setcode='*';

    IF rid IS NOT NULL AND pid IS NOT NULL THEN
        INSERT INTO uaa.role_permissions (role_id, permission_id) VALUES (rid, pid)
        ON CONFLICT (role_id, permission_id) DO NOTHING;
        -- INSERT INTO uaa.page_permissions (permission_id, page) 
        -- VALUES 
        -- (pid, '/home'),
        -- (pid, '/Role'),
        -- (pid, '/Permission'),
        -- (pid, '/User'),
        -- (pid, '/datasets'),
        -- (pid, '/person')
        -- ON CONFLICT (permission_id, page) DO NOTHING;
    END IF;

    IF rid IS NOT NULL AND uid IS NOT NULL THEN
        INSERT INTO uaa.user_roles (user_id, role_id) VALUES (uid, rid)
        ON CONFLICT (user_id, role_id) DO NOTHING;
    END IF;

    IF pid IS NOT NULL THEN
        INSERT INTO uaa.url_permissions (permission_id, url, method, type) VALUES
            (pid, '/login', 'POST', 'ROLE'),
            (pid, '/register', 'POST', 'ROLE'),
            (pid, '/check_auth_ext', 'POST', 'ROLE'),
            -- API endpoints
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
            (pid, '/getPageByUser', 'POST', 'ROLE'),
            (pid, '/getDatasetByPermission', 'POST', 'ROLE')
        ON CONFLICT DO NOTHING;

        -- Page mapping for menu visibility
        INSERT INTO uaa.page_permissions (permission_id, page) VALUES
            (pid, '/home'),
            (pid, '/Role'),
            (pid, '/Permission'),
            (pid, '/User'),
            (pid, '/datasets'),
            (pid, '/person')
        ON CONFLICT DO NOTHING;

        IF pid_data IS NOT NULL AND dsid IS NOT NULL THEN
            INSERT INTO uaa.data_permissions (permission_id, set_id)
            VALUES (pid_data, dsid)
            ON CONFLICT DO NOTHING;
        END IF;
        -- assign DATA permission directly to admin user
        IF pid_data IS NOT NULL AND uid IS NOT NULL THEN
            UPDATE uaa.users SET data_permission_id = pid_data WHERE id = uid;
        END IF;
    END IF;
END$$;

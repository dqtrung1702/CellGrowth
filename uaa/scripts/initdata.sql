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
('UAA', 'UAA')
ON CONFLICT (code) DO NOTHING;
INSERT INTO uaa.permissions (id,code, permission_type, description)
VALUES 
(3,'ALL_ROLE', 'ROLE', 'Full access'),
(4,'UAA', 'ROLE', 'uaa access'),
(5,'FULL_DATA', 'DATA', 'Full data access'),
(6,'UAA_DATA', 'DATA', 'Scope for UAA user')
ON CONFLICT (code, permission_type) DO NOTHING;

-- Data scopes
INSERT INTO uaa.sets (setname, services, setcode)
VALUES 
('ALL', '*', 'ALL'),
('UAA', 'UAA', 'UAA')
ON CONFLICT (setname, services, setcode) DO NOTHING;

INSERT INTO uaa.datasets (set_id, tablename, colname, colval)
WITH DT AS (
    SELECT 'UAA' AS SETCODE, 'USERS' AS TABLENAME, 'USERNAME' AS COLNAME, '*' AS COLVAL
    UNION ALL
    SELECT 'UAA', 'ROLES', 'CODE', 'UAA'
    UNION ALL
    SELECT 'UAA', 'PERMISSIONS', 'CODE', '*'
    UNION ALL
    SELECT 'UAA', 'SETS', 'SETCODE', '*'
    union all
    SELECT 'ALL', '*', '*', '*'
)
SELECT s.id, DT.tablename, DT.colname, DT.colval
FROM uaa.sets s
join DT ON s.setcode = DT.SETCODE
ON CONFLICT DO NOTHING;


DO $$
DECLARE
    rid BIGINT;
    rid_uaa BIGINT;
    pid BIGINT;
    pid_uaa BIGINT;
    pid_data BIGINT;
    pid_data_uaa BIGINT;
    uid BIGINT;
    uid_uaa BIGINT;
    dsid BIGINT;
    dsid_uaa BIGINT;
BEGIN
    SELECT id INTO rid FROM uaa.roles WHERE code = 'Admin';
    SELECT id INTO rid_uaa FROM uaa.roles WHERE code = 'UAA';
    SELECT id INTO pid FROM uaa.permissions WHERE code = 'ALL_ROLE' AND permission_type = 'ROLE';
    SELECT id INTO pid_uaa FROM uaa.permissions WHERE code = 'UAA' AND permission_type = 'ROLE';
    SELECT id INTO pid_data FROM uaa.permissions WHERE code = 'FULL_DATA';
    SELECT id INTO pid_data_uaa FROM uaa.permissions WHERE code = 'UAA_DATA';
    SELECT id INTO uid FROM uaa.users WHERE username = 'admin';
    SELECT id INTO uid_uaa FROM uaa.users WHERE username = 'uaa';
    SELECT id INTO dsid FROM uaa.sets WHERE setname='ALL';
    SELECT id INTO dsid_uaa FROM uaa.sets WHERE setname='UAA';

    IF rid IS NOT NULL AND pid IS NOT NULL THEN
        INSERT INTO uaa.role_permissions (role_id, permission_id) VALUES (rid, pid)
        ON CONFLICT (role_id, permission_id) DO NOTHING;
    END IF;
    IF rid_uaa IS NOT NULL AND pid_uaa IS NOT NULL THEN
        INSERT INTO uaa.role_permissions (role_id, permission_id) VALUES (rid_uaa, pid_uaa)
        ON CONFLICT (role_id, permission_id) DO NOTHING;
    END IF;

    IF rid IS NOT NULL AND uid IS NOT NULL THEN
        INSERT INTO uaa.user_roles (user_id, role_id) VALUES (uid, rid)
        ON CONFLICT (user_id, role_id) DO NOTHING;
    END IF;
    IF rid_uaa IS NOT NULL AND uid_uaa IS NOT NULL THEN
        INSERT INTO uaa.user_roles (user_id, role_id) VALUES (uid_uaa, rid_uaa)
        ON CONFLICT (user_id, role_id) DO NOTHING;
    END IF;

    IF pid IS NOT NULL OR pid_uaa IS NOT NULL THEN
        -- Grant the same URL set to both ALL_ROLE and UAA permissions
        INSERT INTO uaa.url_permissions (permission_id, url, method, type)
        SELECT perm_id, url, method, type
        FROM (VALUES (pid), (pid_uaa)) AS perms(perm_id)
        JOIN (VALUES
            ('/login', 'POST', 'ROLE'),
            ('/register', 'POST', 'ROLE'),
            ('/check_auth_ext', 'POST', 'ROLE'),
            -- API endpoints
            ('/getUserList', 'POST', 'ROLE'),
            ('/getUserInfo', 'POST', 'ROLE'),
            ('/updateUser', 'POST', 'ROLE'),
            ('/updateUserRole', 'POST', 'ROLE'),
            ('/getRoleList', 'POST', 'ROLE'),
            ('/getRoleInfo', 'POST', 'ROLE'),
            ('/addRole', 'POST', 'ROLE'),
            ('/updateRole', 'POST', 'ROLE'),
            ('/deleteRoleById', 'POST', 'ROLE'),
            ('/getPermissionByRole', 'POST', 'ROLE'),
            ('/getUserByRole', 'POST', 'ROLE'),
            ('/getRoleByUser', 'POST', 'ROLE'),
            ('/getPermissionList', 'POST', 'ROLE'),
            ('/getPermissionInfo', 'POST', 'ROLE'),
            ('/addPermission', 'POST', 'ROLE'),
            ('/updatePermission', 'POST', 'ROLE'),
            ('/deletePermissionById', 'POST', 'ROLE'),
            ('/getURLbyPermission', 'POST', 'ROLE'),
            ('/getURLbyPermissionList', 'POST', 'ROLE'),
            ('/getRoleByPermission', 'POST', 'ROLE'),
            ('/getDataPermissionList', 'POST', 'ROLE'),
            ('/getRolePermissionList', 'POST', 'ROLE'),
            ('/getDataSetByUser', 'POST', 'ROLE'),
            ('/getSetList', 'POST', 'ROLE'),
            ('/addSet', 'POST', 'ROLE'),
            ('/updateSet', 'POST', 'ROLE'),
            ('/deleteSetById', 'POST', 'ROLE'),
            ('/getDatasetBySet', 'POST', 'ROLE'),
            ('/updateDatasetBySet', 'POST', 'ROLE'),
            ('/getPageByUser', 'POST', 'ROLE'),
            ('/getDatasetByPermission', 'POST', 'ROLE'),
            ('/access_requests', 'POST', 'ROLE'),
            ('/access_requests', 'GET', 'ROLE'),
            ('/access_requests/%', 'GET', 'ROLE'),
            ('/access_requests/%/approve', 'POST', 'ROLE'),
            ('/access_requests/%/reject', 'POST', 'ROLE'),
            ('/access_requests/%/cancel', 'POST', 'ROLE')
        ) AS urls(url, method, type) ON TRUE
        WHERE perm_id IS NOT NULL
        ON CONFLICT DO NOTHING;

        -- Page mapping for menu visibility (both ALL_ROLE and UAA)
        INSERT INTO uaa.page_permissions (permission_id, page)
        SELECT perm_id, page
        FROM (VALUES (pid)) AS perms(perm_id)
        JOIN (VALUES
            ('/home'),
            ('/Role'),
            ('/Permission'),
            ('/User'),
            ('/datasets'),
            ('/access_requests')
        ) AS pages(page) ON TRUE
        WHERE perm_id IS NOT NULL
        ON CONFLICT DO NOTHING;
        INSERT INTO uaa.page_permissions (permission_id, page)
        SELECT perm_id, page
        FROM (VALUES (pid_uaa)) AS perms(perm_id)
        JOIN (VALUES
            ('/home'),
            ('/Role'),
            ('/Permission'),
            ('/User'),
            ('/datasets'),
            ('/access_requests')
        ) AS pages(page) ON TRUE
        WHERE perm_id IS NOT NULL
        ON CONFLICT DO NOTHING;

        -- Data scopes: FULL_DATA -> ALL, UAA_DATA -> UAA-only tables
        IF (pid_data IS NOT NULL OR pid_data_uaa IS NOT NULL) THEN
            INSERT INTO uaa.data_permissions (permission_id, set_id)
            SELECT perm_id, set_id
            FROM (VALUES (pid_data, dsid), (pid_data_uaa, dsid_uaa)) AS dp(perm_id, set_id)
            WHERE perm_id IS NOT NULL AND set_id IS NOT NULL
            ON CONFLICT DO NOTHING;
        END IF;
        -- assign DATA permission directly to admin user
        IF pid_data IS NOT NULL AND uid IS NOT NULL THEN
            UPDATE uaa.users SET data_permission_id = pid_data WHERE id = uid;
        END IF;
        IF pid_data_uaa IS NOT NULL AND uid_uaa IS NOT NULL THEN
            UPDATE uaa.users SET data_permission_id = pid_data_uaa WHERE id = uid_uaa;
        END IF;
    END IF;
END$$;

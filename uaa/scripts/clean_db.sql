-- Truncate all UAA tables (order matters to avoid FK-like dependencies)
TRUNCATE TABLE
  uaa.user_roles,
  uaa.role_permissions,
  uaa.page_permissions,
  uaa.url_permissions,
  uaa.data_permissions,
  uaa.datasets,
  uaa.users,
  uaa.roles,
  uaa.permissions,
  uaa.sets
RESTART IDENTITY;

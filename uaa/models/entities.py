from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, LargeBinary, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .orm import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "uaa"}

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(LargeBinary, nullable=False)
    userlocked = Column(Boolean, default=False, nullable=False)
    name_display = Column(String(100))
    data_permission_id = Column(Integer, ForeignKey("uaa.permissions.id"))
    last_signon_datetime = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    data_permission = relationship("Permission", back_populates="users", foreign_keys=[data_permission_id])
    identities = relationship("UserIdentity", back_populates="user", cascade="all, delete-orphan")


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = {"schema": "uaa"}

    id = Column(Integer, primary_key=True)
    code = Column(String(100), unique=True, nullable=False)
    description = Column(String(255))
    last_update_username = Column(String(50))
    last_update_datetime = Column(DateTime, default=datetime.utcnow)

    permission_links = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
    user_links = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")


class Permission(Base):
    __tablename__ = "permissions"
    __table_args__ = {"schema": "uaa"}

    id = Column(Integer, primary_key=True)
    code = Column(String(100), nullable=False)
    permission_type = Column(String(50), nullable=False)
    description = Column(String(255))
    last_update_username = Column(String(50))
    last_update_datetime = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="data_permission")
    role_links = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")
    url_permissions = relationship("UrlPermission", back_populates="permission", cascade="all, delete-orphan")
    page_permissions = relationship("PagePermission", back_populates="permission", cascade="all, delete-orphan")
    data_permissions = relationship("DataPermission", back_populates="permission", cascade="all, delete-orphan")


class RolePermission(Base):
    __tablename__ = "role_permissions"
    __table_args__ = {"schema": "uaa"}

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey("uaa.roles.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("uaa.permissions.id"), nullable=False)
    description = Column(String(255))
    last_update_username = Column(String(50))
    last_update_datetime = Column(DateTime, default=datetime.utcnow)

    role = relationship("Role", back_populates="permission_links")
    permission = relationship("Permission", back_populates="role_links")


class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = {"schema": "uaa"}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("uaa.users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("uaa.roles.id"), nullable=False)
    description = Column(String(255))
    last_update_username = Column(String(50))
    last_update_datetime = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="user_links")


class UrlPermission(Base):
    __tablename__ = "url_permissions"
    __table_args__ = {"schema": "uaa"}

    id = Column(Integer, primary_key=True)
    permission_id = Column(Integer, ForeignKey("uaa.permissions.id"), nullable=False)
    url = Column(String, nullable=False)
    method = Column(String(10))
    type = Column(String(20))
    last_update_datetime = Column(DateTime, default=datetime.utcnow)

    permission = relationship("Permission", back_populates="url_permissions")


class PagePermission(Base):
    __tablename__ = "page_permissions"
    __table_args__ = {"schema": "uaa"}

    id = Column(Integer, primary_key=True)
    permission_id = Column(Integer, ForeignKey("uaa.permissions.id"), nullable=False)
    page = Column(String, nullable=False)
    last_update_datetime = Column(DateTime, default=datetime.utcnow)

    permission = relationship("Permission", back_populates="page_permissions")


class Set(Base):
    __tablename__ = "sets"
    __table_args__ = {"schema": "uaa"}

    id = Column(Integer, primary_key=True)
    setname = Column(String, nullable=False)
    services = Column(String, nullable=False)
    setcode = Column(String, nullable=False)

    data_permissions = relationship("DataPermission", back_populates="set", cascade="all, delete-orphan")
    datasets = relationship("Dataset", back_populates="set", cascade="all, delete-orphan")


class DataPermission(Base):
    __tablename__ = "data_permissions"
    __table_args__ = {"schema": "uaa"}

    id = Column(Integer, primary_key=True)
    permission_id = Column(Integer, ForeignKey("uaa.permissions.id"), nullable=False)
    set_id = Column(Integer, ForeignKey("uaa.sets.id"), nullable=False)
    last_update_datetime = Column(DateTime, default=datetime.utcnow)

    permission = relationship("Permission", back_populates="data_permissions")
    set = relationship("Set", back_populates="data_permissions")


class Dataset(Base):
    __tablename__ = "datasets"
    __table_args__ = {"schema": "uaa"}

    id = Column(Integer, primary_key=True)
    set_id = Column(Integer, ForeignKey("uaa.sets.id"), nullable=False)
    tablename = Column(String, nullable=False)
    colname = Column(String, nullable=False)
    colval = Column(String, nullable=False)

    set = relationship("Set", back_populates="datasets")


class AccessRequest(Base):
    __tablename__ = "access_requests"
    __table_args__ = {"schema": "uaa"}

    id = Column(Integer, primary_key=True)
    requester_id = Column(Integer, ForeignKey("uaa.users.id"), nullable=False)
    requester = Column(String)
    request_type = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default="SUBMITTED")
    reason = Column(String)
    ttl_hours = Column(Integer)
    approved_by = Column(Integer)
    approved_at = Column(DateTime)
    rejected_reason = Column(String)
    apply_result_json = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    requester_user = relationship("User")
    items = relationship("AccessRequestItem", back_populates="request", cascade="all, delete-orphan")
    logs = relationship("AccessRequestLog", back_populates="request", cascade="all, delete-orphan", order_by="AccessRequestLog.created_at")


class AccessRequestItem(Base):
    __tablename__ = "access_request_items"
    __table_args__ = {"schema": "uaa"}

    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey("uaa.access_requests.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("uaa.roles.id"))
    data_permission_id = Column(Integer, ForeignKey("uaa.permissions.id"))
    set_id = Column(Integer, ForeignKey("uaa.sets.id"))
    note = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    request = relationship("AccessRequest", back_populates="items")
    role = relationship("Role")
    data_permission = relationship("Permission")
    set = relationship("Set")


class AccessRequestLog(Base):
    __tablename__ = "access_request_logs"
    __table_args__ = {"schema": "uaa"}

    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey("uaa.access_requests.id"), nullable=False)
    actor_id = Column(Integer, ForeignKey("uaa.users.id"))
    action = Column(String(30))
    note = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    request = relationship("AccessRequest", back_populates="logs")
    actor = relationship("User")


class UserIdentity(Base):
    __tablename__ = "user_identities"
    __table_args__ = {"schema": "uaa"}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("uaa.users.id"), nullable=False)
    provider = Column(String(30), nullable=False)
    external_id = Column(String(255), nullable=False)
    email = Column(String(255))
    display_name = Column(String(255))
    avatar_url = Column(String)
    tokens_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="identities")


class UserTOTP(Base):
    __tablename__ = "user_totp"
    __table_args__ = {"schema": "uaa"}

    user_id = Column(Integer, ForeignKey("uaa.users.id"), primary_key=True)
    secret_base32 = Column(String(64), nullable=False)
    confirmed = Column(Boolean, default=False, nullable=False)
    backup_codes_json = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User")


class SocialProvider(Base):
    __tablename__ = "social_providers"
    __table_args__ = {"schema": "uaa"}

    id = Column(Integer, primary_key=True)
    provider = Column(String(32), unique=True, nullable=False)
    client_id = Column(String, nullable=False)
    client_secret_enc = Column(String, nullable=False)
    redirect_uri = Column(String, nullable=False)
    scopes = Column(String)  # space-separated
    enabled = Column(Boolean, default=True, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_by = Column(String(64))

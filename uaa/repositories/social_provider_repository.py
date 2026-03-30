from typing import Optional, Dict, List

from .orm_base import OrmRepo
from models.entities import SocialProvider


class SocialProviderRepository(OrmRepo):
    def get_by_provider(self, provider: str) -> Optional[Dict]:
        if not provider:
            return None
        with self.session() as session:
            row = session.query(SocialProvider).filter(SocialProvider.provider == provider).one_or_none()
            return dict(
                id=row.id,
                provider=row.provider,
                client_id=row.client_id,
                client_secret_enc=row.client_secret_enc,
                redirect_uri=row.redirect_uri,
                scopes=row.scopes,
                enabled=row.enabled,
                updated_at=row.updated_at,
                updated_by=row.updated_by,
            ) if row else None

    def list_enabled(self) -> List[Dict]:
        with self.session() as session:
            rows = session.query(SocialProvider).filter(SocialProvider.enabled.is_(True)).all()
            return [
                dict(
                    id=r.id,
                    provider=r.provider,
                    client_id=r.client_id,
                    client_secret_enc=r.client_secret_enc,
                    redirect_uri=r.redirect_uri,
                    scopes=r.scopes,
                    enabled=r.enabled,
                    updated_at=r.updated_at,
                    updated_by=r.updated_by,
                )
                for r in rows
            ]

    def upsert(self, provider: str, client_id: str, client_secret_enc: str, redirect_uri: str, scopes: str, enabled: bool, updated_by: str):
        with self.session() as session:
            row = session.query(SocialProvider).filter(SocialProvider.provider == provider).one_or_none()
            if not row:
                row = SocialProvider(provider=provider)
                session.add(row)
            row.client_id = client_id
            row.client_secret_enc = client_secret_enc
            row.redirect_uri = redirect_uri
            row.scopes = scopes
            row.enabled = enabled
            row.updated_by = updated_by
            return row.id

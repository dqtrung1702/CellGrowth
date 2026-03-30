from typing import Optional

from .orm_base import OrmRepo
from models.entities import UserIdentity


class UserIdentityRepository(OrmRepo):
    def find_by_provider_external(self, provider: str, external_id: str) -> Optional[dict]:
        if not provider or not external_id:
            return None
        with self.session() as session:
            row = (
                session.query(UserIdentity)
                .filter(UserIdentity.provider == provider, UserIdentity.external_id == external_id)
                .one_or_none()
            )
            return dict(
                id=row.id,
                user_id=row.user_id,
                provider=row.provider,
                external_id=row.external_id,
                email=row.email,
                display_name=row.display_name,
                avatar_url=row.avatar_url,
                tokens_json=row.tokens_json,
            ) if row else None

    def create_identity(self, user_id: int, provider: str, external_id: str, email: str, display_name: str, avatar_url: str, tokens_json):
        with self.session() as session:
            obj = UserIdentity(
                user_id=user_id,
                provider=provider,
                external_id=external_id,
                email=email,
                display_name=display_name,
                avatar_url=avatar_url,
                tokens_json=tokens_json,
            )
            session.add(obj)
            session.flush()
            return obj.id

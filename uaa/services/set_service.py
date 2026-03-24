from typing import List, Optional

from repositories.set_repository import SetRepository
from repositories.interfaces import SetRepoProtocol
from utils.data_scope import data_scope_filters
from models.orm import SessionLocal
from schemas.response import ResponseEnvelope
from utils.query_builder import QueryBuilder
from models.entities import Set


class SetService:
    def __init__(self, set_repo: Optional[SetRepoProtocol] = None):
        self.set_repo: SetRepoProtocol = set_repo or SetRepository()

    def list_sets(self, requester_id: Optional[int], setname: Optional[str], services: Optional[str], setcode: Optional[str]):
        scope_sql, scope_params = data_scope_filters(SessionLocal, requester_id, table_name="sets")
        qb = QueryBuilder(model=Set)
        qb.add_ilike("setname", setname).add_ilike("services", services).add_ilike("setcode", setcode).add_raw(scope_sql, scope_params or [])
        rows = self.set_repo.list_sets(qb.filters())
        return ResponseEnvelope(status="OK", data=rows)

    def add_set(self, payload: dict):
        try:
            set_id = self.set_repo.insert_set(payload)
            return ResponseEnvelope(status="OK", data={"SetId": set_id})
        except ValueError as e:
            return ResponseEnvelope(status="FAIL", message=str(e))
        except Exception as e:
            return ResponseEnvelope(status="FAIL", message=str(e))

    def update_set(self, set_id: int, payload: dict):
        try:
            self.set_repo.update_set(set_id, payload)
            return ResponseEnvelope(status="OK")
        except ValueError as e:
            return ResponseEnvelope(status="FAIL", message=str(e))
        except Exception as e:
            return ResponseEnvelope(status="FAIL", message=str(e))

    def delete_set(self, sid: int):
        self.set_repo.delete_set(sid)
        return ResponseEnvelope(status="OK")

    def dataset_by_set(self, requester_id: Optional[int], sid: int):
        scope_sql, scope_params = data_scope_filters(SessionLocal, requester_id, table_name="sets")
        if scope_sql:
            # quick check with ORM
            sql, bind = self.set_repo._bind_sql(f"SELECT 1 FROM sets WHERE id=%s AND {scope_sql};", [sid] + (scope_params or []))
            from sqlalchemy import text

            with self.set_repo.session() as session:
                ok = session.execute(text(sql), bind).first()
            if not ok:
                return ResponseEnvelope(status="FAIL", message="Access denied")

        rows = self.set_repo.list_dataset_by_set(sid)
        return ResponseEnvelope(status="OK", data=rows)

    def update_dataset_by_set(self, sid: int, items: List[dict]):
        try:
            self.set_repo.replace_dataset_for_set(sid, items)
            return ResponseEnvelope(status="OK", data={"SetId": sid, "Items": len(items)})
        except Exception as e:
            return ResponseEnvelope(status="FAIL", message=str(e))

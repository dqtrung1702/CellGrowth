from typing import List

from sqlalchemy import text

from .orm_base import OrmRepo
from models.entities import Set, Dataset
from sqlalchemy import func


class SetRepository(OrmRepo):
    def ensure_set(self, payload, session):
        setname = (payload.get("setname") or payload.get("SetName") or payload.get("name") or "").strip()
        services = (
            payload.get("services")
            or payload.get("Services")
            or payload.get("service")
            or payload.get("Service")
            or ""
        )
        services = services.strip() if isinstance(services, str) else services
        setcode = (payload.get("setcode") or payload.get("SetCode") or payload.get("code") or "").strip()

        if not setname or not services or not setcode or setcode == "*":
            raise ValueError("SetName, Services, SetCode là bắt buộc và không được để trống hoặc '*'.")

        tbl = payload.get("table") or payload.get("Table") or payload.get("tbl") or payload.get("TableName")
        col = payload.get("column") or payload.get("Column") or payload.get("col") or payload.get("ColumnName")
        val = payload.get("value") or payload.get("Value") or payload.get("val")

        from sqlalchemy.dialects.postgresql import insert

        stmt = (
            insert(Set)
            .values(setname=setname, services=services, setcode=setcode)
            .on_conflict_do_update(
                index_elements=[Set.setname, Set.services, Set.setcode],
                set_={"setname": setname, "services": services, "setcode": setcode},
            )
            .returning(Set.id)
        )
        set_id = session.execute(stmt).scalar_one()

        if tbl and col and val:
            session.execute(
                insert(Dataset)
                .values(set_id=set_id, tablename=tbl, colname=col, colval=val)
                .on_conflict_do_nothing()
            )

        return set_id

    def resolve_set_id(self, session, payload):
        sid = (
            payload.get("SetId")
            or payload.get("set_id")
            or payload.get("id")
            or payload.get("Id")
        )
        try:
            sid = int(sid)
        except Exception:
            raise ValueError("SetId is required for DATA permission.")

        row = session.get(Set, sid)
        if not row:
            raise ValueError(f"SetId {sid} không tồn tại.")
        return sid

    def list_sets(self, filters):
        with self.session() as session:
            base = session.query(
                Set.id.label("SetId"),
                Set.setname.label("SetName"),
                Set.services.label("Services"),
                Set.setcode.label("SetCode"),
            )
            for f in filters:
                base = base.filter(f)
            rows = base.order_by(Set.id).all()
            return [dict(r._mapping) for r in rows]

    def insert_set(self, payload):
        with self.session() as session:
            return self.ensure_set(payload, session)

    def update_set(self, set_id, payload):
        with self.session() as session:
            setname = payload.get("SetName") or payload.get("setname")
            services = payload.get("Services") or payload.get("services")
            setcode = payload.get("SetCode") or payload.get("setcode")
            session.query(Set).filter(Set.id == set_id).update(
                {"setname": setname, "services": services, "setcode": setcode},
                synchronize_session=False,
            )

    def delete_set(self, set_id):
        with self.session() as session:
            session.query(Dataset).filter(Dataset.set_id == set_id).delete(synchronize_session=False)
            session.query(Set).filter(Set.id == set_id).delete(synchronize_session=False)

    def list_dataset_by_set(self, set_id):
        with self.session() as session:
            rows = (
                session.query(
                    Dataset.id.label("Id"),
                    Dataset.set_id.label("SetId"),
                    Dataset.tablename.label("Table"),
                    Dataset.colname.label("Column"),
                    Dataset.colval.label("Value"),
                )
                .filter(Dataset.set_id == set_id)
                .order_by(Dataset.id)
                .all()
            )
            return [dict(r._mapping) for r in rows]

    def replace_dataset_for_set(self, set_id, items: List[dict]):
        with self.session() as session:
            session.query(Dataset).filter(Dataset.set_id == set_id).delete(synchronize_session=False)
            for it in items:
                table = (it.get("Table") or "*").strip()
                col = (it.get("Column") or "*").strip()
                val = (it.get("Value") or "*").strip()
                session.execute(
                    Dataset.__table__.insert()
                    .values(set_id=set_id, tablename=table, colname=col, colval=val)
                    .on_conflict_do_nothing()
                )

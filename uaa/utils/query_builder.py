from typing import List, Tuple, Optional, Any

from sqlalchemy import text


class QueryBuilder:
    """Builder hỗ trợ cả SQLAlchemy expressions lẫn chuỗi cũ (%s)."""

    def __init__(self, model=None, alias: str = ""):
        self.model = model
        self.alias = alias
        self.expressions: List[Any] = []

    def _col(self, column: str):
        if self.model is None:
            raise ValueError("QueryBuilder requires model to build expressions")
        return getattr(self.model, column)

    def add_ilike(self, column: str, value: Optional[str]):
        if value:
            self.expressions.append(self._col(column).ilike(f"%{value}%"))
        return self

    def add_equals(self, column: str, value: Optional[Any]):
        if value is not None:
            self.expressions.append(self._col(column) == value)
        return self

    def add_any(self, column: str, values: Optional[list]):
        if values:
            self.expressions.append(self._col(column).in_(values))
        return self

    def add_raw(self, clause: Optional[str], params: Optional[list]):
        """Cho phép thêm chuỗi WHERE có %s; sẽ bind sang :p0,:p1."""
        if clause:
            sql, bind = self._bind_sql(clause, params or [])
            self.expressions.append(text(sql).bindparams(**bind))
        return self

    def filters(self) -> List[Any]:
        return list(self.expressions)

    @staticmethod
    def _bind_sql(sql: str, params: List[Any]) -> Tuple[str, dict]:
        if not params:
            return sql, {}
        bound = {}
        parts = sql.split("%s")
        rebuilt = []
        for i, part in enumerate(parts):
            rebuilt.append(part)
            if i < len(parts) - 1:
                key = f"p{i}"
                rebuilt.append(f":{key}")
                bound[key] = params[i]
        return "".join(rebuilt), bound

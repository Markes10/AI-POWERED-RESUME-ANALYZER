"""
Base database operations class
"""
import json
from typing import Any, Dict, List, Optional
from .config import SessionLocal, Base


def get_db():
    """Yield a SQLAlchemy session (FastAPI dependency style)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DatabaseOperations:
    def __init__(self, table_name: str):
        self.table_name = table_name

    def _normalize_param_value(self, value: Any) -> Any:
        if isinstance(value, (list, dict)):
            return json.dumps(value)
        return value

    def _normalize_params(self, params: Any) -> Any:
        if isinstance(params, dict):
            return {key: self._normalize_param_value(value) for key, value in params.items()}
        if isinstance(params, (list, tuple)):
            return tuple(self._normalize_param_value(value) for value in params)
        return params

    def _normalize_rows(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized_rows: List[Dict[str, Any]] = []
        for row in rows:
            normalized_row: Dict[str, Any] = {}
            for key, value in row.items():
                if key == "vector_embedding":
                    normalized_row[key] = value
                    continue
                if isinstance(value, str):
                    stripped = value.strip()
                    if stripped and stripped[0] in "[{" and stripped[-1] in "]}":
                        try:
                            normalized_row[key] = json.loads(stripped)
                            continue
                        except Exception:
                            pass
                normalized_row[key] = value
            normalized_rows.append(normalized_row)
        return normalized_rows

    def _normalize_query_for_sqlite(self, query: str, params: Any) -> Any:
        if params is None:
            return query, params

        if isinstance(params, dict):
            return query, self._normalize_params(params)

        if isinstance(params, (list, tuple)) and "%s" in query:
            placeholder_count = query.count("%s")
            if placeholder_count == 0:
                return query, self._normalize_params(params)
            sqlite_query = query
            for _ in range(placeholder_count):
                sqlite_query = sqlite_query.replace("%s", "?", 1)
            return sqlite_query, self._normalize_params(params)

        return query, self._normalize_params(params)

    def execute_query(self, query: str, params: tuple = None) -> Any:
        """Execute a database query"""
        session = SessionLocal()
        try:
            normalized_query, normalized_params = self._normalize_query_for_sqlite(query, params)
            raw_connection = session.connection()
            result = raw_connection.exec_driver_sql(normalized_query, normalized_params or {})
            if query.strip().upper().startswith("SELECT"):
                rows = [dict(row._mapping) for row in result]
                return self._normalize_rows(rows)
            session.commit()
            return getattr(result, "lastrowid", None) or result.rowcount
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_by_id(self, id: int) -> Optional[Dict]:
        """Get a record by ID"""
        query = f"SELECT * FROM {self.table_name} WHERE id = :id"
        result = self.execute_query(query, {"id": id})
        return result[0] if result else None

    def get_all(self) -> List[Dict]:
        """Get all records"""
        query = f"SELECT * FROM {self.table_name}"
        return self.execute_query(query)

    def create(self, data: Dict) -> int:
        """Create a new record"""
        fields = ", ".join(data.keys())
        placeholders = ", ".join([f":{k}" for k in data.keys()])
        query = f"INSERT INTO {self.table_name} ({fields}) VALUES ({placeholders})"

        session = SessionLocal()
        try:
            from sqlalchemy import text
            params = self._normalize_params(data)
            session.execute(text(query), params)
            session.commit()

            last_row_id = session.execute(text("SELECT last_insert_rowid()"))
            scalar = last_row_id.scalar()
            return int(scalar) if scalar is not None else 0
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def update(self, id: int, data: Dict) -> bool:
        """Update a record"""
        set_clause = ", ".join([f"{k} = :{k}" for k in data.keys()])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = :id"
        data["id"] = id
        self.execute_query(query, data)
        return True

    def delete(self, id: int) -> bool:
        """Delete a record"""
        query = f"DELETE FROM {self.table_name} WHERE id = :id"
        self.execute_query(query, {"id": id})
        return True

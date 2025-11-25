import sqlite3
import json
from contextlib import contextmanager
from pathlib import Path


class DatabaseError(Exception):
    """Custom exception for database operations"""
    pass


def json_encode(obj):
    """Encode Python object to JSON string"""
    try:
        return json.dumps(obj)
    except (TypeError, ValueError) as e:
        raise DatabaseError(f"JSON encoding failed: {str(e)}")


def json_decode(json_str):
    """Decode JSON string to Python object"""
    if json_str is None:
        return None
    try:
        return json.loads(json_str)
    except (TypeError, ValueError) as e:
        raise DatabaseError(f"JSON decoding failed: {str(e)}")


class DatabaseManager:
    _instance = None
    _db_path = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance.connection = None
        return cls._instance
    
    def connect(self, db_path):
        """Connect to a database file and create schema if empty"""
        self._db_path = db_path
        self.connection = sqlite3.connect(
            db_path,
            check_same_thread=False,
            timeout=10
        )
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        
        # Auto-load schema if DB empty
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) AS c FROM sqlite_master WHERE type='table'")
        row = cursor.fetchone()
        count = row[0] if row else 0
        cursor.close()
        
        if count == 0:
            schema_path = Path(__file__).parent / "schema.sql"
            if schema_path.exists():
                with open(schema_path, "r", encoding="utf-8") as f:
                    self.connection.executescript(f.read())
                self.connection.commit()
    
    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def commit(self):
        if self.connection:
            self.connection.commit()
    
    def rollback(self):
        """Rollback current transaction"""
        if self.connection:
            self.connection.rollback()
    
    def run_schema(self, schema_path):
        """Load schema from file path"""
        with open(schema_path, "r", encoding="utf-8") as f:
            self.connection.executescript(f.read())
        self.connection.commit()
    
    # -------------------------
    # QUERY METHODS
    # -------------------------
    def execute(self, query, params=()):
        """Execute a query and return cursor"""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor
    
    def query_one(self, query, params=()):
        """Execute query and return single row as dict"""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        cursor.close()
        return dict(row) if row else None
    
    def query(self, query, params=()):
        """Execute query and return all rows as list of dicts"""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        return [dict(r) for r in rows]
    
    def query_all(self, query, params=()):
        """Alias for query()"""
        return self.query(query, params)
    
    def execute_insert(self, query, params=()):
        """Execute INSERT and return last row id"""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        last_id = cursor.lastrowid
        cursor.close()
        return last_id
    
    def execute_update(self, query, params=()):
        """Execute UPDATE and return number of affected rows"""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        row_count = cursor.rowcount
        cursor.close()
        return row_count
    
    def execute_delete(self, query, params=()):
        """Execute DELETE and return number of affected rows"""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        row_count = cursor.rowcount
        cursor.close()
        return row_count


# Global singleton instance
db = DatabaseManager()
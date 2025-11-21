"""
Database Connection Manager
Provides clean API for database operations with error handling
"""

import sqlite3
from contextlib import contextmanager
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

class DatabaseManager:
    """Singleton database manager"""
    
    _instance = None
    _db_path = 'jobbuddy.db'
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.connection = None
    
    def connect(self, db_path: str = None):
        """Connect to database"""
        if db_path:
            self._db_path = db_path
        
        try:
            self.connection = sqlite3.connect(
                self._db_path,
                check_same_thread=False,  # Allow multi-threading
                timeout=10.0  # Wait up to 10 seconds for locks
            )
            self.connection.row_factory = sqlite3.Row
            self.connection.execute('PRAGMA foreign_keys = ON')
            return True
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database cursor"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        try:
            yield cursor
            self.connection.commit()
        except sqlite3.Error as e:
            self.connection.rollback()
            raise DatabaseError(f"Database operation failed: {e}")
        finally:
            cursor.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute SELECT query and return results as list of dicts"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def execute_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Execute SELECT query and return single result"""
        results = self.execute_query(query, params)
        return results[0] if results else None
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT query and return lastrowid"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.lastrowid
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute UPDATE query and return affected rows"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount
    
    def execute_delete(self, query: str, params: tuple = ()) -> int:
        """Execute DELETE query and return affected rows"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount
    
    @contextmanager
    def transaction(self):
        """Context manager for transactions"""
        with self.get_cursor() as cursor:
            try:
                yield cursor
            except Exception as e:
                self.connection.rollback()
                raise DatabaseError(f"Transaction failed: {e}")

# Helper functions for JSON fields
def json_encode(data: Any) -> str:
    """Encode data as JSON string"""
    return json.dumps(data) if data else None

def json_decode(json_str: str) -> Any:
    """Decode JSON string to Python object"""
    try:
        return json.loads(json_str) if json_str else None
    except json.JSONDecodeError:
        return None

# Custom exception
class DatabaseError(Exception):
    """Custom database exception"""
    pass

# Singleton instance
db = DatabaseManager()
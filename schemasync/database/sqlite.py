"""
SQLite database adapter
"""
import os
import shutil
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from .base import BaseAdapter


class SQLiteAdapter(BaseAdapter):
    """SQLite database adapter"""

    def __init__(self, connection_string: str):
        super().__init__(connection_string)
        self.db_path = self._extract_db_path(connection_string)

    def _extract_db_path(self, connection_string: str) -> str:
        """Extract database path from connection string"""
        # Handle sqlite:///path/to/db or sqlite://path/to/db
        if connection_string.startswith('sqlite:///'):
            return connection_string[10:]
        elif connection_string.startswith('sqlite://'):
            return connection_string[9:]
        return connection_string

    def connect(self):
        """Establish database connection"""
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path)
            # Enable foreign keys
            self._connection.execute("PRAGMA foreign_keys = ON")
            # Return rows as dictionaries
            self._connection.row_factory = sqlite3.Row
        return self._connection

    def disconnect(self):
        """Close database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None

    def execute(self, sql: str, params: Optional[tuple] = None) -> None:
        """Execute SQL statement"""
        conn = self.connect()
        if params:
            conn.execute(sql, params)
        else:
            conn.execute(sql)
        conn.commit()

    def fetchall(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute query and return all results"""
        conn = self.connect()
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def fetchone(self, sql: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """Execute query and return first result"""
        conn = self.connect()
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)

        row = cursor.fetchone()
        return dict(row) if row else None

    def transaction(self):
        """Context manager for transactions"""
        return SQLiteTransaction(self)

    def create_migrations_table(self, table_name: str) -> None:
        """Create migrations tracking table"""
        sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version VARCHAR(255) NOT NULL UNIQUE,
            description TEXT,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            execution_time_ms INTEGER DEFAULT 0
        )
        """
        self.execute(sql)

    def get_applied_migrations(self, table_name: str) -> List[str]:
        """Get list of applied migration versions"""
        if not self.table_exists(table_name):
            return []

        sql = f"SELECT version FROM {table_name} ORDER BY version ASC"
        rows = self.fetchall(sql)
        return [row['version'] for row in rows]

    def apply_migration(self, table_name: str, version: str, description: str) -> None:
        """Record migration as applied"""
        sql = f"""
        INSERT INTO {table_name} (version, description, applied_at)
        VALUES (?, ?, ?)
        """
        self.execute(sql, (version, description, datetime.now().isoformat()))

    def revert_migration(self, table_name: str, version: str) -> None:
        """Remove migration record"""
        sql = f"DELETE FROM {table_name} WHERE version = ?"
        self.execute(sql, (version,))

    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information"""
        return {
            'driver': 'sqlite',
            'database': self.db_path,
            'absolute_path': os.path.abspath(self.db_path)
        }

    def backup_database(self, backup_path: str) -> None:
        """Create database backup"""
        # Ensure backup directory exists
        os.makedirs(os.path.dirname(backup_path) or '.', exist_ok=True)

        # Copy database file
        if os.path.exists(self.db_path):
            shutil.copy2(self.db_path, backup_path)
        else:
            # If database doesn't exist yet, create empty backup
            open(backup_path, 'a').close()

    def table_exists(self, table_name: str) -> bool:
        """Check if table exists"""
        sql = """
        SELECT name FROM sqlite_master
        WHERE type='table' AND name=?
        """
        result = self.fetchone(sql, (table_name,))
        return result is not None

    def get_tables(self) -> List[str]:
        """Get list of all tables"""
        sql = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        rows = self.fetchall(sql)
        return [row['name'] for row in rows]

    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get table schema information"""
        # Get table info
        sql = f"PRAGMA table_info({table_name})"
        columns = self.fetchall(sql)

        # Get indexes
        sql = f"PRAGMA index_list({table_name})"
        indexes = self.fetchall(sql)

        # Get foreign keys
        sql = f"PRAGMA foreign_key_list({table_name})"
        foreign_keys = self.fetchall(sql)

        return {
            'name': table_name,
            'columns': columns,
            'indexes': indexes,
            'foreign_keys': foreign_keys
        }


class SQLiteTransaction:
    """SQLite transaction context manager"""

    def __init__(self, adapter: SQLiteAdapter):
        self.adapter = adapter
        self.conn = None

    def __enter__(self):
        self.conn = self.adapter.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        return False

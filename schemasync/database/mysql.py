"""
MySQL database adapter
"""
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from .base import BaseAdapter


class MySQLAdapter(BaseAdapter):
    """MySQL database adapter"""

    def __init__(self, connection_string: str):
        super().__init__(connection_string)
        self.connection_params = self._parse_connection_string(connection_string)

    def _parse_connection_string(self, connection_string: str) -> Dict[str, Any]:
        """Parse MySQL connection string"""
        params = {}

        if '://' in connection_string:
            # Handle mysql+pymysql://user:pass@host:port/dbname
            from urllib.parse import urlparse
            parsed = urlparse(connection_string)

            params['host'] = parsed.hostname or 'localhost'
            params['port'] = parsed.port or 3306
            params['database'] = parsed.path.lstrip('/') if parsed.path else ''
            params['user'] = parsed.username
            params['password'] = parsed.password
        else:
            params['host'] = 'localhost'
            params['port'] = 3306
            params['database'] = connection_string
            params['user'] = None
            params['password'] = None

        return params

    def connect(self):
        """Establish database connection"""
        if self._connection is None:
            try:
                import pymysql
                from pymysql.cursors import DictCursor

                self._connection = pymysql.connect(
                    host=self.connection_params['host'],
                    port=self.connection_params['port'],
                    database=self.connection_params['database'],
                    user=self.connection_params['user'],
                    password=self.connection_params['password'],
                    charset='utf8mb4',
                    cursorclass=DictCursor
                )
            except ImportError:
                raise ImportError("pymysql is required for MySQL support. "
                                "Install with: pip install pymysql")
        return self._connection

    def disconnect(self):
        """Close database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None

    def execute(self, sql: str, params: Optional[tuple] = None) -> None:
        """Execute SQL statement"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            conn.commit()
        finally:
            cursor.close()

    def fetchall(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute query and return all results"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            return cursor.fetchall()
        finally:
            cursor.close()

    def fetchone(self, sql: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """Execute query and return first result"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            return cursor.fetchone()
        finally:
            cursor.close()

    def transaction(self):
        """Context manager for transactions"""
        return MySQLTransaction(self)

    def create_migrations_table(self, table_name: str) -> None:
        """Create migrations tracking table"""
        sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            version VARCHAR(255) NOT NULL UNIQUE,
            description TEXT,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            execution_time_ms INT DEFAULT 0
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
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
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE description = VALUES(description)
        """
        self.execute(sql, (version, description, datetime.now()))

    def revert_migration(self, table_name: str, version: str) -> None:
        """Remove migration record"""
        sql = f"DELETE FROM {table_name} WHERE version = %s"
        self.execute(sql, (version,))

    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information"""
        return {
            'driver': 'mysql',
            'host': self.connection_params['host'],
            'port': self.connection_params['port'],
            'database': self.connection_params['database'],
            'user': self.connection_params['user']
        }

    def backup_database(self, backup_path: str) -> None:
        """Create database backup using mysqldump"""
        import subprocess

        os.makedirs(os.path.dirname(backup_path) or '.', exist_ok=True)

        cmd = [
            'mysqldump',
            '-h', self.connection_params['host'],
            '-P', str(self.connection_params['port']),
            '-u', self.connection_params['user'],
        ]

        if self.connection_params.get('password'):
            cmd.append(f"-p{self.connection_params['password']}")

        cmd.append(self.connection_params['database'])

        try:
            with open(backup_path, 'w') as f:
                subprocess.run(cmd, stdout=f, check=True, capture_output=True)
        except FileNotFoundError:
            raise RuntimeError("mysqldump not found. Please install MySQL client tools.")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Backup failed: {e.stderr.decode()}")

    def table_exists(self, table_name: str) -> bool:
        """Check if table exists"""
        sql = """
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = DATABASE() AND table_name = %s
        """
        result = self.fetchone(sql, (table_name,))
        return result is not None

    def get_tables(self) -> List[str]:
        """Get list of all tables"""
        sql = """
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = DATABASE()
        ORDER BY table_name
        """
        rows = self.fetchall(sql)
        return [row['table_name'] for row in rows]

    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get table schema information"""
        # Get columns
        sql = """
        SELECT column_name, data_type, is_nullable, column_default, extra
        FROM information_schema.columns
        WHERE table_schema = DATABASE() AND table_name = %s
        ORDER BY ordinal_position
        """
        columns = self.fetchall(sql, (table_name,))

        # Get indexes
        sql = """
        SELECT index_name, column_name, non_unique
        FROM information_schema.statistics
        WHERE table_schema = DATABASE() AND table_name = %s
        """
        indexes = self.fetchall(sql, (table_name,))

        # Get foreign keys
        sql = """
        SELECT
            kcu.column_name,
            kcu.referenced_table_name AS foreign_table_name,
            kcu.referenced_column_name AS foreign_column_name
        FROM information_schema.key_column_usage AS kcu
        WHERE kcu.table_schema = DATABASE()
            AND kcu.table_name = %s
            AND kcu.referenced_table_name IS NOT NULL
        """
        foreign_keys = self.fetchall(sql, (table_name,))

        return {
            'name': table_name,
            'columns': columns,
            'indexes': indexes,
            'foreign_keys': foreign_keys
        }


class MySQLTransaction:
    """MySQL transaction context manager"""

    def __init__(self, adapter: MySQLAdapter):
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

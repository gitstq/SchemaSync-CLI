"""
PostgreSQL database adapter
"""
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from .base import BaseAdapter


class PostgreSQLAdapter(BaseAdapter):
    """PostgreSQL database adapter"""

    def __init__(self, connection_string: str):
        super().__init__(connection_string)
        self.connection_params = self._parse_connection_string(connection_string)

    def _parse_connection_string(self, connection_string: str) -> Dict[str, Any]:
        """Parse PostgreSQL connection string"""
        # Handle postgresql+psycopg2://user:pass@host:port/dbname
        params = {}

        if '://' in connection_string:
            # Remove driver prefix
            if '+' in connection_string:
                connection_string = connection_string.split('+')[0] + '://' + connection_string.split('://')[1]

            # Parse URL
            from urllib.parse import urlparse
            parsed = urlparse(connection_string)

            params['host'] = parsed.hostname or 'localhost'
            params['port'] = parsed.port or 5432
            params['database'] = parsed.path.lstrip('/') if parsed.path else ''
            params['user'] = parsed.username
            params['password'] = parsed.password
        else:
            params['host'] = 'localhost'
            params['port'] = 5432
            params['database'] = connection_string

        return params

    def connect(self):
        """Establish database connection"""
        if self._connection is None:
            try:
                import psycopg2
                from psycopg2.extras import RealDictCursor

                self._connection = psycopg2.connect(
                    host=self.connection_params['host'],
                    port=self.connection_params['port'],
                    database=self.connection_params['database'],
                    user=self.connection_params['user'],
                    password=self.connection_params['password']
                )
            except ImportError:
                raise ImportError("psycopg2 is required for PostgreSQL support. "
                                "Install with: pip install psycopg2-binary")
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

            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()

            return [dict(zip(columns, row)) for row in rows]
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

            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            row = cursor.fetchone()

            return dict(zip(columns, row)) if row else None
        finally:
            cursor.close()

    def transaction(self):
        """Context manager for transactions"""
        return PostgreSQLTransaction(self)

    def create_migrations_table(self, table_name: str) -> None:
        """Create migrations tracking table"""
        sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id SERIAL PRIMARY KEY,
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
        VALUES (%s, %s, %s)
        ON CONFLICT (version) DO NOTHING
        """
        self.execute(sql, (version, description, datetime.now()))

    def revert_migration(self, table_name: str, version: str) -> None:
        """Remove migration record"""
        sql = f"DELETE FROM {table_name} WHERE version = %s"
        self.execute(sql, (version,))

    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information"""
        return {
            'driver': 'postgresql',
            'host': self.connection_params['host'],
            'port': self.connection_params['port'],
            'database': self.connection_params['database'],
            'user': self.connection_params['user']
        }

    def backup_database(self, backup_path: str) -> None:
        """Create database backup using pg_dump"""
        import subprocess

        os.makedirs(os.path.dirname(backup_path) or '.', exist_ok=True)

        cmd = [
            'pg_dump',
            '-h', self.connection_params['host'],
            '-p', str(self.connection_params['port']),
            '-U', self.connection_params['user'],
            '-d', self.connection_params['database'],
            '-f', backup_path
        ]

        env = os.environ.copy()
        env['PGPASSWORD'] = self.connection_params.get('password', '')

        try:
            subprocess.run(cmd, env=env, check=True, capture_output=True)
        except FileNotFoundError:
            raise RuntimeError("pg_dump not found. Please install PostgreSQL client tools.")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Backup failed: {e.stderr.decode()}")

    def table_exists(self, table_name: str) -> bool:
        """Check if table exists"""
        sql = """
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = %s
        """
        result = self.fetchone(sql, (table_name,))
        return result is not None

    def get_tables(self) -> List[str]:
        """Get list of all tables"""
        sql = """
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
        """
        rows = self.fetchall(sql)
        return [row['table_name'] for row in rows]

    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get table schema information"""
        # Get columns
        sql = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s
        ORDER BY ordinal_position
        """
        columns = self.fetchall(sql, (table_name,))

        # Get indexes
        sql = """
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE schemaname = 'public' AND tablename = %s
        """
        indexes = self.fetchall(sql, (table_name,))

        # Get foreign keys
        sql = """
        SELECT
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'
            AND tc.table_name = %s
        """
        foreign_keys = self.fetchall(sql, (table_name,))

        return {
            'name': table_name,
            'columns': columns,
            'indexes': indexes,
            'foreign_keys': foreign_keys
        }


class PostgreSQLTransaction:
    """PostgreSQL transaction context manager"""

    def __init__(self, adapter: PostgreSQLAdapter):
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

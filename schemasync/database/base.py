"""
Base database adapter interface
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple


class BaseAdapter(ABC):
    """Abstract base class for database adapters"""

    def __init__(self, connection_string: str):
        """
        Initialize adapter

        Args:
            connection_string: Database connection string
        """
        self.connection_string = connection_string
        self._connection = None

    @abstractmethod
    def connect(self):
        """Establish database connection"""
        pass

    @abstractmethod
    def disconnect(self):
        """Close database connection"""
        pass

    @abstractmethod
    def execute(self, sql: str, params: Optional[tuple] = None) -> None:
        """
        Execute SQL statement

        Args:
            sql: SQL statement
            params: Query parameters
        """
        pass

    @abstractmethod
    def fetchall(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Execute query and return all results

        Args:
            sql: SQL query
            params: Query parameters

        Returns:
            List of result rows as dictionaries
        """
        pass

    @abstractmethod
    def fetchone(self, sql: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """
        Execute query and return first result

        Args:
            sql: SQL query
            params: Query parameters

        Returns:
            First result row as dictionary, or None
        """
        pass

    @abstractmethod
    def transaction(self):
        """Context manager for transactions"""
        pass

    @abstractmethod
    def create_migrations_table(self, table_name: str) -> None:
        """
        Create migrations tracking table

        Args:
            table_name: Name of the migrations table
        """
        pass

    @abstractmethod
    def get_applied_migrations(self, table_name: str) -> List[str]:
        """
        Get list of applied migration versions

        Args:
            table_name: Name of the migrations table

        Returns:
            List of applied migration version strings
        """
        pass

    @abstractmethod
    def apply_migration(self, table_name: str, version: str, description: str) -> None:
        """
        Record migration as applied

        Args:
            table_name: Name of the migrations table
            version: Migration version
            description: Migration description
        """
        pass

    @abstractmethod
    def revert_migration(self, table_name: str, version: str) -> None:
        """
        Remove migration record

        Args:
            table_name: Name of the migrations table
            version: Migration version
        """
        pass

    @abstractmethod
    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get connection information

        Returns:
            Dictionary with connection details
        """
        pass

    @abstractmethod
    def backup_database(self, backup_path: str) -> None:
        """
        Create database backup

        Args:
            backup_path: Path to save backup
        """
        pass

    @abstractmethod
    def table_exists(self, table_name: str) -> bool:
        """
        Check if table exists

        Args:
            table_name: Name of the table

        Returns:
            True if table exists
        """
        pass

    @abstractmethod
    def get_tables(self) -> List[str]:
        """
        Get list of all tables

        Returns:
            List of table names
        """
        pass

    @abstractmethod
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """
        Get table schema information

        Args:
            table_name: Name of the table

        Returns:
            Dictionary with schema details
        """
        pass

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
        return False

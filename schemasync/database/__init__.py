"""
Database adapters for SchemaSync
"""
from .base import BaseAdapter
from .sqlite import SQLiteAdapter
from .postgresql import PostgreSQLAdapter
from .mysql import MySQLAdapter

__all__ = ["BaseAdapter", "SQLiteAdapter", "PostgreSQLAdapter", "MySQLAdapter"]


def get_adapter(driver: str):
    """
    Get database adapter by driver name

    Args:
        driver: Database driver name (sqlite, postgresql, mysql)

    Returns:
        Adapter class

    Raises:
        ValueError: If driver is not supported
    """
    adapters = {
        'sqlite': SQLiteAdapter,
        'postgresql': PostgreSQLAdapter,
        'postgres': PostgreSQLAdapter,
        'mysql': MySQLAdapter,
    }

    driver_lower = driver.lower()
    if driver_lower not in adapters:
        raise ValueError(f"Unsupported database driver: {driver}. "
                        f"Supported: {', '.join(adapters.keys())}")

    return adapters[driver_lower]

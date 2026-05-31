"""
SchemaSync-CLI - A lightweight database schema migration tool

A developer-friendly CLI tool for managing database schema versions
and migrations across SQLite, PostgreSQL, and MySQL.
"""

__version__ = "1.0.0"
__author__ = "SchemaSync Team"
__license__ = "MIT"
__title__ = "SchemaSync-CLI"
__description__ = "A lightweight database schema migration tool"

from .config import Config
from .migration.manager import MigrationManager

__all__ = ["Config", "MigrationManager"]

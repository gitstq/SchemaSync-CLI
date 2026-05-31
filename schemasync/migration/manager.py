"""
Migration manager - high-level interface
"""
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from ..config import Config
from ..database import get_adapter
from .file import MigrationFile
from .executor import MigrationExecutor


class MigrationManager:
    """High-level migration management interface"""

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize migration manager

        Args:
            config: Configuration instance (creates default if None)
        """
        self.config = config or Config()
        self.migrations_dir = self.config.get_migrations_dir()
        self.backup_dir = self.config.get_backup_dir()

    def init(self, directory: Optional[str] = None) -> None:
        """
        Initialize migration environment

        Args:
            directory: Directory to initialize (default: current directory)
        """
        target_dir = Path(directory) if directory else Path.cwd()

        # Create migrations directory
        migrations_dir = target_dir / self.config.get('migrations.directory', 'migrations')
        migrations_dir.mkdir(parents=True, exist_ok=True)

        # Create __init__.py
        init_file = migrations_dir / '__init__.py'
        init_file.write_text('"""Database migrations"""\n', encoding='utf-8')

        # Create backup directory
        backup_dir = target_dir / self.config.get('migrations.backup_directory', 'backups')
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Create config file if not exists
        config_file = target_dir / 'schemasync.yaml'
        if not config_file.exists():
            self.config.save(str(config_file))

        print(f"✅ Initialized SchemaSync in {target_dir}")
        print(f"   Migrations directory: {migrations_dir}")
        print(f"   Backup directory: {backup_dir}")

    def create(self, description: str,
               upgrade_sql: str = "",
               downgrade_sql: str = "") -> MigrationFile:
        """
        Create a new migration

        Args:
            description: Migration description
            upgrade_sql: Upgrade SQL
            downgrade_sql: Downgrade SQL

        Returns:
            Created MigrationFile
        """
        self.migrations_dir.mkdir(parents=True, exist_ok=True)

        # Get last migration for down_revision
        migrations = self._load_migrations()
        last_migration = migrations[-1] if migrations else None
        down_revision = last_migration.version if last_migration else None

        migration = MigrationFile.create(
            self.migrations_dir,
            description,
            upgrade_sql,
            downgrade_sql,
            down_revision
        )

        print(f"✅ Created migration: {migration.path.name}")
        print(f"   Version: {migration.version}")
        print(f"   Path: {migration.path}")

        return migration

    def status(self) -> Dict[str, Any]:
        """Get migration status"""
        migrations = self._load_migrations()

        with self._get_adapter() as adapter:
            executor = MigrationExecutor(
                adapter,
                self.config.get('migrations.table_name', 'schema_migrations')
            )
            return executor.get_status(migrations)

    def migrate(self, target_version: Optional[str] = None,
                dry_run: bool = False) -> List[Dict]:
        """
        Execute pending migrations

        Args:
            target_version: Target version (None = latest)
            dry_run: Preview without executing

        Returns:
            List of execution results
        """
        migrations = self._load_migrations()

        if not migrations:
            print("⚠️  No migrations found")
            return []

        # Create backup if enabled
        if not dry_run and self.config.get('migrations.backup_before_migrate', True):
            self._create_backup()

        with self._get_adapter() as adapter:
            executor = MigrationExecutor(
                adapter,
                self.config.get('migrations.table_name', 'schema_migrations')
            )

            def progress_callback(migration, direction, success, error=None):
                status = "✅" if success else "❌"
                action = "Applied" if direction == 'up' else "Reverted"
                print(f"{status} {action}: {migration.version} - {migration.description}")
                if error:
                    print(f"   Error: {error}")

            results = executor.migrate(
                migrations, target_version, dry_run, progress_callback
            )

            if dry_run:
                print("\n⚠️  This was a dry run. No changes were made.")

            return results

    def rollback(self, steps: int = 1,
                target_version: Optional[str] = None,
                dry_run: bool = False) -> List[Dict]:
        """
        Rollback migrations

        Args:
            steps: Number of migrations to rollback
            target_version: Target version to rollback to
            dry_run: Preview without executing

        Returns:
            List of execution results
        """
        migrations = self._load_migrations()

        if not migrations:
            print("⚠️  No migrations found")
            return []

        # Create backup if enabled
        if not dry_run and self.config.get('migrations.backup_before_migrate', True):
            self._create_backup()

        with self._get_adapter() as adapter:
            executor = MigrationExecutor(
                adapter,
                self.config.get('migrations.table_name', 'schema_migrations')
            )

            def progress_callback(migration, direction, success, error=None):
                status = "✅" if success else "❌"
                action = "Reverted" if direction == 'down' else "Applied"
                print(f"{status} {action}: {migration.version} - {migration.description}")
                if error:
                    print(f"   Error: {error}")

            results = executor.rollback(
                migrations, steps, target_version, dry_run, progress_callback
            )

            if dry_run:
                print("\n⚠️  This was a dry run. No changes were made.")

            return results

    def history(self) -> List[Dict[str, Any]]:
        """Get migration history"""
        migrations = self._load_migrations()

        with self._get_adapter() as adapter:
            executor = MigrationExecutor(
                adapter,
                self.config.get('migrations.table_name', 'schema_migrations')
            )

            applied = executor.get_applied_migrations()
            migration_map = {m.version: m for m in migrations}

            history = []
            for version in applied:
                migration = migration_map.get(version)
                history.append({
                    'version': version,
                    'description': migration.description if migration else 'Unknown',
                    'file': migration.path.name if migration else None
                })

            return history

    def _load_migrations(self) -> List[MigrationFile]:
        """Load all migrations from directory"""
        if not self.migrations_dir.exists():
            return []
        return MigrationFile.from_directory(self.migrations_dir)

    def _get_adapter(self):
        """Get database adapter"""
        driver = self.config.get('database.driver', 'sqlite')
        adapter_class = get_adapter(driver)
        connection_string = self.config.get_database_url()
        return adapter_class(connection_string)

    def _create_backup(self) -> str:
        """Create database backup"""
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"backup_{timestamp}"

        with self._get_adapter() as adapter:
            backup_path = self.backup_dir / backup_name
            adapter.backup_database(str(backup_path))

        print(f"💾 Created backup: {backup_path}")
        return str(backup_path)

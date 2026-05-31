"""
Migration execution engine
"""
import time
from pathlib import Path
from typing import List, Optional, Callable
from ..database.base import BaseAdapter
from .file import MigrationFile


class MigrationExecutor:
    """Executes database migrations"""

    def __init__(self, adapter: BaseAdapter, table_name: str = "schema_migrations"):
        """
        Initialize executor

        Args:
            adapter: Database adapter
            table_name: Name of migrations tracking table
        """
        self.adapter = adapter
        self.table_name = table_name

    def ensure_migrations_table(self) -> None:
        """Ensure migrations tracking table exists"""
        self.adapter.create_migrations_table(self.table_name)

    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions"""
        return self.adapter.get_applied_migrations(self.table_name)

    def get_pending_migrations(self, migrations: List[MigrationFile]) -> List[MigrationFile]:
        """
        Get list of pending migrations

        Args:
            migrations: All available migrations

        Returns:
            List of pending migrations
        """
        applied = set(self.get_applied_migrations())
        return [m for m in migrations if m.version not in applied]

    def execute_migration(self, migration: MigrationFile,
                         direction: str = 'up',
                         dry_run: bool = False,
                         progress_callback: Optional[Callable] = None) -> dict:
        """
        Execute a single migration

        Args:
            migration: Migration to execute
            direction: 'up' or 'down'
            dry_run: If True, only print SQL without executing
            progress_callback: Optional callback for progress updates

        Returns:
            Execution result dictionary
        """
        result = {
            'version': migration.version,
            'description': migration.description,
            'direction': direction,
            'success': False,
            'execution_time': 0,
            'sql_executed': []
        }

        # Get SQL
        if direction == 'up':
            sql = migration.get_upgrade_sql()
        else:
            sql = migration.get_downgrade_sql()

        result['sql_executed'] = [sql]

        if dry_run:
            result['success'] = True
            return result

        # Execute migration
        start_time = time.time()

        try:
            with self.adapter.transaction():
                # Execute the migration SQL
                self.adapter.execute(sql)

                # Update migration tracking
                if direction == 'up':
                    self.adapter.apply_migration(
                        self.table_name,
                        migration.version,
                        migration.description
                    )
                else:
                    self.adapter.revert_migration(
                        self.table_name,
                        migration.version
                    )

            result['execution_time'] = int((time.time() - start_time) * 1000)
            result['success'] = True

            if progress_callback:
                progress_callback(migration, direction, True)

        except Exception as e:
            result['execution_time'] = int((time.time() - start_time) * 1000)
            result['error'] = str(e)

            if progress_callback:
                progress_callback(migration, direction, False, str(e))

        return result

    def migrate(self, migrations: List[MigrationFile],
                target_version: Optional[str] = None,
                dry_run: bool = False,
                progress_callback: Optional[Callable] = None) -> List[dict]:
        """
        Execute pending migrations

        Args:
            migrations: All available migrations
            target_version: Target version (None = latest)
            dry_run: If True, only preview without executing
            progress_callback: Optional callback for progress updates

        Returns:
            List of execution results
        """
        self.ensure_migrations_table()

        pending = self.get_pending_migrations(migrations)

        if target_version:
            # Filter migrations up to target version
            pending = [m for m in pending if m.version <= target_version]

        results = []
        for migration in pending:
            result = self.execute_migration(
                migration, 'up', dry_run, progress_callback
            )
            results.append(result)

            if not dry_run and not result['success']:
                # Stop on first failure
                break

        return results

    def rollback(self, migrations: List[MigrationFile],
                steps: int = 1,
                target_version: Optional[str] = None,
                dry_run: bool = False,
                progress_callback: Optional[Callable] = None) -> List[dict]:
        """
        Rollback migrations

        Args:
            migrations: All available migrations
            steps: Number of migrations to rollback
            target_version: Target version to rollback to
            dry_run: If True, only preview without executing
            progress_callback: Optional callback for progress updates

        Returns:
            List of execution results
        """
        self.ensure_migrations_table()

        applied = self.get_applied_migrations()

        if not applied:
            return []

        # Determine which migrations to rollback
        if target_version:
            # Rollback all migrations after target_version
            to_rollback = [v for v in applied if v > target_version]
            to_rollback.reverse()
        else:
            # Rollback specified number of steps
            to_rollback = applied[-steps:]
            to_rollback.reverse()

        # Find migration files
        migration_map = {m.version: m for m in migrations}

        results = []
        for version in to_rollback:
            if version in migration_map:
                migration = migration_map[version]
                result = self.execute_migration(
                    migration, 'down', dry_run, progress_callback
                )
                results.append(result)

                if not dry_run and not result['success']:
                    break

        return results

    def get_status(self, migrations: List[MigrationFile]) -> dict:
        """
        Get migration status

        Args:
            migrations: All available migrations

        Returns:
            Status dictionary
        """
        self.ensure_migrations_table()

        applied = set(self.get_applied_migrations())

        status = {
            'total': len(migrations),
            'applied': len(applied),
            'pending': 0,
            'migrations': []
        }

        for migration in migrations:
            is_applied = migration.version in applied
            if not is_applied:
                status['pending'] += 1

            status['migrations'].append({
                'version': migration.version,
                'description': migration.description,
                'applied': is_applied
            })

        return status

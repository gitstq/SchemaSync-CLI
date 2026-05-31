"""
Tests for migration module
"""
import os
import pytest
from pathlib import Path

from schemasync.migration.file import MigrationFile
from schemasync.migration.executor import MigrationExecutor
from schemasync.database.sqlite import SQLiteAdapter


class TestMigrationFile:
    """Test migration file operations"""

    def test_create_migration(self, tmp_path):
        """Test creating a new migration file"""
        migration = MigrationFile.create(
            tmp_path,
            "add users table",
            "CREATE TABLE users (id INTEGER PRIMARY KEY);",
            "DROP TABLE users;"
        )

        assert migration.path.exists()
        assert migration.path.suffix == '.py'
        assert 'add_users_table' in migration.path.name

        # Check content
        content = migration.path.read_text()
        assert 'def upgrade():' in content
        assert 'def downgrade():' in content
        assert 'CREATE TABLE users' in content
        assert 'DROP TABLE users' in content

    def test_load_migration(self, tmp_path):
        """Test loading a migration file"""
        migration = MigrationFile.create(
            tmp_path,
            "test migration",
            "SELECT 1;",
            "SELECT 2;"
        )

        metadata = migration.load()

        assert 'revision' in metadata
        assert 'upgrade' in metadata
        assert 'downgrade' in metadata
        assert callable(metadata['upgrade'])
        assert callable(metadata['downgrade'])

    def test_get_sql(self, tmp_path):
        """Test getting upgrade/downgrade SQL"""
        migration = MigrationFile.create(
            tmp_path,
            "sql test",
            "CREATE TABLE test (id INT);",
            "DROP TABLE test;"
        )

        upgrade = migration.get_upgrade_sql()
        downgrade = migration.get_downgrade_sql()

        assert 'CREATE TABLE test' in upgrade
        assert 'DROP TABLE test' in downgrade

    def test_from_directory(self, tmp_path):
        """Test loading migrations from directory"""
        # Create some migrations
        MigrationFile.create(tmp_path, "first", "SELECT 1;", "")
        MigrationFile.create(tmp_path, "second", "SELECT 2;", "")

        migrations = MigrationFile.from_directory(tmp_path)

        assert len(migrations) == 2
        # Should be sorted by version
        assert migrations[0].version < migrations[1].version


class TestMigrationExecutor:
    """Test migration execution"""

    @pytest.fixture
    def adapter(self, tmp_path):
        """Create SQLite adapter for testing"""
        db_path = tmp_path / 'test.db'
        adapter = SQLiteAdapter(f'sqlite:///{db_path}')
        return adapter

    @pytest.fixture
    def migrations_dir(self, tmp_path):
        """Create temporary migrations directory"""
        migrations_dir = tmp_path / 'migrations'
        migrations_dir.mkdir()
        return migrations_dir

    def test_create_migrations_table(self, adapter):
        """Test creating migrations tracking table"""
        executor = MigrationExecutor(adapter)
        executor.ensure_migrations_table()

        assert adapter.table_exists('schema_migrations')

    def test_apply_migration(self, adapter, migrations_dir):
        """Test applying a migration"""
        # Create a migration
        migration = MigrationFile.create(
            migrations_dir,
            "create test table",
            "CREATE TABLE test (id INTEGER PRIMARY KEY);",
            "DROP TABLE test;"
        )

        executor = MigrationExecutor(adapter)
        executor.ensure_migrations_table()

        result = executor.execute_migration(migration, 'up')

        assert result['success'] is True
        assert adapter.table_exists('test')

        # Check migration was recorded
        applied = executor.get_applied_migrations()
        assert migration.version in applied

    def test_rollback_migration(self, adapter, migrations_dir):
        """Test rolling back a migration"""
        # Create and apply a migration
        migration = MigrationFile.create(
            migrations_dir,
            "create rollback table",
            "CREATE TABLE rollback_test (id INTEGER PRIMARY KEY);",
            "DROP TABLE rollback_test;"
        )

        executor = MigrationExecutor(adapter)
        executor.ensure_migrations_table()
        executor.execute_migration(migration, 'up')

        # Rollback
        result = executor.execute_migration(migration, 'down')

        assert result['success'] is True
        assert not adapter.table_exists('rollback_test')

        # Check migration was removed
        applied = executor.get_applied_migrations()
        assert migration.version not in applied

    def test_dry_run(self, adapter, migrations_dir):
        """Test dry run mode"""
        migration = MigrationFile.create(
            migrations_dir,
            "dry run test",
            "CREATE TABLE dry_run (id INTEGER);",
            "DROP TABLE dry_run;"
        )

        executor = MigrationExecutor(adapter)
        executor.ensure_migrations_table()

        result = executor.execute_migration(migration, 'up', dry_run=True)

        assert result['success'] is True
        assert not adapter.table_exists('dry_run')  # Should not be created

    def test_get_status(self, adapter, migrations_dir):
        """Test getting migration status"""
        # Create migrations
        m1 = MigrationFile.create(migrations_dir, "first", "SELECT 1;", "")
        m2 = MigrationFile.create(migrations_dir, "second", "SELECT 2;", "")

        executor = MigrationExecutor(adapter)
        executor.ensure_migrations_table()

        # Apply first migration
        executor.execute_migration(m1, 'up')

        status = executor.get_status([m1, m2])

        assert status['total'] == 2
        assert status['applied'] == 1
        assert status['pending'] == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

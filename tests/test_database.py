"""
Tests for database adapters
"""
import pytest
from pathlib import Path

from schemasync.database.sqlite import SQLiteAdapter


class TestSQLiteAdapter:
    """Test SQLite adapter"""

    @pytest.fixture
    def adapter(self, tmp_path):
        """Create SQLite adapter for testing"""
        db_path = tmp_path / 'test.db'
        adapter = SQLiteAdapter(f'sqlite:///{db_path}')
        return adapter

    def test_connect_disconnect(self, adapter):
        """Test connection management"""
        adapter.connect()
        assert adapter._connection is not None

        adapter.disconnect()
        assert adapter._connection is None

    def test_execute_and_fetch(self, adapter):
        """Test executing SQL and fetching results"""
        with adapter:
            # Create table
            adapter.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")

            # Insert data
            adapter.execute("INSERT INTO test (name) VALUES (?)", ("test_name",))

            # Fetch
            result = adapter.fetchone("SELECT * FROM test WHERE id = 1")
            assert result['name'] == 'test_name'

            # Fetch all
            adapter.execute("INSERT INTO test (name) VALUES (?)", ("test_name2",))
            results = adapter.fetchall("SELECT * FROM test")
            assert len(results) == 2

    def test_transaction(self, adapter):
        """Test transaction handling"""
        with adapter:
            adapter.execute("CREATE TABLE trans_test (id INTEGER)")

            # Successful transaction
            with adapter.transaction():
                adapter.execute("INSERT INTO trans_test VALUES (1)")
                adapter.execute("INSERT INTO trans_test VALUES (2)")

            results = adapter.fetchall("SELECT * FROM trans_test")
            assert len(results) == 2

    def test_table_exists(self, adapter):
        """Test checking table existence"""
        with adapter:
            assert not adapter.table_exists('nonexistent')

            adapter.execute("CREATE TABLE existing (id INTEGER)")
            assert adapter.table_exists('existing')

    def test_get_tables(self, adapter):
        """Test getting list of tables"""
        with adapter:
            adapter.execute("CREATE TABLE table1 (id INTEGER)")
            adapter.execute("CREATE TABLE table2 (id INTEGER)")

            tables = adapter.get_tables()
            assert 'table1' in tables
            assert 'table2' in tables

    def test_migrations_table(self, adapter):
        """Test migrations tracking table"""
        with adapter:
            adapter.create_migrations_table('test_migrations')
            assert adapter.table_exists('test_migrations')

            # Test applying migration
            adapter.apply_migration('test_migrations', '20250101000001', 'test migration')
            applied = adapter.get_applied_migrations('test_migrations')
            assert '20250101000001' in applied

            # Test reverting migration
            adapter.revert_migration('test_migrations', '20250101000001')
            applied = adapter.get_applied_migrations('test_migrations')
            assert '20250101000001' not in applied

    def test_backup_database(self, adapter, tmp_path):
        """Test database backup"""
        with adapter:
            adapter.execute("CREATE TABLE backup_test (id INTEGER)")
            adapter.execute("INSERT INTO backup_test VALUES (1)")

        backup_path = tmp_path / 'backup.db'
        adapter.backup_database(str(backup_path))

        assert backup_path.exists()

        # Verify backup works
        backup_adapter = SQLiteAdapter(f'sqlite:///{backup_path}')
        with backup_adapter:
            result = backup_adapter.fetchone("SELECT * FROM backup_test")
            assert result['id'] == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

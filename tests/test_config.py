"""
Tests for configuration module
"""
import os
import tempfile
import pytest
from pathlib import Path

from schemasync.config import Config


class TestConfig:
    """Test configuration management"""

    def test_default_config(self):
        """Test default configuration values"""
        config = Config()

        assert config.get('database.driver') == 'sqlite'
        assert config.get('database.host') == 'localhost'
        assert config.get('migrations.directory') == 'migrations'
        assert config.get('migrations.table_name') == 'schema_migrations'

    def test_get_set(self):
        """Test getting and setting values"""
        config = Config()

        # Test get with default
        assert config.get('nonexistent.key', 'default') == 'default'

        # Test set and get
        config.set('test.key', 'value')
        assert config.get('test.key') == 'value'

        # Test nested set
        config.set('database.host', 'remotehost')
        assert config.get('database.host') == 'remotehost'

    def test_yaml_config_file(self, tmp_path):
        """Test loading YAML config file"""
        config_file = tmp_path / 'test_config.yaml'
        config_file.write_text("""
database:
  driver: postgresql
  host: db.example.com
  port: 5432
  name: testdb
migrations:
  directory: custom_migrations
""")

        config = Config(str(config_file))

        assert config.get('database.driver') == 'postgresql'
        assert config.get('database.host') == 'db.example.com'
        assert config.get('database.port') == 5432
        assert config.get('migrations.directory') == 'custom_migrations'

    def test_json_config_file(self, tmp_path):
        """Test loading JSON config file"""
        config_file = tmp_path / 'test_config.json'
        config_file.write_text('''
{
  "database": {
    "driver": "mysql",
    "host": "mysql.example.com"
  }
}
''')

        config = Config(str(config_file))

        assert config.get('database.driver') == 'mysql'
        assert config.get('database.host') == 'mysql.example.com'

    def test_environment_variables(self, monkeypatch):
        """Test environment variable overrides"""
        monkeypatch.setenv('SCHEMASYNC_DB_DRIVER', 'postgresql')
        monkeypatch.setenv('SCHEMASYNC_DB_HOST', 'envhost')
        monkeypatch.setenv('SCHEMASYNC_DB_PORT', '3306')

        config = Config()

        assert config.get('database.driver') == 'postgresql'
        assert config.get('database.host') == 'envhost'
        assert config.get('database.port') == 3306

    def test_save_config(self, tmp_path):
        """Test saving configuration"""
        config = Config()
        config.set('database.name', 'saved_db')

        config_file = tmp_path / 'saved_config.yaml'
        config.save(str(config_file))

        # Load and verify
        loaded = Config(str(config_file))
        assert loaded.get('database.name') == 'saved_db'

    def test_get_database_url_sqlite(self):
        """Test SQLite database URL generation"""
        config = Config()
        config.set('database.driver', 'sqlite')
        config.set('database.name', 'test.db')

        url = config.get_database_url()
        assert url == 'sqlite:///test.db'

    def test_get_database_url_postgresql(self):
        """Test PostgreSQL database URL generation"""
        config = Config()
        config.set('database.driver', 'postgresql')
        config.set('database.host', 'localhost')
        config.set('database.port', 5432)
        config.set('database.name', 'testdb')
        config.set('database.user', 'user')
        config.set('database.password', 'pass')

        url = config.get_database_url()
        assert 'postgresql+psycopg2' in url
        assert 'user:pass@localhost:5432/testdb' in url

    def test_get_migrations_dir(self):
        """Test migrations directory path"""
        config = Config()
        path = config.get_migrations_dir()

        assert isinstance(path, Path)
        assert path.name == 'migrations'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

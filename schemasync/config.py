"""
Configuration management for SchemaSync
"""
import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Configuration manager for SchemaSync"""

    DEFAULT_CONFIG = {
        "database": {
            "driver": "sqlite",
            "host": "localhost",
            "port": None,
            "name": "database.db",
            "user": None,
            "password": None,
            "url": None
        },
        "migrations": {
            "directory": "migrations",
            "table_name": "schema_migrations",
            "backup_before_migrate": True,
            "backup_directory": "backups"
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": None
        }
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration

        Args:
            config_path: Path to configuration file (YAML or JSON)
        """
        self.config_path = config_path or self._find_config_file()
        self._config = self._load_config()

    def _find_config_file(self) -> Optional[str]:
        """Find configuration file in current directory"""
        possible_files = [
            "schemasync.yaml",
            "schemasync.yml",
            "schemasync.json",
            ".schemasync.yaml",
            ".schemasync.yml",
            ".schemasync.json"
        ]

        for filename in possible_files:
            if os.path.exists(filename):
                return filename
        return None

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        config = self.DEFAULT_CONFIG.copy()

        if self.config_path and os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                if self.config_path.endswith(('.yaml', '.yml')):
                    user_config = yaml.safe_load(f) or {}
                else:
                    user_config = json.load(f)

            # Merge user config with defaults
            self._deep_merge(config, user_config)

        # Override with environment variables
        self._apply_env_variables(config)

        return config

    def _deep_merge(self, base: Dict, override: Dict) -> None:
        """Deep merge two dictionaries"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def _apply_env_variables(self, config: Dict[str, Any]) -> None:
        """Apply environment variable overrides"""
        env_mappings = {
            "SCHEMASYNC_DB_DRIVER": ("database", "driver"),
            "SCHEMASYNC_DB_HOST": ("database", "host"),
            "SCHEMASYNC_DB_PORT": ("database", "port"),
            "SCHEMASYNC_DB_NAME": ("database", "name"),
            "SCHEMASYNC_DB_USER": ("database", "user"),
            "SCHEMASYNC_DB_PASSWORD": ("database", "password"),
            "SCHEMASYNC_DB_URL": ("database", "url"),
            "SCHEMASYNC_MIGRATIONS_DIR": ("migrations", "directory"),
            "SCHEMASYNC_LOG_LEVEL": ("logging", "level"),
        }

        for env_var, (section, key) in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                # Convert port to int if needed
                if key == "port" and value:
                    try:
                        value = int(value)
                    except ValueError:
                        continue
                config[section][key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation

        Args:
            key: Configuration key (e.g., 'database.driver')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation

        Args:
            key: Configuration key (e.g., 'database.driver')
            value: Value to set
        """
        keys = key.split('.')
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def save(self, path: Optional[str] = None) -> None:
        """
        Save configuration to file

        Args:
            path: Path to save configuration (defaults to current config path)
        """
        save_path = path or self.config_path or "schemasync.yaml"

        with open(save_path, 'w', encoding='utf-8') as f:
            if save_path.endswith(('.yaml', '.yml')):
                yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)
            else:
                json.dump(self._config, f, indent=2, ensure_ascii=False)

    def get_database_url(self) -> str:
        """Get database connection URL"""
        # Check for explicit URL
        url = self.get('database.url')
        if url:
            return url

        # Build URL from components
        driver = self.get('database.driver', 'sqlite')

        if driver == 'sqlite':
            db_name = self.get('database.name', 'database.db')
            return f"sqlite:///{db_name}"

        host = self.get('database.host', 'localhost')
        port = self.get('database.port')
        name = self.get('database.name', '')
        user = self.get('database.user', '')
        password = self.get('database.password', '')

        if driver == 'postgresql':
            driver = 'postgresql+psycopg2'
        elif driver == 'mysql':
            driver = 'mysql+pymysql'

        if port:
            host = f"{host}:{port}"

        if user and password:
            auth = f"{user}:{password}@"
        elif user:
            auth = f"{user}@"
        else:
            auth = ""

        return f"{driver}://{auth}{host}/{name}"

    def get_migrations_dir(self) -> Path:
        """Get migrations directory path"""
        return Path(self.get('migrations.directory', 'migrations'))

    def get_backup_dir(self) -> Path:
        """Get backup directory path"""
        return Path(self.get('migrations.backup_directory', 'backups'))

    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary"""
        return self._config.copy()

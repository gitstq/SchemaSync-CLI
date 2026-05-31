"""
Migration file operations
"""
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List


class MigrationFile:
    """Represents a single migration file"""

    MIGRATION_TEMPLATE = '''"""
Migration: {version}_{description}
Created: {created_at}
"""

revision = '{version}'
down_revision = {down_revision}


def upgrade():
    """Apply migration"""
    return """
{upgrade_sql}
    """


def downgrade():
    """Revert migration"""
    return """
{downgrade_sql}
    """
'''

    def __init__(self, path: Path):
        """
        Initialize migration file

        Args:
            path: Path to migration file
        """
        self.path = path
        self._metadata = None
        self._module = None

    @property
    def version(self) -> str:
        """Get migration version from filename"""
        # Extract version from filename like: 20250101000001_description.py
        match = re.match(r'^(\d+)_.*\.py$', self.path.name)
        if match:
            return match.group(1)
        return self.path.stem

    @property
    def description(self) -> str:
        """Get migration description from filename"""
        # Extract description from filename
        match = re.match(r'^\d+_(.+)\.py$', self.path.name)
        if match:
            desc = match.group(1)
            return desc.replace('_', ' ')
        return self.path.stem

    def load(self) -> Dict[str, Any]:
        """Load migration module and return metadata"""
        if self._metadata is None:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                f"migration_{self.version}",
                self.path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            self._module = module
            self._metadata = {
                'revision': getattr(module, 'revision', self.version),
                'down_revision': getattr(module, 'down_revision', None),
                'upgrade': getattr(module, 'upgrade', lambda: ''),
                'downgrade': getattr(module, 'downgrade', lambda: '')
            }

        return self._metadata

    def get_upgrade_sql(self) -> str:
        """Get upgrade SQL"""
        metadata = self.load()
        upgrade_func = metadata['upgrade']
        return upgrade_func() if callable(upgrade_func) else upgrade_func

    def get_downgrade_sql(self) -> str:
        """Get downgrade SQL"""
        metadata = self.load()
        downgrade_func = metadata['downgrade']
        return downgrade_func() if callable(downgrade_func) else downgrade_func

    @classmethod
    def create(cls, migrations_dir: Path, description: str,
               upgrade_sql: str = "", downgrade_sql: str = "",
               down_revision: Optional[str] = None) -> 'MigrationFile':
        """
        Create a new migration file

        Args:
            migrations_dir: Directory to create migration in
            description: Migration description
            upgrade_sql: Upgrade SQL
            downgrade_sql: Downgrade SQL
            down_revision: Previous migration version

        Returns:
            New MigrationFile instance
        """
        # Generate version timestamp
        version = datetime.now().strftime('%Y%m%d%H%M%S')

        # Sanitize description for filename
        safe_desc = re.sub(r'[^\w\s-]', '', description).strip()
        safe_desc = re.sub(r'[-\s]+', '_', safe_desc).lower()

        filename = f"{version}_{safe_desc}.py"
        filepath = migrations_dir / filename

        # Format template
        content = cls.MIGRATION_TEMPLATE.format(
            version=version,
            description=safe_desc,
            created_at=datetime.now().isoformat(),
            down_revision=f"'{down_revision}'" if down_revision else 'None',
            upgrade_sql=upgrade_sql or "-- Add your upgrade SQL here",
            downgrade_sql=downgrade_sql or "-- Add your downgrade SQL here"
        )

        # Write file
        filepath.write_text(content, encoding='utf-8')

        return cls(filepath)

    @classmethod
    def from_directory(cls, migrations_dir: Path) -> List['MigrationFile']:
        """
        Load all migration files from directory

        Args:
            migrations_dir: Directory containing migration files

        Returns:
            List of MigrationFile instances sorted by version
        """
        if not migrations_dir.exists():
            return []

        migrations = []
        for file_path in migrations_dir.glob('*.py'):
            if file_path.name.startswith('_'):
                continue
            migrations.append(cls(file_path))

        # Sort by version
        migrations.sort(key=lambda m: m.version)
        return migrations

    def __repr__(self):
        return f"MigrationFile({self.path.name})"

    def __eq__(self, other):
        if isinstance(other, MigrationFile):
            return self.version == other.version
        return False

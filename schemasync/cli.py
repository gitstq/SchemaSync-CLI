"""
Command-line interface for SchemaSync
"""
import os
import sys
from pathlib import Path

import click

from . import __version__, __title__
from .config import Config
from .migration.manager import MigrationManager
from .utils.helpers import print_table


# Custom context class
class Context:
    def __init__(self):
        self.config = None
        self.manager = None


pass_context = click.make_pass_decorator(Context, ensure=True)


def get_manager(ctx: Context) -> MigrationManager:
    """Get or create migration manager"""
    if ctx.manager is None:
        ctx.config = Config()
        ctx.manager = MigrationManager(ctx.config)
    return ctx.manager


@click.group()
@click.version_option(version=__version__, prog_name=__title__)
@click.option('--config', '-c', type=click.Path(), help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, config, verbose):
    """
    SchemaSync-CLI - Database Schema Migration Tool

    A lightweight, developer-friendly tool for managing database schema
    versions and migrations across SQLite, PostgreSQL, and MySQL.

    Examples:
        schemasync init                    # Initialize migration environment
        schemasync create "add users"      # Create new migration
        schemasync status                  # Show migration status
        schemasync migrate                 # Run pending migrations
        schemasync rollback                # Rollback last migration
    """
    # Store options in context
    ctx.ensure_object(Context)
    ctx.obj.config_path = config
    ctx.obj.verbose = verbose

    if verbose:
        click.echo("Verbose mode enabled")


@cli.command()
@click.option('--directory', '-d', type=click.Path(), help='Target directory')
@click.pass_context
def init(ctx, directory):
    """Initialize migration environment"""
    manager = get_manager(ctx.obj)
    manager.init(directory)


@cli.command()
@click.argument('description')
@click.option('--upgrade-sql', default='', help='Upgrade SQL (optional)')
@click.option('--downgrade-sql', default='', help='Downgrade SQL (optional)')
@click.pass_context
def create(ctx, description, upgrade_sql, downgrade_sql):
    """Create a new migration"""
    manager = get_manager(ctx.obj)
    migration = manager.create(description, upgrade_sql, downgrade_sql)

    # Open in editor if no SQL provided
    if not upgrade_sql and not downgrade_sql:
        click.echo(f"\n📝 Edit the migration file to add your SQL:")
        click.echo(f"   {migration.path}")


@cli.command()
@click.pass_context
def status(ctx):
    """Show migration status"""
    manager = get_manager(ctx.obj)
    status_info = manager.status()

    click.echo(f"\n📊 Migration Status")
    click.echo(f"   Total: {status_info['total']}")
    click.echo(f"   Applied: {status_info['applied']}")
    click.echo(f"   Pending: {status_info['pending']}")

    if status_info['migrations']:
        click.echo(f"\n📋 Migrations:")
        rows = []
        for m in status_info['migrations']:
            status_icon = "✅" if m['applied'] else "⏳"
            rows.append([
                status_icon,
                m['version'],
                m['description'][:40]
            ])
        print_table(['Status', 'Version', 'Description'], rows)


@cli.command()
@click.option('--target', '-t', help='Target version')
@click.option('--dry-run', is_flag=True, help='Preview without executing')
@click.pass_context
def migrate(ctx, target, dry_run):
    """Run pending migrations"""
    manager = get_manager(ctx.obj)

    if dry_run:
        click.echo("🔍 Dry run mode - no changes will be made\n")

    results = manager.migrate(target, dry_run)

    if results:
        success_count = sum(1 for r in results if r.get('success'))
        click.echo(f"\n📊 Summary: {success_count}/{len(results)} migrations successful")

        if not dry_run and success_count == len(results):
            click.echo("✅ All migrations applied successfully!")
    else:
        click.echo("ℹ️  No migrations to apply")


@cli.command()
@click.option('--steps', '-s', default=1, help='Number of migrations to rollback')
@click.option('--to', 'target_version', help='Target version to rollback to')
@click.option('--dry-run', is_flag=True, help='Preview without executing')
@click.pass_context
def rollback(ctx, steps, target_version, dry_run):
    """Rollback migrations"""
    manager = get_manager(ctx.obj)

    if dry_run:
        click.echo("🔍 Dry run mode - no changes will be made\n")

    results = manager.rollback(steps, target_version, dry_run)

    if results:
        success_count = sum(1 for r in results if r.get('success'))
        click.echo(f"\n📊 Summary: {success_count}/{len(results)} migrations reverted")

        if not dry_run and success_count == len(results):
            click.echo("✅ Rollback completed successfully!")
    else:
        click.echo("ℹ️  No migrations to rollback")


@cli.command(name='history')
@click.pass_context
def show_history(ctx):
    """Show migration history"""
    manager = get_manager(ctx.obj)
    history = manager.history()

    if not history:
        click.echo("ℹ️  No migration history found")
        return

    click.echo(f"\n📜 Migration History ({len(history)} applied):")
    rows = []
    for h in history:
        rows.append([
            h['version'],
            h['description'][:40],
            h['file'] or '-'
        ])
    print_table(['Version', 'Description', 'File'], rows)


@cli.command()
@click.pass_context
def config(ctx):
    """Show current configuration"""
    cfg = Config(ctx.obj.config_path)

    click.echo("\n⚙️  Current Configuration:")
    click.echo(f"   Config file: {cfg.config_path or 'Using defaults'}")
    click.echo(f"\n   Database:")
    click.echo(f"     Driver: {cfg.get('database.driver')}")
    click.echo(f"     Host: {cfg.get('database.host')}")
    click.echo(f"     Port: {cfg.get('database.port')}")
    click.echo(f"     Name: {cfg.get('database.name')}")
    click.echo(f"\n   Migrations:")
    click.echo(f"     Directory: {cfg.get('migrations.directory')}")
    click.echo(f"     Table: {cfg.get('migrations.table_name')}")
    click.echo(f"     Backup enabled: {cfg.get('migrations.backup_before_migrate')}")


# Entry point
def main():
    """CLI entry point"""
    cli()


if __name__ == '__main__':
    main()

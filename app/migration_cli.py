"""
Beanie Migration CLI Wrapper for Container Environment
Provides easy access to Beanie's official migration system in Docker containers
"""
import os
import sys
import asyncio
from typing import Optional
import click
from pathlib import Path

# Add app directory to Python path for imports
sys.path.append('/app')

from configs import app_conf, sys_conf
from shared.odm import mclient


def get_mongodb_uri() -> str:
    """Get MongoDB URI from environment configuration"""
    # Use the existing MongoDB client configuration
    return mclient.get_uri()


def get_migration_path() -> str:
    """Get absolute path to migrations directory"""
    return "/app/migrations"


@click.group()
def cli():
    """Beanie Migration CLI Wrapper for Container Environment"""
    pass


@cli.command()
@click.argument('name')
@click.option('--description', '-d', default='', help='Migration description')
def new(name: str, description: str):
    """Create a new migration using Beanie's official CLI"""
    migration_path = get_migration_path()
    
    # Ensure migrations directory exists
    Path(migration_path).mkdir(exist_ok=True)
    
    try:
        # Use Beanie's official new-migration command
        import subprocess
        
        cmd = [
            'uv', 'run', 'beanie', 'new-migration',
            '-n', name,
            '-p', migration_path
        ]
        
        click.echo(f"Creating migration: {name}")
        if description:
            click.echo(f"Description: {description}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd='/app')
        
        if result.returncode == 0:
            click.echo("✅ Migration created successfully")
            if result.stdout:
                click.echo(result.stdout)
        else:
            click.echo("❌ Failed to create migration", err=True)
            if result.stderr:
                click.echo(result.stderr, err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Error creating migration: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--distance', '-d', type=int, default=0, 
              help='Number of migrations to run (0 = all)')
@click.option('--backward', '-b', is_flag=True, 
              help='Run migrations backward')
@click.option('--dry-run', '-n', is_flag=True,
              help='Show what would be migrated without executing')
@click.option('--database', '--db', 
              help='Database name (defaults to configured databases)')
def migrate(distance: int, backward: bool, dry_run: bool, database: Optional[str]):
    """Run migrations using Beanie's official CLI"""
    try:
        import subprocess
        
        uri = get_mongodb_uri()
        migration_path = get_migration_path()
        
        # If no specific database is provided, run for all configured databases
        databases = [database] if database else [
            "App-Config", 
            app_conf.userdb, 
            app_conf.malldb, 
            "AiSP-Mission"
        ]
        
        for db_name in databases:
            click.echo(f"\n📊 Processing database: {db_name}")
            
            cmd = [
                'uv', 'run', 'beanie', 'migrate',
                '-uri', uri,
                '-db', db_name,
                '-p', migration_path
            ]
            
            if distance > 0:
                cmd.extend(['--distance', str(distance)])
            
            if backward:
                cmd.append('--backward')
            
            if dry_run:
                click.echo(f"🔍 Dry run mode - would execute: {' '.join(cmd)}")
                continue
            
            click.echo(f"🚀 Running migrations for {db_name}...")
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd='/app')
            
            if result.returncode == 0:
                click.echo(f"✅ Migrations completed for {db_name}")
                if result.stdout:
                    click.echo(result.stdout)
            else:
                click.echo(f"❌ Migration failed for {db_name}", err=True)
                if result.stderr:
                    click.echo(result.stderr, err=True)
                # Don't exit here, continue with other databases
        
        if not dry_run:
            click.echo("\n✅ All database migrations completed")
        
    except Exception as e:
        click.echo(f"❌ Error running migrations: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def status():
    """Show migration status for all databases"""
    try:
        migration_path = get_migration_path()
        
        # List migration files
        migration_files = []
        if Path(migration_path).exists():
            migration_files = sorted([
                f.name for f in Path(migration_path).glob("*.py") 
                if not f.name.startswith("__")
            ])
        
        click.echo("📋 Migration Status")
        click.echo(f"Migration path: {migration_path}")
        click.echo(f"Available migrations: {len(migration_files)}")
        
        if migration_files:
            click.echo("\n📄 Migration files:")
            for migration_file in migration_files:
                click.echo(f"   • {migration_file}")
        else:
            click.echo("\n📝 No migration files found")
        
        # Show configured databases
        databases = [
            "App-Config", 
            app_conf.userdb, 
            app_conf.malldb, 
            "AiSP-Mission"
        ]
        
        click.echo(f"\n🗄️ Configured databases:")
        for db in databases:
            click.echo(f"   • {db}")
        
    except Exception as e:
        click.echo(f"❌ Error getting status: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def init():
    """Initialize migration system (ensure directories exist)"""
    try:
        migration_path = get_migration_path()
        Path(migration_path).mkdir(exist_ok=True)
        
        # Create __init__.py if it doesn't exist
        init_file = Path(migration_path) / "__init__.py"
        if not init_file.exists():
            init_file.write_text("# Beanie ODM Migrations Directory\n")
        
        click.echo(f"✅ Migration system initialized")
        click.echo(f"   Migration path: {migration_path}")
        
    except Exception as e:
        click.echo(f"❌ Error initializing migration system: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
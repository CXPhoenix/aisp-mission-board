"""
Beanie Migration Runner for FastAPI Integration
Programmatically executes Beanie migrations during application startup
"""
import logging
import asyncio
from pathlib import Path
from typing import List, Optional

from beanie.migrations.controllers.iterative import IterativeMigrationController
from beanie.migrations.controllers.free_fall import FreeFallMigrationController
from beanie.migrations.models import MigrationLog, RunningDirections
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from configs import app_conf
from shared.odm import mclient

logger = logging.getLogger(__name__)


class BeanieAutomationMigrationRunner:
    """
    Automated migration runner for Beanie ODM
    Integrates with FastAPI application startup
    """
    
    def __init__(self, migration_path: str = "/app/migrations"):
        self.migration_path = Path(migration_path)
        self.client: Optional[AsyncIOMotorClient] = None
        
    def _get_migration_files(self) -> List[Path]:
        """Get sorted list of migration files"""
        if not self.migration_path.exists():
            return []
        
        migration_files = []
        for file_path in self.migration_path.glob("*.py"):
            if file_path.name.startswith("__"):
                continue
            migration_files.append(file_path)
        
        # Sort by filename (which includes timestamp)
        migration_files.sort(key=lambda x: x.name)
        return migration_files
    
    async def _run_database_migrations(self, database_name: str) -> bool:
        """Run migrations for a specific database"""
        try:
            if not self.client:
                logger.error("MongoDB client not initialized")
                return False
            
            database = self.client[database_name]
            migration_files = self._get_migration_files()
            
            if not migration_files:
                logger.info(f"No migration files found for database {database_name}")
                return True
            
            logger.info(f"Found {len(migration_files)} migration files for {database_name}")
            
            # Initialize migration collection
            await MigrationLog.init_database_connection(database)
            
            # Run iterative migrations
            iterative_controller = IterativeMigrationController(
                database=database,
                migrations_path=str(self.migration_path)
            )
            
            await iterative_controller.run_migrations(
                direction=RunningDirections.FORWARD
            )
            
            # Run free fall migrations
            free_fall_controller = FreeFallMigrationController(
                database=database,
                migrations_path=str(self.migration_path)
            )
            
            await free_fall_controller.run_migrations(
                direction=RunningDirections.FORWARD
            )
            
            logger.info(f"Successfully completed migrations for database {database_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to run migrations for database {database_name}: {str(e)}")
            return False
    
    async def run_all_migrations(self) -> bool:
        """Run migrations for all configured databases"""
        try:
            # Get MongoDB client from mclient
            self.client = mclient.client
            
            # List of databases to migrate
            databases = [
                "App-Config",
                app_conf.userdb,
                app_conf.malldb,
                "AiSP-Mission"
            ]
            
            success_count = 0
            total_databases = len(databases)
            
            for database_name in databases:
                logger.info(f"Running migrations for database: {database_name}")
                
                success = await self._run_database_migrations(database_name)
                if success:
                    success_count += 1
                else:
                    logger.error(f"Migration failed for database: {database_name}")
                    # Continue with other databases even if one fails
            
            if success_count == total_databases:
                logger.info("All database migrations completed successfully")
                return True
            else:
                logger.warning(f"Migrations completed with issues: {success_count}/{total_databases} databases successful")
                return False
                
        except Exception as e:
            logger.error(f"Failed to run migrations: {str(e)}")
            return False
    
    async def check_pending_migrations(self) -> bool:
        """Check if there are pending migrations"""
        try:
            migration_files = self._get_migration_files()
            
            if not migration_files:
                return False
            
            # For simplicity, we'll assume there are pending migrations if files exist
            # In a more sophisticated implementation, we could check against MigrationLog
            logger.info(f"Found {len(migration_files)} migration files")
            return True
            
        except Exception as e:
            logger.error(f"Failed to check pending migrations: {str(e)}")
            return False


# Global migration runner instance
migration_runner = BeanieAutomationMigrationRunner()
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
- `docker-compose up -d` - Start all services (app, TailwindCSS, MongoDB, MongoDB Express, Cloudflare tunnel)
- `docker-compose up app mongo` - Start only app and database for development
- `docker-compose down` - Stop all services

### Development Mode
- TailwindCSS runs in watch mode automatically when using docker-compose
- App directory is mounted as volume for live reloading during development
- Logs are stored in `./data/logs`

### Python Environment
- Uses `uv` for dependency management (see `pyproject.toml`)
- Requires Python >=3.12
- Install dependencies: `uv sync` (if developing locally)

### Testing and Linting
- No specific testing framework configured yet
- No linting tools configured in pyproject.toml
- Manual testing through FastAPI's automatic API docs at `/docs`
- **Important**: When making changes, verify functionality by testing the web interface directly
- **Testing Strategy**: Human testers will handle post-development testing, but you must provide comprehensive test plans

### Database Migration
- **Migration System**: Official Beanie ODM migration functionality
- **Migration Files**: Stored in `app/migrations/` directory following Beanie conventions
- **Auto-execution**: Automatically checks and executes pending migrations on container startup
- **CLI Tools**: Containerized wrapper for official Beanie migration commands

### TailwindCSS Development
- TailwindCSS build command: `pnpm build` (in tailwind_styles directory)
- Watch mode: `pnpx @tailwindcss/cli -i ./src/input.css -o ./dist/style.css --watch`
- Styles are mounted as volume in Docker for live reloading

## Architecture Overview

### Core Framework
- **FastAPI** web application with custom error handling and routing
- **Beanie ODM** for MongoDB operations with multiple database connections
- **Jinja2** templates for server-side rendering
- **TailwindCSS** for styling (built via separate Docker container)

### Application Structure
```
app/
├── main.py              # FastAPI app entry point with lifespan management
├── configs/             # Configuration classes and settings
├── models/              # Beanie ODM models (User, Mission, Product, etc.)
├── pages/               # Route handlers organized by feature
│   ├── auth_pages.py    # Authentication routes
│   ├── mission_pages.py # Mission management
│   ├── mall_pages.py    # Shopping/product features
│   ├── user_pages.py    # User management
│   └── admin_pages/     # Admin functionality (modularized)
├── shared/              # Common utilities and middleware
│   ├── odm.py          # MongoDB client and connection management
│   ├── sessions.py     # Session middleware
│   ├── dependencies.py # FastAPI dependencies
│   └── webpage.py      # Template rendering utilities
├── templates/          # Jinja2 HTML templates
└── public/            # Static assets (CSS, JS, images)
```

### Database Architecture
- **Multiple MongoDB databases** managed through `MongoDbClient` class in `app/shared/odm.py`
- Databases: `userdb`, `malldb`, `recorddb`, `AiSP-Mission`, `App-Config`
- Models are organized by feature: User, Mission, Product, TransactionRecord, etc.
- Database connections initialized during FastAPI lifespan with specific collections per database
- Each model specifies its collection name through Beanie settings
- **Connection Pattern**: Database connections are established in `main.py` lifespan function

### Key Design Patterns
- **ODM with Beanie**: All models inherit from Beanie Document for MongoDB operations
- **Dependency Injection**: FastAPI dependencies for authentication and database access
- **Template-based Rendering**: Server-side HTML generation with Jinja2
- **Session-based Authentication**: Custom session middleware for user management
- **Admin Role System**: Role-based access control with admin user initialization

### Environment Configuration
- Environment variables stored in `env.d/` directory
- Separate configs for app, MongoDB, MongoDB Express, and Cloudflare
- Configuration classes in `app/configs/` handle settings management

### Docker Setup
- Multi-service architecture with Docker Compose
- Services: `app` (FastAPI), `tw` (TailwindCSS), `mongo` (MongoDB), `me` (Mongo Express), `cf` (Cloudflare tunnel)
- Development vs production command variations for TailwindCSS
- Volume mounts for live development and persistent data
- Health checks configured for MongoDB service
- Internal networks for security isolation

## Writing Guidelines

### Commit Messages
- **Use commit emojis** for better visual representation of changes
- **Write detailed commit messages** explaining what was changed and why
- **Use English** for all descriptions and explanations
- **Keep technical terms in original language** (e.g., FastAPI, MongoDB, Docker)
- Follow conventional commit format with emoji prefixes

### README Documentation
- **Use commit emojis** to organize sections and features
- **Write in English** for all content
- **Preserve technical terms** in their original language
- Focus on clear explanations for developers
- Include practical examples and usage instructions

## Important Development Notes

### Security Considerations
- Session-based authentication using JWT tokens
- Password hashing with bcrypt
- Role-based access control (USER, MANAGER, ADMIN)
- Environment variables for sensitive configuration
- OpenAPI documentation disabled in production (DOCS_URL=None)

### Multi-Database Design
- Each database serves specific domain purposes
- Cross-database relationships managed through Beanie's Link/BackLink
- Connection pooling handled by MongoDbClient class
- **Database Initialization**: Admin users are automatically promoted during app startup

### Error Handling
- Custom HTTP exception handler with localized error pages
- Template-based error responses with return navigation
- Static file serving with cache-busting for development

### Current Development Status
- Core user and mission management: ✅ Complete
- Admin interface: ✅ Complete
- Virtual mall system: ✅ Complete (including physical product requests)
- Achievement system: 🚧 Planned (badge.py model exists but not integrated)
- Testing framework: ❌ Not configured

### Service Access Points
- Main app: `http://localhost:8000`
- MongoDB Express: `http://localhost:8081`
- API documentation: `http://localhost:8000/docs` (disabled in production)
- ReDoc: `http://localhost:8000/redoc` (disabled in production)

### Logging Configuration
- Log configuration managed through `app/log_config.yaml`
- Logs stored in `./data/logs/` directory
- Rotating file handlers with 10MB max size and 5 backup files
- Separate handlers for application events and access logs
- Custom UTC+8 formatters for Taiwan timezone

### Environment Setup
- Environment files in `env.d/` directory with `.example` templates
- Required environment variables:
  - `MONGODB_*`: Database connection settings
  - `SYSTEM_SESSION_SECRET`: Session encryption key
  - `APP_*`: Application configuration (databases, admin users)
- Admin users configured via `APP_ADMINS` environment variable (colon-separated)

## Development Best Practices

### Code Editing Guidelines
- Always read existing code patterns before making changes
- Follow the existing routing structure in `pages/` directory
- Use the established ODM patterns from `models/` directory
- Maintain consistency with the existing template structure

### Database Operations
- Always use Beanie ODM for database operations
- Reference the `MongoDbClient` class in `shared/odm.py` for connection patterns
- Follow the multi-database architecture when creating new models
- Use appropriate database for each domain (user data → userdb, products → malldb, etc.)

### Template Development
- All templates extend `base.html`
- Use the `WebPage` utility class from `shared/webpage.py` for consistent rendering
- Follow the established pattern of organizing templates by feature in subdirectories
- Maintain the TailwindCSS + Flowbite component structure

### Migration Management

#### Using Official Beanie CLI (Recommended)
- **Creating new migrations**:
  ```bash
  # Create new migration using official Beanie CLI
  docker-compose exec app uv run beanie new-migration -n <migration_name> -p /app/migrations
  ```

- **Running migrations**:
  ```bash
  # Run migrations for specific database
  docker-compose exec app uv run beanie migrate -uri mongodb://user:pass@mongo:27017 -db <database_name> -p /app/migrations
  
  # Run with distance limit
  docker-compose exec app uv run beanie migrate -uri mongodb://user:pass@mongo:27017 -db <database_name> -p /app/migrations --distance 1
  
  # Run backward migrations
  docker-compose exec app uv run beanie migrate -uri mongodb://user:pass@mongo:27017 -db <database_name> -p /app/migrations --backward
  ```

#### Using Container CLI Wrapper
- **Creating new migrations**:
  ```bash
  # Use our container wrapper
  docker-compose exec app uv run python -m app.migration_cli new <migration_name>
  ```

- **Running migrations**:
  ```bash
  # Run migrations for all configured databases
  docker-compose exec app uv run python -m app.migration_cli migrate
  
  # Run with specific options
  docker-compose exec app uv run python -m app.migration_cli migrate --database userdb --distance 1
  
  # Dry run to see what would be executed
  docker-compose exec app uv run python -m app.migration_cli migrate --dry-run
  ```

- **Checking migration status**:
  ```bash
  # Show migration files and database configuration
  docker-compose exec app uv run python -m app.migration_cli status
  
  # Initialize migration system
  docker-compose exec app uv run python -m app.migration_cli init
  ```

### Migration Development Workflow
1. **Modify models**: Edit your Beanie ODM models in `app/models/`
2. **Create migration**: Use Beanie CLI to create migration files with proper timestamp naming
3. **Implement migration**: Edit the generated migration file using official Forward/Backward class structure
4. **Test migration**: Test migration correctness in development environment using CLI tools
5. **Deploy**: Container restart will automatically execute pending migrations

### Migration Structure (Beanie Official)
All migrations follow the official Beanie structure with Forward and Backward classes:

```python
# Example: 20241207_120000_migration_name.py
from beanie import iterative_migration

class Forward:
    @iterative_migration()
    async def migration_method(self, input_document: OldModel, output_document: NewModel):
        # Forward migration logic
        output_document.new_field = input_document.old_field

class Backward:
    @iterative_migration()
    async def rollback_method(self, input_document: NewModel, output_document: OldModel):
        # Backward migration logic
        output_document.old_field = input_document.new_field
```

### Migration Types
- **Iterative Migration**: Uses `@iterative_migration()` decorator, processes documents one by one
- **Free Fall Migration**: Uses `@free_fall_migration()` decorator, supports complex operations with session/transaction

### Important Notes
- The application uses server-side rendering with Jinja2 templates
- All user-facing content should be in Traditional Chinese (Taiwan)
- Testing must be done through the web interface as no automated testing framework is configured
- Always verify database connections and model relationships when making changes
- **Migration System**: Uses official Beanie ODM migration framework with Forward/Backward class structure
- **Auto-execution**: Migrations run automatically on container startup via `migration_runner.py`
- **Container Environment**: Migrations work in Docker containers using `uv` package management
- **CLI Access**: Both official Beanie CLI and custom wrapper available for migration management
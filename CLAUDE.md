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
- **Multiple MongoDB databases** managed through `MongoDbClient` class
- Databases: `userdb`, `malldb`, `recorddb`, `AiSP-Mission`, `App-Config`
- Models are organized by feature: User, Mission, Product, TransactionRecord, etc.
- Database connections initialized during FastAPI lifespan with specific collections per database

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
- Separate containers for app, TailwindCSS building, MongoDB, and utilities
- Development vs production command variations for TailwindCSS
- Volume mounts for live development and persistent data
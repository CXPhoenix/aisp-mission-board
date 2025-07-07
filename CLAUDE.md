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
- Services: `app` (FastAPI), `tw` (TailwindCSS), `mongo` (MongoDB), `me` (Mongo Express), `cf` (Cloudflare tunnel)
- Development vs production command variations for TailwindCSS
- Volume mounts for live development and persistent data
- Health checks configured for MongoDB service
- Internal networks for security isolation

## Writing Guidelines

### Commit Messages
- **Use commit emojis** for better visual representation of changes
- **Write detailed commit messages** explaining what was changed and why
- **Use Traditional Chinese (Taiwan)** for all descriptions and explanations
- **Keep technical terms in original language** (e.g., FastAPI, MongoDB, Docker)
- Follow conventional commit format with emoji prefixes

### README Documentation
- **Use commit emojis** to organize sections and features
- **Write in Traditional Chinese (Taiwan)** for all content
- **Preserve technical terms** in their original language
- Focus on clear explanations for Taiwan-based developers
- Include practical examples and usage instructions

## Important Development Notes

### Security Considerations
- Session-based authentication using JWT tokens
- Password hashing with bcrypt
- Role-based access control (USER, MANAGER, ADMIN)
- Environment variables for sensitive configuration

### Multi-Database Design
- Each database serves specific domain purposes
- Cross-database relationships managed through Beanie's Link/BackLink
- Connection pooling handled by MongoDbClient class

### Current Development Status
- Core user and mission management: ✅ Complete
- Admin interface: ✅ Complete
- Virtual mall system: 🚧 In development
- Achievement system: 🚧 Planned
- Testing framework: ❌ Not configured

### Service Access Points
- Main app: `http://localhost:8000`
- MongoDB Express: `http://localhost:8081`
- API documentation: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
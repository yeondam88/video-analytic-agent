# Configuration System

This directory contains the configuration system for the application. The configuration is based on Pydantic settings and follows a modular approach for better organization and maintainability.

## Structure

```
config/
├── __init__.py      # Main settings entry point
├── api.py           # API server settings
├── database.py      # Database connection settings
├── services.py      # External services settings
├── storage.py       # File storage settings
└── README.md        # This file
```

## Usage

Import the settings from the main entry point:

```python
from src.config import settings

# Access settings by category
db_url = settings.database.get_sqlalchemy_url()
api_host = settings.api.HOST
storage_path = settings.storage.storage_dir
openai_key = settings.services.OPENAI_API_KEY
```

## Settings Categories

### API Settings (api.py)

- Server configuration (host, port, workers)
- CORS settings
- API metadata
- Rate limiting
- Circuit breaker
- Pagination
- Cache settings

### Database Settings (database.py)

- PostgreSQL connection settings
- Connection pool configuration
- SQLAlchemy URL construction

### Storage Settings (storage.py)

- File storage paths
- Storage limits
- Cleanup configuration
- Path validation and creation

### Services Settings (services.py)

- Supabase configuration
- OpenAI settings
- Deepgram settings
- Feature flags

## Environment Variables

Settings can be configured through environment variables or a `.env` file. See each settings module for the specific variables it uses.

Example `.env` file:

```env
# API
API_HOST=0.0.0.0
API_PORT=8000

# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=secret
DB_NAME=video_analytics

# Storage
MAX_STORAGE_GB=5.0
CLEANUP_DAYS=7

# Services
OPENAI_API_KEY=sk-...
DEEPGRAM_API_KEY=...
SUPABASE_URL=...
SUPABASE_KEY=...
```

## Adding New Settings

1. Create a new settings class in the appropriate module
2. Use Pydantic's Field with description and validation
3. Add the new settings class to the main Settings class in `__init__.py`
4. Update this documentation

## Best Practices

1. Always use type hints and Field descriptions
2. Provide sensible defaults where possible
3. Use environment variables for sensitive data
4. Document all settings in code and this README
5. Keep settings modular and organized by category
6. Use validation for complex settings
7. Include examples in documentation

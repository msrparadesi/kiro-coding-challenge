# Events API - Python Documentation

This directory contains auto-generated API documentation for the Events API backend, created using [pdoc](https://pdoc.dev/).

## Viewing the Documentation

Open `index.html` in your web browser to view the complete API documentation.

## What's Included

- **Module Documentation**: Complete documentation for all Python modules
- **Class Documentation**: Detailed information about Pydantic models and classes
- **Function Documentation**: API endpoints, database operations, and utility functions
- **Type Annotations**: Full type information for all functions and methods
- **Cross-References**: Clickable links between related components
- **Search**: Built-in search functionality for quick navigation

## Regenerating Documentation

To regenerate this documentation after code changes:

```bash
# From the backend directory
./generate-docs.sh
```

Or manually:
```bash
pdoc app -o docs
```

## Documentation Structure

- `index.html` - Main entry point
- `app.html` - App module overview
- `app/` - Individual module documentation
  - `main.html` - FastAPI application and routes
  - `models.html` - Pydantic models and validation
  - `database.html` - DynamoDB operations
  - `config.html` - Configuration settings
  - `exceptions.html` - Error handling
  - `validators.html` - Custom validators
- `search.js` - Search functionality

## About pdoc

pdoc is a lightweight documentation generator that:
- Extracts documentation from Python docstrings
- Supports type annotations
- Generates clean, responsive HTML
- Provides automatic cross-referencing
- Requires no configuration

Learn more at [pdoc.dev](https://pdoc.dev/)

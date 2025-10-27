# pa-square

A passive aggressive (PA) personal assistant (PA) Discord bot to help keep track of to-do list items.

## Description

PA-Square utilizes the Habitica API to keep track of your to-do list. Bot users can perform CRUD operations on items in their Habitica to-do list. The bot is built using Python's asyncio framework for efficient concurrent operations.

- **Habitica API Documentation**: https://habitica.com/apidoc/#api-_header
- **Claude API Documentation**: https://docs.anthropic.com/en/api/overview#examples (for passive aggressive reminders)

## Project Structure

```
pa-square/
├── src/
│   └── pa_square/              # Main application package
│       ├── __init__.py         # Package initialization
│       ├── __main__.py         # Entry point for python -m pa_square
│       ├── main.py             # Main bot runner
│       ├── config.py           # Configuration management
│       ├── bot/                # Discord bot commands and events
│       │   ├── __init__.py
│       │   ├── commands.py     # Bot command handlers
│       │   └── events.py       # Bot event handlers
│       ├── habitica/           # Habitica API integration
│       │   ├── __init__.py
│       │   ├── manager.py      # Habitica API manager
│       │   └── constants.py    # API endpoint constants
│       └── utils/              # Utility modules
│           ├── __init__.py
│           └── keep_alive.py   # Keep-alive server
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── habitica/               # Habitica tests
│   │   ├── __init__.py
│   │   └── test_manager.py
│   ├── bot/                    # Bot tests
│   │   └── __init__.py
│   └── utils/                  # Utils tests
│       └── __init__.py
├── pyproject.toml              # Project configuration and dependencies
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Production dependencies
├── .env                        # Environment variables (not in git)
├── .gitignore                  # Git ignore patterns
└── README.md                   # This file
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pa-square
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .[dev]  # Includes dev dependencies
# or
pip install -r requirements.txt  # Production only
```

4. Configure environment variables:
Create a `.env` file in the root directory:
```env
DISCORD_TOKEN=your_discord_token
HABITICA_BASE_URL=https://habitica.com/api/v3
HABITICA_USER=your_habitica_username
HABITICA_PW=your_habitica_password
APPLICATION_NAME=pa-square
```

## Usage

Run the bot using one of these methods:

```bash
# As a module
python -m pa_square

# Using the entry point (after installation)
pa-square

# Directly
python src/pa_square/main.py
```

## Development

### Running Tests

```bash
pytest
# With coverage
pytest --cov=pa_square --cov-report=html
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

## Architecture

This project follows Python best practices for asyncio applications:

- **src-layout**: Package code lives in `src/pa_square/` for clean imports
- **Async-first**: Built on asyncio with aiohttp for concurrent API calls
- **Modular design**: Separation of concerns (bot, habitica, utils)
- **Type hints**: Comprehensive type annotations throughout
- **Testing**: Pytest with async support and mocking
- **Configuration**: Centralized config management with validation

## License

MIT

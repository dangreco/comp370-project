# Onboarding Guide

Welcome to the COMP 370 Seinfeld Script Analysis project! This guide will help you
get started with development.

## Prerequisites

This project uses **Nix** for development environment management. You'll need to
install Nix on your system:

### Installing Nix

<!-- markdownlint-disable line-length -->

```bash
# Linux/macOS with the Determinate Systems installer (recommended)
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install

# Or use the official installer
sh <(curl -L https://nixos.org/nix/install) --daemon
```

<!-- markdownlint-enable line-length -->

For more information, visit [the Nix installation guide](https://nixos.org/download.html).

### Enabling Flakes (if using official installer)

Add the following to `~/.config/nix/nix.conf`:

```conf
experimental-features = nix-command flakes
```

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/dangreco/comp370-project.git
cd comp370-project
```

### 2. Enter the Development Environment

```bash
nix develop
```

This will automatically set up all necessary dependencies including:

- Python 3.13
- uv (Python package manager)
- Task (task runner)
- Development tools (linters, formatters, etc.)
- LaTeX tools

### 3. Seed the Database

The project requires initial data to be scraped and loaded:

```bash
task seed
```

This will:

- Remove any existing database
- Scrape Seinfeld episode data from IMSDB
- Populate the SQLite database with episode metadata and scripts

**Note**: This process may take a few minutes as it scrapes data from the web.

### 4. Run the Development Server

```bash
task run
```

The GraphQL API will be available at:

- API endpoint: <http://localhost:8000/graphql>
- GraphiQL playground: <http://localhost:8000/graphiql>

## Development Workflow

### Available Tasks

The project uses [Task](https://taskfile.dev) for common operations. View all
available tasks:

```bash
task --list
```

Common tasks include:

- `task run` - Start the development server
- `task test` - Run all tests
- `task check` - Check for linting/formatting errors
- `task fix` - Auto-fix linting/formatting issues
- `task seed` - Reseed the database
- `task build` - Build the project (including LaTeX documentation)
- `task clean` - Clean build artifacts

### Code Quality

Before committing, ensure your code passes all checks:

```bash
task check
```

Auto-fix formatting issues:

```bash
task fix
```

### Testing

Run the test suite:

```bash
task test
```

### Pre-commit Hooks

The project uses Husky for pre-commit hooks. These are automatically installed when
you enter the Nix development environment. The hooks will:

- Run linting checks
- Format code
- Run tests

## Project Structure

```text
.
├── src/
│   └── comp370/           # Main application code
│       ├── db/            # Database models and client
│       ├── gql/           # GraphQL schema and resolvers
│       ├── scraper/       # Web scraping client
│       └── main.py        # Application entry point
├── scripts/
│   └── python/
│       ├── seed.py        # Database seeding script
│       └── test.py        # Test script
├── docs/
│   └── report/            # LaTeX documentation
├── public/
│   └── graphiql/          # GraphiQL web interface
├── data/                  # SQLite database and cache files
├── docker/
│   └── Dockerfile         # Container image definition
├── .github/
│   └── workflows/         # CI/CD workflows
└── tasks/                 # Task definitions
```

## Technology Stack

### Backend

- **Python 3.13** - Programming language
- **FastAPI** - Web framework
- **Starlette** - ASGI toolkit
- **GraphQL (Graphene)** - API query language
- **SQLAlchemy** - ORM
- **BeautifulSoup4** - HTML parsing for web scraping
- **requests-cache** - HTTP caching

### Development Tools

- **uv** - Fast Python package manager
- **Task** - Task runner
- **Ruff** - Python linter and formatter
- **pytest** - Testing framework
- **Nix** - Development environment management

### Deployment

- **Docker/Podman** - Container runtime
- **GitHub Actions** - CI/CD

## Docker Usage

### Build the Container

```bash
task docker:build
# or with Podman
task podman:build
```

### Run the Container

```bash
task docker:run
# or with Podman
task podman:run
```

The application will be available at <http://localhost:8000>.

## GraphQL API

### Example Queries

Once the server is running, visit the GraphiQL playground at
<http://localhost:8000/graphiql> to explore the API.

Example query to get first episode:

```graphql
query {
  episode(season: 1, number: 1) {
    title
  }
}
```

## Contributing

1. Create a new branch for your feature/fix
2. Make your changes
3. Run `task check` to ensure code quality
4. Run `task test` to ensure tests pass
5. Commit your changes (pre-commit hooks will run automatically)
6. Push your branch and create a pull request

## Troubleshooting

### "Command not found" errors

Make sure you're in the Nix development environment:

```bash
nix develop
```

### Database issues

Try reseeding the database:

```bash
task seed
```

### Cache issues

Clear the requests cache:

```bash
rm -rf data/requests.db
```

### Nix build issues

Update flake inputs:

```bash
nix flake update
```

## Additional Resources

- [Python Documentation](https://docs.python.org/3/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [GraphQL Documentation](https://graphql.org/)
- [Nix Documentation](https://nixos.org/manual/nix/stable/)
- [Task Documentation](https://taskfile.dev/)
- [uv Documentation](https://docs.astral.sh/uv/)

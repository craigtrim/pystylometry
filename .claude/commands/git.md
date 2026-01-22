# Git Context

Handle git operations for stylometry-ttr repository based on the user's instructions.

**User Instructions:** $ARGUMENTS

## Repository Structure

```
/Users/craigtrim/git/stylometry-ttr/
├── stylometry_ttr/      # Main package
│   ├── __init__.py      # Public API (compute_ttr, tokenize)
│   ├── models.py        # Pydantic models (TTRResult, TTRAggregate)
│   ├── tokenizer.py     # Text tokenization
│   └── ttr.py           # TTR computation
├── tests/               # Test suite
│   ├── data/            # Test fixtures
│   └── test_ttr.py      # Unit and integration tests
├── pyproject.toml       # Poetry config
├── Makefile             # Build commands
└── README.md            # Documentation
```

## Git Configuration

```bash
git config --global user.name "Craig Trim"
git config --global user.email "craigtrim@gmail.com"
```

## Commit Message Format

Use conventional commit prefixes:
- `feat:` - New feature or metric
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code restructuring
- `test:` - Test additions or changes
- `chore:` - Maintenance tasks

**Examples:**
- `feat: Add moving average TTR metric`
- `fix: Handle empty token list edge case`
- `docs: Update README with usage examples`
- `refactor: Simplify STTR computation loop`
- `test: Add tests for unicode normalization`

## Commit Rules

- **No Co-Authored-By lines** - Do not include co-author attributions
- **Atomic commits** - One logical change per commit
- **Descriptive messages** - Reflect the actual work done

## Chunking Large Commits

When changes span multiple areas, break them into logical commits:

**Split by module:**
- Tokenizer changes get their own commits
- TTR computation changes get their own commits
- Model changes get their own commits
- Test changes can accompany their related code or be separate

**Split by nature of change:**
- New features separate from bug fixes
- Refactoring separate from new functionality
- Documentation separate from code changes

**Logical groupings (commit together):**
- A new metric and its tests
- A bug fix and its regression test
- Related model fields that work together

## Checking for Changes

```bash
# All changes
git status
git diff HEAD

# Specific module
git status -- stylometry_ttr/ttr.py
git diff HEAD -- stylometry_ttr/

# Tests only
git status -- tests/
```

## Staging Changes

```bash
# Single file
git add stylometry_ttr/ttr.py

# Entire package
git add stylometry_ttr/

# Tests
git add tests/
```

## Creating Commits

```bash
git commit -m "prefix: Commit message here"
```

## Verifying Commits

```bash
git log -1 --oneline
```

## Development Workflow

Before committing:
1. Run `make lint` to check code style
2. Run `make test` to verify all tests pass
3. Stage and commit changes

## Instructions

Follow the user's instructions in `$ARGUMENTS`. This may include:
- Committing specific changes
- Checking what has changed
- Creating commits with specific messages
- Reviewing recent commit history

Always check for changes before attempting to commit. If no changes exist, inform the user and stop.

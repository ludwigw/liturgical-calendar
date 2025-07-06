# Testing

## Test Suite Structure
- `tests/unit/`: Unit tests for individual modules/classes (fast, isolated, use mocks/stubs)
- `tests/integration/`: Integration and end-to-end tests (full workflows, real data, script entry points)
- `tests/fixtures/`: Sample data for use in tests

## Running Tests
- All tests: `PYTHONPATH=. python -m unittest discover -s tests -p 'test*.py' -v`
- Only unit: `PYTHONPATH=. python -m unittest discover -s tests/unit -p 'test*.py' -v`
- Only integration: `PYTHONPATH=. python -m unittest discover -s tests/integration -p 'test*.py' -v`

## Adding New Tests
- Place new unit tests in `tests/unit/`, integration tests in `tests/integration/`.
- Name files as `test_*.py` and classes as `Test*` for discovery.
- Use `unittest` framework (not pytest).
- Use fixtures for reusable sample data.
- Cover edge cases and reference `docs/liturgical_logic.md` for tricky logic.

## Best Practices
- Write tests before or alongside new features.
- Keep tests isolated and fast where possible.
- Use mocks/stubs for external dependencies in unit tests.
- Ensure all tests pass before committing (see project rules).

## Coverage and Edge Cases
- The suite covers all major logic, including:
  - Season and week calculation
  - Readings selection and precedence
  - Artwork selection and caching
  - Image generation pipeline
- Edge cases (e.g., Pre-Lent, Christmas, variable week numbers) are tested (see `docs/liturgical_logic.md`).

## See Also
- `README.md` and `docs/architecture.md` for quick commands and rationale.
- `docs/liturgical_logic.md` for logic details and edge case rationale.
- `docs/examples/` for runnable test and usage examples.

# Linting, Pre-Commit Hooks, and Code Quality

## Linting Policy

- All code must pass **pylint** with a score of 10.00/10.
- All standard pylint checks are enabled, except for a small number of justified disables (see `.pylintrc`).
- No warnings or errors are allowed in CI or before merging.

### Running Pylint

To check code quality locally:

```sh
pylint liturgical_calendar/
```

You should see a score of 10.00/10 and no warnings or errors.

## Pre-Commit Hooks

This project uses [pre-commit](https://pre-commit.com/) to enforce code quality and formatting before every commit.

### What the hooks do:

- **black**: Auto-formats code for consistency.
- **isort**: Sorts imports.
- **autoflake**: Removes unused imports and variables.
- **pylint**: Runs all lint checks.
- **Run all tests**: Ensures the full test suite passes.

### How to set up:

1. Install pre-commit (once):
   ```sh
   pip install pre-commit
   ```
2. Install the hooks (once per clone):
   ```sh
   pre-commit install
   ```
3. (Optional) Run all hooks manually:
   ```sh
   pre-commit run --all-files
   ```

### Troubleshooting

- If a hook fails, fix the reported issues and re-commit.
- If black reformats files, `git add` the changes and re-commit.
- If tests fail, run them locally and fix any issues before committing.

## Code Quality Standards

- All code must be clean, readable, and maintainable.
- No unused variables, arguments, or imports.
- All exceptions must be specific (no broad `except Exception`).
- All logging must use parameterized style (no f-strings in logging).
- All modules and functions must have docstrings.
- All code must be covered by tests.

For more, see the [README](../README.md) and [Architecture Overview](architecture.md).

## Continuous Integration (CI)

This project uses GitHub Actions for CI:

- **test.yml**: Runs all tests, pylint, and CLI checks on every push and pull request (Python 3.11 & 3.12).
- **integration.yml**: Runs all integration tests and CLI commands.
- **publish.yml**: On release, bumps the Poetry version, builds, and uploads the package.

**All code must pass these checks before merging.**

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

(Work in progress) 
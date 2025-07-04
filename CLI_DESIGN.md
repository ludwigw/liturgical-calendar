# Liturgical Calendar Project - CLI Design Plan

## Goals
- Provide a single, unified command-line interface (`litcal`) for all major project functions.
- Make the CLI discoverable, user-friendly, and self-documenting (with `--help`).
- Support all current script functionality (image generation, artwork caching, liturgical info lookup, config validation, etc.).
- Allow for easy extension (e.g., new subcommands, options).
- Integrate with the existing logging and config system, including `--verbose`.
- Remain compatible with Raspberry Pi/e-ink and headless environments.

## Status: ✅ **COMPLETED**

- The CLI is fully implemented as `python -m liturgical_calendar.cli` (or `litcal` if installed as a script).
- All planned subcommands are live: `generate`, `info`, `cache-artwork`, `validate-config`, `version`.
- Global options `--config` and `--verbose` are supported.
- All legacy scripts are now superseded by the CLI.
- See the README for up-to-date usage and examples.

## Usage Examples
```sh
python -m liturgical_calendar.cli generate 2024-12-25 --output christmas.png --verbose
python -m liturgical_calendar.cli cache-artwork --config myconfig.yaml
python -m liturgical_calendar.cli info 2024-12-25
python -m liturgical_calendar.cli validate-config
python -m liturgical_calendar.cli version
```

## Proposed Structure

### 1. CLI Entrypoint
- **File:** `liturgical_calendar/cli.py` (or as a `__main__.py`)
- **Installable Script:** Add a `console_scripts` entry in `pyproject.toml`/`setup.py` for `litcal`.

### 2. Subcommands
Use a subcommand-based CLI (via `argparse`):

- `litcal generate [DATE] [--config CONFIG] [--output PATH] [--verbose]`
  - Generate a liturgical image for a given date (default: today).
- `litcal cache-artwork [--config CONFIG] [--verbose]`
  - Download/cache all artwork images.
- `litcal info [DATE] [--config CONFIG] [--verbose]`
  - Print liturgical info (season, feast, readings) for a date.
- `litcal validate-config [--config CONFIG] [--verbose]`
  - Validate the current config file and print any issues.
- `litcal version`
  - Print version and exit.

### 3. Global Options
- `--config CONFIG` (path to config file)
- `--verbose` (set log level to DEBUG)
- `--help` (show help for any command)

### 4. Help and Usage
- `litcal --help` shows all subcommands and global options.
- `litcal <subcommand> --help` shows options for that subcommand.

### 5. Implementation Notes
- Use `argparse.ArgumentParser` with subparsers for subcommands.
- Each subcommand calls into the appropriate service/module (reuse existing logic).
- Logging is initialized at the top, with log level set by `--verbose`.
- Config is loaded once at startup, passed to all subcommands.
- Exit codes: 0 for success, nonzero for errors.

## Extensibility
- New subcommands (e.g., `compare-lectionaries`, `list-feasts`) can be added easily.
- Can be wrapped for use in other scripts or GUIs.

## Next Steps
- [x] Confirm this design or suggest changes (e.g., command names, options).
- [x] Implement the CLI entrypoint and subcommands.
- [x] Update documentation (README, architecture.md) with usage examples.
- [x] Add/adjust tests for CLI behavior. 
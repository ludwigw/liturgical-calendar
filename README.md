# Liturgical Calendar

## Features

- Calculates Anglican liturgical seasons, feasts, and colors for any date
- Generates images for e-ink or digital displays
- Centralized, extensible configuration (YAML/env)
- Raspberry Pi & e-ink display support
- Fully tested with `unittest`
- Modular, maintainable codebase

## Quickstart

Generate today's liturgical image with default settings:

```sh
python -m liturgical_calendar.cli generate
```

Or get liturgical info for today at the command line:

```sh
liturgical_calendar
```

## Command-Line Interface (CLI)

The project now provides a unified CLI for all major functions. You can run it as:

```sh
python -m liturgical_calendar.cli [subcommand] [options]
```

Or, if installed as a script:

```sh
litcal [subcommand] [options]
```

### Subcommands

- `generate [DATE] [--output PATH] [--config CONFIG] [--verbose]`  
  Generate a liturgical image for a given date (default: today).
- `info [DATE] [--config CONFIG] [--verbose]`  
  Print liturgical info (season, feast, readings) for a date.
- `cache-artwork [--config CONFIG] [--verbose]`  
  Download/cache all artwork images.
- `validate-config [--config CONFIG] [--verbose]`  
  Validate the current config file and print any issues.
- `version`  
  Print version and exit.

### Global Options
- `--config CONFIG` (path to config file)
- `--verbose` (set log level to DEBUG)
- `--help` (show help for any command)

### Example Usage

```sh
python -m liturgical_calendar.cli generate 2024-12-25 --output christmas.png --verbose
python -m liturgical_calendar.cli info 2024-12-25
python -m liturgical_calendar.cli cache-artwork
python -m liturgical_calendar.cli validate-config
python -m liturgical_calendar.cli version
```

See the [Architecture Overview](docs/architecture.md) for design details and advanced usage.

**Note:** The CLI provides a unified interface for all project functionality. Use the CLI for all workflows.

## Documentation

- [Architecture Overview](docs/architecture.md)
- [Liturgical Logic & Edge Cases](docs/liturgical_logic.md)
- [API Reference](docs/api_reference.md)
- [Image Generation](docs/image_generation.md)
- [Caching](docs/caching.md)
- [Testing](docs/testing.md)
- [Raspberry Pi & E-Ink Integration](docs/raspberry_pi_eink.md)
- [Example Scripts](docs/examples/)

---

This Python module will return the name, season, week number and liturgical
colour for any day in the Gregorian calendar, according to the Anglican
tradition of the Church of England.



The output of this module is compared against the
[Church of England Lectionary](https://www.chpublishing.co.uk/features/lectionary),
which is taken to be the canonical source.

## Background

Some churches use a special church calendar. Days and seasons within the year
may be either "fasts" (solemn times) or "feasts" (joyful times). The year is
structured around the greatest feast in the calendar, the festival of the
Resurrection of Jesus, known as Easter, and the second greatest feast, the
festival of the Nativity of Jesus, known as Christmas. Before Christmas and
Easter there are solemn fast seasons known as Advent and Lent respectively.
After Christmas comes the feast of Epiphany, and after Easter comes the feast
of Pentecost. These days have the adjacent seasons named after them.

The church's new year falls on Advent Sunday, which occurs around the start of
December. Then follows the four-week fast season of Advent, then comes the
Christmas season, which lasts twelve days; then comes Epiphany, then the
forty days of Lent. Then comes Easter, then the long season of Pentecost
(which some churches call Trinity, after the feast which falls soon after
Pentecost). Then the next year begins and we return to Advent again.

Along with all these, the church remembers the women and men who have made
a positive difference in church history by designating feast days for them,
usually on the anniversary of their death. For example, we remember St. Andrew
on the 30th day of November in the Western churches. Every Sunday is the feast
day of Jesus, and if it has no other name is numbered according to the
season in which it falls. So, for example, the third Sunday in Pentecost
season would be called Pentecost 3.

Seasons are traditionally assigned colours, which are used for clothing and
other materials. The major feasts are coloured white or gold. Fasts are
purple. Feasts for martyrs (people who died for their faith) are red.
Other days are green.

## Installation

```console
pip install liturgical-calendar
```

## Usage, as a command

Once installed, this can be run at the command line. Currently it prints
an object with various attributes. This portion of the module needs
improvement, although it is probably more useful as a library.

Specify the date in YYYY-MM-DD format, or leave blank to return info
for today.

```console
# Get info for today
$ liturgical_calendar
name : 
prec : 1
season : Advent
weekno : 4
date : 2023-12-21
colour : purple
colourcode : #ad099a

# Get info for an arbitrary date
$ liturgical_calendar 2023-01-25
name : The Conversion of Paul
url : https://en.wikipedia.org/wiki/Conversion_of_Paul
prec : 7
type : Festival
season : Epiphany
weekno : 3
date : 2023-01-25
colour : white
colourcode : #ffffff
```

## Usage, as a library

```py
# Get info for today
dayinfo = liturgical_calendar()

# Get info for an arbitrary date
# Date can be expressed as a string in YYYY-MM-DD format, a Datetime object, or a Date object
dayinfo = liturgical_calendar('YYYY-MM-DD')

# Access the attributes individually
print(dayinfo['colour'])
```

## Issues

If you find bugs (either in the code or in the calendar), please
[create an issue on GitHub](https://github.com/liturgical-app/calendar/issues).

Pull requests are always welcome, either to address bugs or add new features.

## Example

There is a sample app which uses this library called
[Liturgical Colour App](https://github.com/djjudas21/liturgical-colour-app).

## Configuration

The project uses a centralized `Settings` class for all configuration. Configuration values can be set in three ways:

1. **Defaults in code**: Sensible defaults are provided in `liturgical_calendar/config/settings.py`.
2. **YAML config file**: You can provide a `config.yaml` file in the project root, or specify a path to a config file using the `--config` option.
3. **Environment variables**: Any config value can be overridden by setting an environment variable with the same name (case-insensitive, underscores).

### Usage Example

```sh
# Use defaults
python -m liturgical_calendar.cli generate 2024-12-25

# Use a custom config file
python -m liturgical_calendar.cli generate 2024-12-25 --config my_config.yaml

# Override with environment variable
IMAGE_WIDTH=2048 python -m liturgical_calendar.cli generate 2024-12-25
```

See `liturgical_calendar/config/settings.py` for all available config options.

## Testing

The test suite is organized as follows:

- `tests/unit/`: Unit tests for individual classes and functions (fast, isolated, use mocks/stubs).
- `tests/integration/`: Integration and end-to-end tests (test full workflows, real data, script entry points).
- `tests/fixtures/`: Sample data for use in tests (JSON, YAML, etc.).

### Running All Tests

To run all tests:

```sh
PYTHONPATH=. python -m unittest discover -s tests -p 'test*.py' -v
```

### Running Only Unit or Integration Tests

To run only unit tests:

```sh
PYTHONPATH=. python -m unittest discover -s tests/unit -p 'test*.py' -v
```

To run only integration tests:

```sh
PYTHONPATH=. python -m unittest discover -s tests/integration -p 'test*.py' -v
```

All tests must pass before committing changes. See the project rules for commit and test summary requirements.

## Raspberry Pi & E-Ink Integration

This project can be run on a Raspberry Pi to update an e-ink display with the current liturgical calendar image. See [docs/raspberry_pi_eink.md](docs/raspberry_pi_eink.md) for a full integration guide, including:
- System requirements and installation
- Scheduling regular updates (e.g., with cron)
- E-ink display tips (image size, color mode, conversion)
- Performance notes for low-resource devices
- Troubleshooting

A minimal example for updating an e-ink display is provided in `docs/examples/update_eink_display.py`.

## Requirements & Dependencies

- Python 3.8+
- Pillow, PyYAML, etc. (see requirements.txt)
- On Raspberry Pi/ARM: You may need to install system packages for Pillow (e.g., libjpeg, zlib, libfreetype6-dev). See the Pi integration guide for details.

## Troubleshooting

### Common Issues
- **Missing fonts:** Ensure the required fonts are present in the `fonts/` directory or update the config.
- **Pillow install errors on Pi:** Install system dependencies: `sudo apt-get install libjpeg-dev zlib1g-dev libfreetype6-dev`
- **Image not updating on e-ink:** Check the device-specific update command and permissions.
- **YAML config errors:** Validate your `config.yaml` with an online YAML linter.
- **Performance issues:** Use smaller images, avoid upsampling, and limit batch size on low-memory devices.
- **Verbose Mode:** All CLI scripts support a `--verbose` flag. When used, logging is set to DEBUG level and extra diagnostic output is shown. Use this for troubleshooting or detailed progress info.

See [docs/raspberry_pi_eink.md](docs/raspberry_pi_eink.md) for more troubleshooting tips.

## Contributing

We welcome contributions! Please follow these guidelines:

- Use [Conventional Commits](https://www.conventionalcommits.org/) for commit messages.
- All changes must pass the full test suite before committing (see Testing section).
- Include a summary table of test results in each commit message.
- Open issues or pull requests for bugs, features, or questions.

## License

[Specify your license here, or link to LICENSE file]

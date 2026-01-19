# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WineBuddy is a CLI tool for querying a wine cellar database. It imports wine data from CellarTracker CSV exports and stores them in a SQLite database, then provides filtering and output options.

## Commands

```bash
# Run the CLI directly with uv
uv run python winebuddy.py --help

# Or install as a tool and run
uv tool install .
winebuddy --help

# Discover available filter values
winebuddy discover colors
winebuddy discover producers
winebuddy discover regions

# Run tests
./test.sh
```

## Architecture

- **winebuddy.py**: Main CLI application using Typer. Contains:
  - Database initialization and CSV import (`init_database`, `load_csv_to_database`, `ensure_database`)
  - Query building with parameterized SQL (`build_query`)
  - Output formatters for table, JSON, and CSV (`format_table`, `format_json`, `format_csv`)
  - `discover` subcommand group for listing distinct values (colors, producers, varietals, countries, regions, vintages)
  - `query` command with filter options

- **cellar.db**: SQLite database (auto-created from cellar.csv on first run)
- **cellar.csv**: Wine data exported from CellarTracker

## Key Implementation Details

- Non-vintage wines use `1001` in the CSV and are stored as `NULL` in the database
- Drinking window values of `9999` indicate unknown
- Sort columns use a whitelist (`SORT_COLUMNS` dict) to prevent SQL injection
- CSV files use `latin-1` encoding

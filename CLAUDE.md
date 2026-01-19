# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WineBuddy is a wine cellar management application built with Python 3.14+ and SQLite. It tracks wine inventory including vintage, producer, varietal, region, quantity, and drinking windows.

## Commands

This project uses [uv](https://docs.astral.sh/uv) for dependency and environment management.

```bash
# Run any Python script
uv run python <script.py>

# Initialize the database
uv run python init_db.py

# Load wine data from CSV
uv run python load_csv.py

# Query example (red wines older than 2016)
uv run python query_old_reds.py
```

## Architecture

- **cellar.db** - SQLite database with `wines` table
- **cellar.csv** - Source data for wine inventory
- **init_db.py** - Database schema initialization
- **load_csv.py** - CSV to SQLite data loader
- **query_old_reds.py** - Example query script

### Database Schema

The `wines` table stores: color, category, size, currency, value, price, quantities, vintage, wine_name, locale, producer, varietal, country, region, subregion, drinking window (begin_consume/end_consume), and scores (professional_score/community_score).

Special values: vintage=1001 indicates non-vintage wines; begin_consume/end_consume=9999 indicates unknown drinking window.

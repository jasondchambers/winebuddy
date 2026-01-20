# WineBuddy

A wine cellar database CLI application that enables you to query the wines in your
cellar. 

You may ask, why even bother going to the trouble of developing a nerdy CLI
application for querying your wine cellar. That is a good question? The answer
is exploring can you ask your chat application (i.e. Claude Code) about the
contents of your wine cellar. That is a far more interesting scenario.

So, the real use of WineBuddy is to incorporate it into a Claude Code Skill, so
you can do exactly that. The skill is called 
[wine-paring](https://github.com/jasondchambers/wine-pairing) so be sure to
check it out.

## Installation

### Try without installing

```bash
# From local directory
uvx --from . winebuddy --help
```

```bash
# Install from local directory
uv tool install .
```

Once installed, run the tool directly:

```bash
winebuddy --help
```

### Uninstall

```bash
uv tool uninstall winebuddy
```

## Setup

First, you need the data. The recommended way is to build your cellar using [CellarTracker](https://mobileapp.cellartracker.com), then export using their website to generate a CSV file as follows:

![Alt text](export_instructions.png)

Make sure you include wines from all pages, you generate a Comma Separated
Values for the Export Format, and you select precisely the columns shown above.
Make sure the file exported is named cellar.csv and is moved to the current
directory.

The database will automatically get created when you call `winebuddy`.

## Discovering What Is In Your Cellar

Before querying, you can explore what values exist in your cellar using the `discover` command:

```bash
winebuddy discover colors      # List all wine colors (Red, White, Rosé, etc.)
winebuddy discover producers   # List all producers
winebuddy discover varietals   # List all varietals
winebuddy discover countries   # List all countries
winebuddy discover regions     # List all regions
winebuddy discover vintages    # List all vintages
```

This helps you know exactly what filter values to use when querying.

## Querying Your Cellar

Use `winebuddy query` to search and filter wines from your cellar.

```bash
winebuddy query [OPTIONS]
```

### Filter Options

| Option | Short | Description |
|--------|-------|-------------|
| `--color` | `-c` | Filter by wine color (Red, White, Rosé, etc.) |
| `--producer` | `-p` | Filter by producer (partial match) |
| `--varietal` | `-v` | Filter by varietal (partial match) |
| `--country` | | Filter by country (exact match) |
| `--region` | `-r` | Filter by region (partial match) |
| `--vintage` | | Filter by exact vintage year |
| `--vintage-min` | | Minimum vintage year |
| `--vintage-max` | | Maximum vintage year |
| `--score-min` | | Minimum professional score |
| `--in-stock` | | Only show wines with quantity > 0 |
| `--ready` | | Only show wines within their drinking window |

### Output Options

| Option | Short | Description |
|--------|-------|-------------|
| `--sort` | `-s` | Sort by: `vintage`, `producer`, `score`, `value`, `name` |
| `--desc` | `-d` | Sort in descending order |
| `--limit` | `-l` | Limit number of results |
| `--format` | `-f` | Output format: `table`, `json`, `csv` |

## Examples

### Basic Queries

```bash
# List all wines
winebuddy query

# List all red wines
winebuddy query --color Red

# List all wines from a specific producer
winebuddy query --producer "Château"

# List all Pinot Noir wines
winebuddy query --varietal "Pinot Noir"
```

### Vintage Filters

```bash
# Wines from exactly 2015
winebuddy query --vintage 2015

# Wines from 2015 or older
winebuddy query --vintage-max 2015

# Wines from 2018 or newer
winebuddy query --vintage-min 2018

# Wines between 2010 and 2015
winebuddy query --vintage-min 2010 --vintage-max 2015
```

### Location Filters

```bash
# Wines from France
winebuddy query --country France

# Wines from Burgundy region
winebuddy query --region Burgundy

# California Cabernet Sauvignon
winebuddy query --region California --varietal "Cabernet Sauvignon"
```

### Stock and Drinking Window

```bash
# Only wines currently in stock
winebuddy query --in-stock

# Wines ready to drink now
winebuddy query --ready

# Red wines in stock that are ready to drink
winebuddy query --color Red --in-stock --ready
```

### Sorting Results

```bash
# Sort by vintage (oldest first)
winebuddy query --sort vintage

# Sort by vintage (newest first)
winebuddy query --sort vintage --desc

# Sort by professional score (highest first)
winebuddy query --sort score --desc

# Sort by value (most expensive first)
winebuddy query --sort value --desc

# Top 10 highest-scored wines
winebuddy query --sort score --desc --limit 10
```

### Output Formats

#### Table (default)

```bash
winebuddy query --limit 5
```

```
Vintage | Wine Name                    | Producer        | Varietal   | Region     | Qty | Score
--------+------------------------------+-----------------+------------+------------+-----+------
NV      | Billecart-Salmon Brut Rosé   | Billecart-Salmon| Champagne  | Champagne  | 8   | -
2015    | Château Margaux              | Château Margaux | Bordeaux   | Bordeaux   | 2   | 98.0
...

5 wine(s) found.
```

#### JSON

```bash
winebuddy query --format json --limit 2
```

```json
[
  {
    "id": 1,
    "wine_name": "Billecart-Salmon Champagne Brut Rosé",
    "vintage": null,
    "producer": "Billecart-Salmon",
    "varietal": "Champagne Blend",
    "color": "Rosé",
    "country": "France",
    "region": "Champagne",
    "subregion": null,
    "quantity": 8,
    "value": 89.99,
    "professional_score": null,
    "begin_consume": 2020,
    "end_consume": 2025
  }
]
```

#### CSV

```bash
winebuddy query --format csv --limit 2
```

```csv
id,wine_name,vintage,producer,varietal,color,country,region,subregion,quantity,value,professional_score,begin_consume,end_consume
1,Billecart-Salmon Champagne Brut Rosé,,Billecart-Salmon,Champagne Blend,Rosé,France,Champagne,,8,89.99,,2020,2025
```

Export to a file:

```bash
winebuddy query --format csv > my_wines.csv
```

### Combined Examples

```bash
# French red wines from 2015 or older, sorted by score
winebuddy query --country France --color Red --vintage-max 2015 --sort score --desc

# Top 5 most valuable wines in stock
winebuddy query --in-stock --sort value --desc --limit 5

# All Champagne ready to drink, as JSON
winebuddy query --region Champagne --ready --format json

# Italian wines with score >= 90
winebuddy query --country Italy --score-min 90
```

## Database Schema

The `wines` table contains:

- **color**: Red, White, Rosé, etc.
- **category**: Still, Sparkling, etc.
- **vintage**: Year (NULL for non-vintage wines)
- **wine_name**, **producer**, **varietal**
- **country**, **region**, **subregion**, **locale**
- **quantity**: Bottles currently in cellar
- **value**, **price**, **currency**
- **begin_consume**, **end_consume**: Drinking window (9999 = unknown)
- **professional_score**, **community_score**

---
name: winebuddy
description: Query personal wine cellar database. Use for wine pairing recommendations, searching wines, checking inventory, finding bottles by region/varietal/vintage/producer, discovering what's in the cellar, checking drinking windows, or any question about the wine collection.
compatibility: Requires git, uv, and Python 3
metadata:
  author: jasondchambers
  version: "1.0"
allowed-tools: Bash(git:*) Bash(uv:*) Bash(cd:*) Bash(if:*) Bash(cp:*)
---

# WineBuddy Skill

Query and explore your personal wine cellar database.

## Step 1: Ensure winebuddy is installed and up-to-date

```bash
if [ ! -d ~/.winebuddy ]; then
  git clone https://github.com/jasondchambers/winebuddy.git ~/.winebuddy
fi && cd ~/.winebuddy && git pull
```

## Step 2: Run Commands

Always refresh the database before running a command. This ensures the database
is current and alerts the user to any cellar changes (new wines, consumed bottles,
quantity changes). Exit code 255 means the CSV is missing (a real error); exit
codes 1 (created) and 2 (rebuilt) are successes that should not block the command.

```bash
cd ~/.winebuddy && REFRESH_OUTPUT=$(uv run python winebuddy.py --refresh 2>&1); REFRESH_RC=$?; [ $REFRESH_RC -ne 255 ] && QUERY_OUTPUT=$(uv run python winebuddy.py <command> 2>&1); echo "$REFRESH_OUTPUT"; echo "$QUERY_OUTPUT"
```

**Important:** Always include the full `REFRESH_OUTPUT` in your response to the user so
they can see any cellar changes (new wines added, bottles consumed, quantity changes).

## Commands

| Command | Purpose |
|---------|---------|
| `query` | Search and filter wines |
| `discover <type>` | List distinct values (colors, varietals, regions, etc.) |

## Query Filters

| Option | Description | Example |
|--------|-------------|---------|
| `--color` | Wine color | `--color Red` |
| `--varietal` | Grape variety (partial match) | `--varietal "Pinot Noir"` |
| `--producer` | Producer name (partial match) | `--producer "Patricia Green"` |
| `--country` | Country of origin | `--country Italy` |
| `--region` | Region (partial match) | `--region Willamette` |
| `--vintage` | Exact vintage year | `--vintage 2019` |
| `--vintage-min` | Minimum vintage | `--vintage-min 2015` |
| `--vintage-max` | Maximum vintage | `--vintage-max 2018` |
| `--score-min` | Minimum score | `--score-min 90` |
| `--in-stock` | Only wines with quantity > 0 | `--in-stock` |
| `--ready` | Wines in their drinking window | `--ready` |

## Output Options

| Option | Description |
|--------|-------------|
| `--format table` | ASCII table (default) |
| `--format json` | JSON output |
| `--format csv` | CSV output |
| `--sort vintage\|producer\|score\|price\|wine_name` | Sort field |
| `--desc` | Sort descending |
| `--limit N` | Limit results |

## Discover Command

List distinct values in the cellar:

```bash
cd ~/.winebuddy && uv run python winebuddy.py discover colors
cd ~/.winebuddy && uv run python winebuddy.py discover varietals
cd ~/.winebuddy && uv run python winebuddy.py discover producers
cd ~/.winebuddy && uv run python winebuddy.py discover countries
cd ~/.winebuddy && uv run python winebuddy.py discover regions
cd ~/.winebuddy && uv run python winebuddy.py discover vintages
```

## Wine Pairing

For food pairing recommendations, see [the pairing guide](references/PAIRING.md).

## Example Queries

For common query examples, see [the examples guide](references/EXAMPLES.md).

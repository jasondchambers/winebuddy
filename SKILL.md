---
name: winebuddy
description: Query personal wine cellar database. Use for wine pairing recommendations, searching wines, checking inventory, finding bottles by region/varietal/vintage/producer, discovering what's in the cellar, checking drinking windows, or any question about the wine collection.
allowed-tools:
  - Bash(git clone:*)
  - Bash(git pull:*)
  - Bash(uv run:*)
  - Bash(cd:*)
  - Bash(if:*)
  - Bash(cp:*)
user-invocable: true
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

## Commands Overview

| Command | Purpose |
|---------|---------|
| `query` | Search and filter wines |
| `discover <type>` | List distinct values (colors, varietals, regions, etc.) |

---

## Query Command

Search wines with filters:

```bash
cd ~/.winebuddy && uv run python winebuddy.py query [OPTIONS]
```

### Filter Options

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
| `--score-min` | Minimum score (professional or community) | `--score-min 90` |
| `--in-stock` | Only wines with quantity > 0 | `--in-stock` |
| `--ready` | Wines in their drinking window | `--ready` |

### Output Options

| Option | Description |
|--------|-------------|
| `--format table` | ASCII table (default) |
| `--format json` | JSON output |
| `--format csv` | CSV output |
| `--sort vintage\|producer\|score\|price\|wine_name` | Sort field |
| `--desc` | Sort descending |
| `--limit N` | Limit results |

### JSON Output Fields

```json
{
  "id": 1,
  "wine_name": "Wine name",
  "vintage": 2019,
  "producer": "Winery",
  "varietal": "Pinot Noir",
  "color": "Red",
  "country": "USA",
  "region": "Oregon",
  "subregion": "Willamette Valley",
  "quantity": 3,
  "value": 75.95,
  "professional_score": 93.5,
  "community_score": 91.2,
  "begin_consume": 2024,
  "end_consume": 2032
}
```

---

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

---

## Example Queries

### Inventory Questions

```bash
# All wines in stock
cd ~/.winebuddy && uv run python winebuddy.py query --in-stock --format table

# Most valuable bottles
cd ~/.winebuddy && uv run python winebuddy.py query --in-stock --sort price --desc --limit 5 --format json

# Oldest vintages
cd ~/.winebuddy && uv run python winebuddy.py query --in-stock --sort vintage --limit 5 --format json
```

### Finding Specific Wines

```bash
# Italian wines
cd ~/.winebuddy && uv run python winebuddy.py query --in-stock --country Italy --format json

# Wines from a region
cd ~/.winebuddy && uv run python winebuddy.py query --in-stock --region "Willamette" --format json

# Specific producer
cd ~/.winebuddy && uv run python winebuddy.py query --in-stock --producer "Patricia Green" --format json

# Specific varietal
cd ~/.winebuddy && uv run python winebuddy.py query --in-stock --varietal "Nebbiolo" --format json
```

### Drinking Window Questions

```bash
# Ready to drink now
cd ~/.winebuddy && uv run python winebuddy.py query --in-stock --ready --format json

# Top rated wines
cd ~/.winebuddy && uv run python winebuddy.py query --in-stock --sort score --desc --limit 10 --format json

# Wines from specific vintage range
cd ~/.winebuddy && uv run python winebuddy.py query --in-stock --vintage-min 2015 --vintage-max 2018 --format json
```

---

## Wine Pairing

For food pairing recommendations, use these guidelines:

| Dish Type | Recommended Varietals |
|-----------|----------------------|
| **Red meat** (beef, lamb) | Cabernet Sauvignon, Merlot, Syrah, Red Bordeaux Blend |
| **Poultry** (chicken, turkey) | Pinot Noir, Chardonnay |
| **Pork** | Grenache, Tempranillo, Riesling |
| **Fish** (light) | Sauvignon Blanc, Pinot Grigio, Arneis |
| **Salmon/rich fish** | Pinot Noir, Chardonnay, Champagne Blend |
| **Seafood/shellfish** | Champagne Blend, Sparkling, Sauvignon Blanc |
| **Pasta (red sauce)** | Sangiovese, Nebbiolo |
| **Pasta (cream sauce)** | Chardonnay |
| **Spicy food** | Riesling, Gewürztraminer, Frappato |

### Pairing Query Strategy

1. Identify appropriate varietals from the table above
2. Query wines by varietal, sorted by score:
   ```bash
   cd ~/.winebuddy && uv run python winebuddy.py query --in-stock --varietal "Pinot Noir" --format json --sort score --desc --limit 5
   ```
3. Check drinking windows in results to identify:
   - **Drink Soon**: `end_consume` < 2026 (current year)
   - **Best Available**: Highest scores regardless of window

### Pairing Response Format

```
## Wine Pairing Recommendations for [Dish]

### Drink Soon (Past Drinking Window)
1. **[Wine]** ([Vintage]) - Score: [X] | Value: $[X] | Window: [X-X]
   Why it pairs: [rationale]

### Best Available (Special Occasions)
1. **[Wine]** ([Vintage]) - Score: [X] | Value: $[X] | Window: [X-X]
   Why it pairs: [rationale]
```

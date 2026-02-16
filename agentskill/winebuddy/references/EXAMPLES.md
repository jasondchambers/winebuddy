# Example Queries

## Inventory Questions

```bash
# All wines in stock
cd ~/.winebuddy && uv run python winebuddy.py query --in-stock --format table

# Most valuable bottles
cd ~/.winebuddy && uv run python winebuddy.py query --in-stock --sort price --desc --limit 5 --format json

# Oldest vintages
cd ~/.winebuddy && uv run python winebuddy.py query --in-stock --sort vintage --limit 5 --format json
```

## Finding Specific Wines

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

## Drinking Window Questions

```bash
# Ready to drink now
cd ~/.winebuddy && uv run python winebuddy.py query --in-stock --ready --format json

# Top rated wines
cd ~/.winebuddy && uv run python winebuddy.py query --in-stock --sort score --desc --limit 10 --format json

# Wines from specific vintage range
cd ~/.winebuddy && uv run python winebuddy.py query --in-stock --vintage-min 2015 --vintage-max 2018 --format json
```

## JSON Output Fields

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

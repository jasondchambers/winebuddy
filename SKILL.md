---
name: wine-pairing
description: Recommend wine pairings from personal cellar for dishes and meals. Use when asking what wine to pair with food, dinner, a dish, or meal. Queries wine cellar database and suggests wines based on pairing principles and drinking windows.
---

# Wine Pairing Skill

Recommend wines from the user's personal cellar to pair with dishes they plan to cook.

## Setup (Run Every Time)

Before querying, ensure the winebuddy tool and cellar data are available:

### Step 1: Clone winebuddy if needed

```bash
if [ ! -d ~/.winebuddy ]; then
  git clone git@github.com:jasondchambers/winebuddy.git ~/.winebuddy
fi
```

### Step 2: Check for cellar.csv

```bash
ls ~/.winebuddy/cellar.csv
```

**If cellar.csv is NOT found**, stop and display these instructions to the user:

> **Cellar data not found!**
>
> To use this skill, you need to export your wine cellar from CellarTracker:
>
> 1. Log in to [CellarTracker](https://www.cellartracker.com)
> 2. Go to your cellar and export as CSV
> 3. Save the file as `~/.winebuddy/cellar.csv`
>
> Required CSV columns: Color, Category, Size, Currency, Value, Price, TotalQuantity, Quantity, Pending, Vintage, Wine, Locale, Producer, Varietal, Country, Region, SubRegion, BeginConsume, EndConsume, PScore, CScore
>
> Once your cellar.csv is in place, ask me again for wine pairing recommendations.

**If cellar.csv IS found**, proceed with the pairing recommendations.

## How to Run Winebuddy

All winebuddy commands should be run using uvx from the cloned repo directory:

```bash
cd ~/.winebuddy && uvx --from . winebuddy <command>
```

## How to Use

When the user provides a dish or meal they're planning, follow these steps:

### Step 1: Query the Wine Cellar

Run the following command to get all in-stock wines sorted by score:

```bash
cd ~/.winebuddy && uvx --from . winebuddy query --in-stock --format json --sort score --desc
```

This returns JSON with wine data including:
- `color` - Red, White, Rosé, Sparkling, etc.
- `varietal` - Grape variety (Pinot Noir, Chardonnay, etc.)
- `producer` - Winery name
- `wine_name` - Full wine name
- `vintage` - Year (null for non-vintage)
- `region`, `country` - Origin
- `value` - Estimated bottle value in dollars
- `professional_score` - Critic score (higher is better)
- `begin_consume`, `end_consume` - Drinking window years (9999 means unknown)
- `quantity` - Bottles available

### Step 2: Analyze Wines for the Dish

Using classic wine pairing principles, identify wines that would complement the dish:

**General Pairing Guidelines:**
- **Red meat** (beef, lamb, game): Full-bodied reds (Cabernet, Merlot, Syrah, Malbec)
- **Poultry** (chicken, turkey): Light reds (Pinot Noir) or full-bodied whites (Chardonnay)
- **Pork**: Medium reds (Grenache, Tempranillo) or aromatic whites (Riesling)
- **Fish**: White wines (Sauvignon Blanc, Pinot Grigio, Albariño)
- **Seafood/shellfish**: Crisp whites, Champagne/sparkling
- **Salmon/rich fish**: Pinot Noir or oaked Chardonnay
- **Pasta with red sauce**: Italian reds (Sangiovese, Nebbiolo)
- **Pasta with cream sauce**: Oaked Chardonnay, Pinot Grigio
- **Spicy food**: Off-dry whites (Riesling, Gewürztraminer) or fruity reds
- **Cheese**: Varies by cheese type; generally robust reds for hard cheeses, whites for soft
- **Desserts**: Sweet wines (Port, Sauternes, late harvest)

**Consider also:**
- Regional pairings (French dish → French wine)
- Sauce and preparation method weight
- Seasonal appropriateness

### Step 3: Generate Two Recommendation Lists

Create exactly **two lists of up to 3 wines each**:

#### List 1: "Drink Soon" (Past Drinking Window)

Wines that have **passed their drinking window** - these should be consumed soon to avoid further decline.

**Criteria:**
- `end_consume` < current year (2026)
- `end_consume` != 9999 (exclude unknown drinking windows)
- Must be appropriate for the dish
- Sort by `professional_score` descending (highest first)

**Purpose:** Help the user consume wines that are past their peak before they decline further.

#### List 2: "Best Available" (For Special Occasions)

The highest-scored wines that pair with the dish, **ignoring drinking window**.

**Criteria:**
- Appropriate pairing for the dish
- Sort by `professional_score` descending (highest first)
- Include wines regardless of drinking window status

**Purpose:** When the occasion is special enough to open a prized bottle.

### Step 4: Present Recommendations

Format your response as follows:

```
## Wine Pairing Recommendations for [Dish Name]

### Drink Soon (Past Drinking Window)
These wines have passed their optimal drinking window and should be enjoyed soon:

1. **[Wine Name]** ([Vintage])
   - Producer: [Producer]
   - Varietal: [Varietal] | Region: [Region]
   - Score: [Score] | Value: $[Value] | Drinking Window: [Begin]-[End]
   - Why it pairs: [Brief pairing rationale]

2. ...

3. ...

### Best Available (For Special Occasions)
Your highest-rated wines that pair beautifully with this dish:

1. **[Wine Name]** ([Vintage])
   - Producer: [Producer]
   - Varietal: [Varietal] | Region: [Region]
   - Score: [Score] | Value: $[Value] | Drinking Window: [Begin]-[End]
   - Why it pairs: [Brief pairing rationale]

2. ...

3. ...
```

**Notes:**
- If fewer than 3 wines match criteria for a list, show what's available
- If no wines match for "Drink Soon", note that no wines are past their window
- Always explain *why* each wine pairs well with the specific dish
- Mention if a wine is within its drinking window vs past it

## Discovery Commands

If needed, use these to explore what's in the cellar:

```bash
cd ~/.winebuddy && uvx --from . winebuddy discover colors      # List all wine colors
cd ~/.winebuddy && uvx --from . winebuddy discover producers   # List all producers
cd ~/.winebuddy && uvx --from . winebuddy discover varietals   # List all grape varieties
cd ~/.winebuddy && uvx --from . winebuddy discover regions     # List all regions
cd ~/.winebuddy && uvx --from . winebuddy discover vintages    # List all vintages
```

## Filtering Examples

Query specific wine types if helpful:

```bash
cd ~/.winebuddy && uvx --from . winebuddy query --in-stock --color Red --format json --sort score --desc
cd ~/.winebuddy && uvx --from . winebuddy query --in-stock --color White --format json --sort score --desc
cd ~/.winebuddy && uvx --from . winebuddy query --in-stock --varietal "Pinot Noir" --format json
cd ~/.winebuddy && uvx --from . winebuddy query --in-stock --region Burgundy --format json
```

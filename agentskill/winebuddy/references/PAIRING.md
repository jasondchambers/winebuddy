# Wine Pairing Guide

## Pairing Table

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
| **Spicy food** | Riesling, Gewurztraminer, Frappato |

## Pairing Query Strategy

1. Identify appropriate varietals from the table above
2. Query wines by varietal, sorted by score:
   ```bash
   cd ~/.winebuddy && uv run python winebuddy.py query --in-stock --varietal "Pinot Noir" --format json --sort score --desc --limit 5
   ```
3. Check drinking windows in results to identify:
   - **Drink Soon**: `end_consume` < current year
   - **Best Available**: Highest scores regardless of window

## Pairing Response Format

```
## Wine Pairing Recommendations for [Dish]

### Drink Soon (Past Drinking Window)
1. **[Wine]** ([Vintage]) - Score: [X] | Value: $[X] | Window: [X-X]
   Why it pairs: [rationale]

### Best Available (Special Occasions)
1. **[Wine]** ([Vintage]) - Score: [X] | Value: $[X] | Window: [X-X]
   Why it pairs: [rationale]
```

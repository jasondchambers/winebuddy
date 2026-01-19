#!/usr/bin/env bash
# Test script for the Wine Query CLI

set -e  # Exit on first error

echo "=== Wine Query CLI Tests ==="
echo

# Test 1: Help output
echo "Test 1: Help output"
uv run python query.py --help > /dev/null
echo "PASS: Help displays correctly"
echo

# Test 2: Basic query (no filters)
echo "Test 2: Basic query with limit"
output=$(uv run python query.py --limit 5)
if echo "$output" | grep -q "wine(s) found"; then
    echo "PASS: Basic query works"
else
    echo "FAIL: Basic query did not return expected output"
    exit 1
fi
echo

# Test 3: Color filter
echo "Test 3: Color filter (Red wines)"
output=$(uv run python query.py --color Red --limit 3)
if echo "$output" | grep -q "wine(s) found"; then
    echo "PASS: Color filter works"
else
    echo "FAIL: Color filter did not work"
    exit 1
fi
echo

# Test 4: Varietal filter (contains match)
echo "Test 4: Varietal filter (Pinot Noir)"
output=$(uv run python query.py --varietal "Pinot Noir" --limit 3)
if echo "$output" | grep -q "Pinot Noir"; then
    echo "PASS: Varietal filter works"
else
    echo "FAIL: Varietal filter did not work"
    exit 1
fi
echo

# Test 5: Vintage range filter
echo "Test 5: Vintage range filter (max 2015)"
output=$(uv run python query.py --vintage-max 2015 --limit 5)
if echo "$output" | grep -q "wine(s) found"; then
    echo "PASS: Vintage range filter works"
else
    echo "FAIL: Vintage range filter did not work"
    exit 1
fi
echo

# Test 6: In-stock filter
echo "Test 6: In-stock filter"
output=$(uv run python query.py --in-stock --limit 5)
if echo "$output" | grep -q "wine(s) found"; then
    echo "PASS: In-stock filter works"
else
    echo "FAIL: In-stock filter did not work"
    exit 1
fi
echo

# Test 7: Sort by score descending
echo "Test 7: Sort by score descending"
output=$(uv run python query.py --sort score --desc --limit 5)
if echo "$output" | grep -q "wine(s) found"; then
    echo "PASS: Sort by score works"
else
    echo "FAIL: Sort by score did not work"
    exit 1
fi
echo

# Test 8: JSON output format
echo "Test 8: JSON output format"
output=$(uv run python query.py --limit 2 --format json)
if echo "$output" | grep -q '"wine_name"'; then
    echo "PASS: JSON output works"
else
    echo "FAIL: JSON output did not work"
    exit 1
fi
echo

# Test 9: CSV output format
echo "Test 9: CSV output format"
output=$(uv run python query.py --limit 2 --format csv)
if echo "$output" | grep -q "id,wine_name,vintage"; then
    echo "PASS: CSV output works"
else
    echo "FAIL: CSV output did not work"
    exit 1
fi
echo

# Test 10: Combined filters
echo "Test 10: Combined filters (Red + in-stock + sort by vintage)"
output=$(uv run python query.py --color Red --in-stock --sort vintage --limit 5)
if echo "$output" | grep -q "wine(s) found"; then
    echo "PASS: Combined filters work"
else
    echo "FAIL: Combined filters did not work"
    exit 1
fi
echo

# Test 11: Producer filter (contains match)
echo "Test 11: Producer filter"
output=$(uv run python query.py --producer "Château" --limit 3)
if echo "$output" | grep -q "wine(s) found"; then
    echo "PASS: Producer filter works"
else
    echo "FAIL: Producer filter did not work"
    exit 1
fi
echo

# Test 12: Country filter
echo "Test 12: Country filter (USA)"
output=$(uv run python query.py --country USA --limit 3)
if echo "$output" | grep -q "wine(s) found"; then
    echo "PASS: Country filter works"
else
    echo "FAIL: Country filter did not work"
    exit 1
fi
echo

# Test 13: Short option flags
echo "Test 13: Short option flags (-c, -v, -l, -f)"
output=$(uv run python query.py -c Red -l 2 -f json)
if echo "$output" | grep -q '"color": "Red"'; then
    echo "PASS: Short option flags work"
else
    echo "FAIL: Short option flags did not work"
    exit 1
fi
echo

echo "=== All tests passed! ==="

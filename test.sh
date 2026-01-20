#!/usr/bin/env bash
# Test script for the Wine Query CLI

set -e # Exit on first error

echo "=== Wine Query CLI Tests ==="
echo

# Test 1: Help output
echo "Test 1: Help output"
uv run python winebuddy.py --help >/dev/null
echo "PASS: Help displays correctly"
echo

# Test 2: Basic query (no filters)
echo "Test 2: Basic query with limit"
output=$(uv run python winebuddy.py --cellar-name cellar.test query --limit 5)
expected=$(cat test2.expected)
if [ "$output" = "$expected" ]; then
  echo "PASS: Basic query works"
else
  echo "FAIL: Basic query did not return expected output"
  echo "Expected:"
  echo "$expected"
  echo "Got:"
  echo "$output"
  exit 1
fi
echo

# Test 3: Color filter
echo "Test 3: Color filter (Red wines)"
output=$(uv run python winebuddy.py --cellar-name cellar.test query --color Red --limit 3)
expected=$(cat test3.expected)
if [ "$output" = "$expected" ]; then
  echo "PASS: Color filter works"
else
  echo "FAIL: Color filter did not work"
  echo "Expected:"
  echo "$expected"
  echo "Got:"
  echo "$output"
  exit 1
fi
echo

# Test 4: Varietal filter (contains match)
echo "Test 4: Varietal filter (Pinot Noir)"
output=$(uv run python winebuddy.py --cellar-name cellar.test query --varietal "Pinot Noir" --limit 3)
expected=$(cat test4.expected)
if [ "$output" = "$expected" ]; then
  echo "PASS: Varietal filter works"
else
  echo "FAIL: Varietal filter did not work"
  echo "Expected:"
  echo "$expected"
  echo "Got:"
  echo "$output"
  exit 1
fi
echo

# Test 5: Vintage range filter
echo "Test 5: Vintage range filter (max 2015)"
output=$(uv run python winebuddy.py --cellar-name cellar.test query --vintage-max 2015 --limit 5)
expected=$(cat test5.expected)
if [ "$output" = "$expected" ]; then
  echo "PASS: Vintage range filter works"
else
  echo "FAIL: Vintage range filter did not work"
  echo "Expected:"
  echo "$expected"
  echo "Got:"
  echo "$output"
  exit 1
fi
echo

# Test 6: In-stock filter
echo "Test 6: In-stock filter"
output=$(uv run python winebuddy.py --cellar-name cellar.test query --in-stock --limit 5)
expected=$(cat test6.expected)
if [ "$output" = "$expected" ]; then
  echo "PASS: In-stock filter works"
else
  echo "FAIL: In-stock filter did not work"
  echo "Expected:"
  echo "$expected"
  echo "Got:"
  echo "$output"
  exit 1
fi
echo

# Test 7: Sort by score descending
echo "Test 7: Sort by score descending"
output=$(uv run python winebuddy.py --cellar-name cellar.test query --sort score --desc --limit 5)
expected=$(cat test7.expected)
if [ "$output" = "$expected" ]; then
  echo "PASS: Sort by score works"
else
  echo "FAIL: Sort by score did not work"
  echo "Expected:"
  echo "$expected"
  echo "Got:"
  echo "$output"
  exit 1
fi
echo

# Test 8: JSON output format
echo "Test 8: JSON output format"
output=$(uv run python winebuddy.py --cellar-name cellar.test query --limit 2 --format json)
expected=$(cat test8.expected)
if [ "$output" = "$expected" ]; then
  echo "PASS: JSON output works"
else
  echo "FAIL: JSON output did not work"
  echo "Expected:"
  echo "$expected"
  echo "Got:"
  echo "$output"
  exit 1
fi
echo

# Test 9: CSV output format
echo "Test 9: CSV output format"
output=$(uv run python winebuddy.py --cellar-name cellar.test query --limit 2 --format csv)
expected=$(cat test9.expected)
if [ "$output" = "$expected" ]; then
  echo "PASS: CSV output works"
else
  echo "FAIL: CSV output did not work"
  echo "Expected:"
  echo "$expected"
  echo "Got:"
  echo "$output"
  exit 1
fi
echo

# Test 10: Combined filters
echo "Test 10: Combined filters (Red + in-stock + sort by vintage)"
output=$(uv run python winebuddy.py --cellar-name cellar.test query --color Red --in-stock --sort vintage --limit 5)
expected=$(cat test10.expected)
if [ "$output" = "$expected" ]; then
  echo "PASS: Combined filters work"
else
  echo "FAIL: Combined filters did not work"
  echo "Expected:"
  echo "$expected"
  echo "Got:"
  echo "$output"
  exit 1
fi
echo

# Test 11: Producer filter (contains match)
echo "Test 11: Producer filter"
output=$(uv run python winebuddy.py --cellar-name cellar.test query --producer "Château" --limit 3)
expected=$(cat test11.expected)
if [ "$output" = "$expected" ]; then
  echo "PASS: Producer filter works"
else
  echo "FAIL: Producer filter did not work"
  echo "Expected:"
  echo "$expected"
  echo "Got:"
  echo "$output"
  exit 1
fi
echo

# Test 12: Country filter
echo "Test 12: Country filter (USA)"
output=$(uv run python winebuddy.py --cellar-name cellar.test query --country USA --limit 3)
expected=$(cat test12.expected)
if [ "$output" = "$expected" ]; then
  echo "PASS: Country filter works"
else
  echo "FAIL: Country filter did not work"
  echo "Expected:"
  echo "$expected"
  echo "Got:"
  echo "$output"
  exit 1
fi
echo

# Test 13: Short option flags
echo "Test 13: Short option flags (-c, -v, -l, -f)"
output=$(uv run python winebuddy.py --cellar-name cellar.test query -c Red -l 2 -f json)
expected=$(cat test13.expected)
if [ "$output" = "$expected" ]; then
  echo "PASS: Short option flags work"
else
  echo "FAIL: Short option flags did not work"
  echo "Expected:"
  echo "$expected"
  echo "Got:"
  echo "$output"
  exit 1
fi
echo

# Test 14: Discover colors
echo "Test 14: Discover colors"
output=$(uv run python winebuddy.py --cellar-name cellar.test discover colors)
expected=$(cat test14.expected)
if [ "$output" = "$expected" ]; then
  echo "PASS: Discover colors works"
else
  echo "FAIL: Discover colors did not work"
  echo "Expected:"
  echo "$expected"
  echo "Got:"
  echo "$output"
  exit 1
fi
echo

# Test 15: Discover regions
echo "Test 15: Discover regions"
output=$(uv run python winebuddy.py --cellar-name cellar.test discover regions)
expected=$(cat test15.expected)
if [ "$output" = "$expected" ]; then
  echo "PASS: Discover regions works"
else
  echo "FAIL: Discover regions did not work"
  echo "Expected:"
  echo "$expected"
  echo "Got:"
  echo "$output"
  exit 1
fi
echo

echo "=== All tests passed! ==="

#!/usr/bin/env bash
# Test script for the Wine Query CLI

set -e # Exit on first error

# Helper function for tests that compare output against expected files
run_test() {
  local test_num=$1
  local test_name=$2
  shift 2
  local cmd_args=("$@")

  echo "Test $test_num: $test_name"
  output=$(uv run python winebuddy.py --cellar-name ./cellar.test "${cmd_args[@]}")
  expected=$(cat "test${test_num}.expected")
  if [ "$output" = "$expected" ]; then
    echo "PASS: $test_name"
  else
    echo "FAIL: $test_name"
    echo "Expected:"
    echo "$expected"
    echo "Got:"
    echo "$output"
    exit 1
  fi
  echo
}

echo "=== Wine Query CLI Tests ==="
echo

# Test 1: Help output (special case - no expected file)
echo "Test 1: Help output"
uv run python winebuddy.py --help >/dev/null
echo "PASS: Help displays correctly"
echo

# Tests 2-15: Compare output against expected files
run_test 2  "Basic query with limit"                            query --limit 5
run_test 3  "Color filter (Red wines)"                          query --color Red --limit 3
run_test 4  "Varietal filter (Pinot Noir)"                      query --varietal "Pinot Noir" --limit 3
run_test 5  "Vintage range filter (max 2015)"                   query --vintage-max 2015 --limit 5
run_test 6  "In-stock filter"                                   query --in-stock --limit 5
run_test 7  "Sort by score descending"                          query --sort score --desc --limit 5
run_test 8  "JSON output format"                                query --limit 2 --format json
run_test 9  "CSV output format"                                 query --limit 2 --format csv
run_test 10 "Combined filters (Red + in-stock + sort by vintage)" query --color Red --in-stock --sort vintage --limit 5
run_test 11 "Producer filter"                                   query --producer "Château" --limit 3
run_test 12 "Country filter (USA)"                              query --country USA --limit 3
run_test 13 "Short option flags (-c, -v, -l, -f)"               query -c Red -l 2 -f json
run_test 14 "Discover colors"                                   discover colors
run_test 15 "Discover regions"                                  discover regions

# =============================================================================
# Refresh tests — these manage their own DB lifecycle
# =============================================================================

# Test 16: --refresh creates database (exit code 1)
echo "Test 16: Refresh creates database"
rm -f cellar.test.db
output=$(uv run python winebuddy.py --cellar-name ./cellar.test --refresh 2>/dev/null) || exit_code=$?
expected=$(cat "test16.expected")
if [ "$output" = "$expected" ] && [ "${exit_code:-0}" = "1" ]; then
  echo "PASS: Refresh creates database"
else
  echo "FAIL: Refresh creates database"
  echo "Expected exit code 1, got: ${exit_code:-0}"
  echo "Expected output:"
  echo "$expected"
  echo "Got:"
  echo "$output"
  exit 1
fi
echo

# Test 17: --refresh when up to date (exit code 0)
echo "Test 17: Refresh when up to date"
exit_code=0
output=$(uv run python winebuddy.py --cellar-name ./cellar.test --refresh 2>/dev/null) || exit_code=$?
expected=$(cat "test17.expected")
if [ "$output" = "$expected" ] && [ "$exit_code" = "0" ]; then
  echo "PASS: Refresh when up to date"
else
  echo "FAIL: Refresh when up to date"
  echo "Expected exit code 0, got: $exit_code"
  echo "Expected output:"
  echo "$expected"
  echo "Got:"
  echo "$output"
  exit 1
fi
echo

# Test 18: --refresh rebuild with no content changes (exit code 2)
echo "Test 18: Refresh rebuild with no content changes"
sleep 1
touch cellar.test.csv
exit_code=0
output=$(uv run python winebuddy.py --cellar-name ./cellar.test --refresh 2>/dev/null) || exit_code=$?
expected=$(cat "test18.expected")
if [ "$output" = "$expected" ] && [ "$exit_code" = "2" ]; then
  echo "PASS: Refresh rebuild with no content changes"
else
  echo "FAIL: Refresh rebuild with no content changes"
  echo "Expected exit code 2, got: $exit_code"
  echo "Expected output:"
  echo "$expected"
  echo "Got:"
  echo "$output"
  exit 1
fi
echo

# Test 19: --refresh rebuild with changes (new wine, removed wine, qty change)
echo "Test 19: Refresh rebuild with changes"
# Create a modified CSV: remove Allegrini, change Billecart-Salmon qty 8->5, add new wine
python3 -c "
import csv
with open('cellar.test.csv', 'r', encoding='latin-1') as f:
    reader = csv.reader(f)
    rows = list(reader)
header = rows[0]
data = rows[1:]
qty_idx = header.index('Quantity')
producer_idx = header.index('Producer')
data = [r for r in data if r[producer_idx] != 'Allegrini']
billecart_idx = next(i for i, r in enumerate(data) if r[producer_idx] == 'Billecart-Salmon')
data[billecart_idx][qty_idx] = '5'
data.append(['White','Dry','750ml','USD','25.00','0','6','6','0','2023','Chablis Premier Cru','France, Burgundy, Chablis','Domaine Testeur','Chardonnay','France','Burgundy','Chablis','2025','2030','92',''])
with open('cellar.test.csv', 'w', encoding='latin-1', newline='') as f:
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)
    writer.writerow(header)
    writer.writerows(data)
"
exit_code=0
output=$(uv run python winebuddy.py --cellar-name ./cellar.test --refresh 2>/dev/null) || exit_code=$?
expected=$(cat "test19.expected")
if [ "$output" = "$expected" ] && [ "$exit_code" = "2" ]; then
  echo "PASS: Refresh rebuild with changes"
else
  echo "FAIL: Refresh rebuild with changes"
  echo "Expected exit code 2, got: $exit_code"
  echo "Expected output:"
  echo "$expected"
  echo "Got:"
  echo "$output"
  exit 1
fi
# Restore original CSV from git
git checkout cellar.test.csv 2>/dev/null
echo

# Clean up refresh test artifacts
rm -f cellar.test.db

echo "=== All tests passed! ==="

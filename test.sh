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
  output=$(uv run python winebuddy.py --cellar-name cellar.test "${cmd_args[@]}")
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

echo "=== All tests passed! ==="

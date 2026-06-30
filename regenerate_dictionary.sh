#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 parse_dictionary.py
python3 generate_directory_pages.py

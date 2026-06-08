#!/usr/bin/env python3
"""Parse the raw dictionary text in start.html into CSV and JSON datasets."""
from pathlib import Path
import csv
import json

SRC = Path('start.html')
CSV_OUT = Path('dictionary.csv')
JSON_OUT = Path('dictionary.json')


def parse_dictionary_text(text):
    lines = text.splitlines()
    start_index = None
    for i, line in enumerate(lines):
        if line.strip().lower().startswith('german, lithuanian'):
            start_index = i + 1
            break
    if start_index is None:
        raise ValueError('Could not find the dictionary header line in start.html')

    entries = []
    for line in lines[start_index:]:
        if not line.strip():
            continue
        parts = [part.strip() for part in line.split(',') if part.strip()]
        if not parts:
            continue
        headword = parts[0]
        translations = parts[1:]
        entries.append({'headword': headword, 'translations': translations})

    if not entries:
        raise ValueError('No dictionary entries were parsed from start.html')
    return entries


def write_csv(entries, path):
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(['headword', 'translations'])
        for entry in entries:
            writer.writerow([entry['headword'], '; '.join(entry['translations'])])


def write_json(entries, path):
    payload = {
        'source': 'Lexicon Lithuanicum',
        'language': 'German-Lithuanian',
        'dialect': 'East Prussia',
        'entries': entries,
    }
    with path.open('w', encoding='utf-8') as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def main():
    text = SRC.read_text(encoding='utf-8')
    entries = parse_dictionary_text(text)
    write_csv(entries, CSV_OUT)
    write_json(entries, JSON_OUT)
    print(f'Parsed {len(entries)} entries from {SRC.name}')
    print(f'Wrote {CSV_OUT.name} and {JSON_OUT.name}')


if __name__ == '__main__':
    main()

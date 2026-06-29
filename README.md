# Lexicon Lithuanicum

Handwritten 17th-century German–Lithuanian dictionary (East Prussia dialect).

This repository preserves the raw dictionary source and provides structured data for reuse.

## Contents

- `index.html` — repository landing page with links and a live dictionary search.
- `start.html` — raw source text with metadata and the dictionary entries.
- `search.html` — dedicated bilingual search page with German and Lithuanian inputs and a recent search history.
- `dictionary.csv` — structured dataset with German headwords and Lithuanian translations.
- `dictionary.json` — structured JSON dataset for programmatic use.
- `parse_dictionary.py` — parser script to regenerate the dataset from `start.html`.

## Usage

1. Regenerate the dataset:
   ```bash
   python3 parse_dictionary.py
   ```

2. Regenerate the directory pages from the updated source:
   ```bash
   python3 generate_directory_pages.py
   ```

3. Use `dictionary.csv` for spreadsheet or data analysis tools.
4. Use `dictionary.json` for web apps or scripts.

## Notes

- The source preserves historic orthography and East Prussian German–Lithuanian forms.
- The files are encoded in UTF-8.
- `dictionary.csv` uses semicolons to separate multiple translations in a single field.

## License

This repository uses the terms in `LICENSE`.

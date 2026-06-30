#!/usr/bin/env python3
from pathlib import Path
from collections import OrderedDict
import json
import unicodedata

SRC = Path('start.html')
DICTIONARY_JSON = Path('dictionary.json')

DE_LT_PAGE_KEYS = [chr(c) for c in range(ord('a'), ord('z') + 1)] + ['ue']
LT_DE_PAGE_KEYS = [chr(c) for c in range(ord('a'), ord('z') + 1)] + ['ss']

NAV_LT_DE = ' | '.join(
    f'<a href="az-directory-lt-de-{key}.html">{"ß" if key == "ss" else key.upper()}</a>'
    for key in LT_DE_PAGE_KEYS
)
NAV_DE_LT = ' | '.join(
    f'<a href="az-directory-de-lt-{key}.html">{"Ü" if key == "ue" else key.upper()}</a>'
    for key in DE_LT_PAGE_KEYS
)

HTML_HEAD = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    body {{ font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 1.5rem; color: #111; background: #f9fafb; }}
    main {{ max-width: 900px; margin: 0 auto; }}
    h1, h2 {{ color: #0b3d91; }}
    a {{ color: #0b3d91; }}
    .card {{ background: white; border: 1px solid #d1d5db; border-radius: 0.75rem; padding: 1.25rem; margin-top: 1rem; }}
    .nav {{ margin: 1rem 0 1.5rem; line-height: 1.8; }}
  </style>
</head>
<body>
<main>
  <h1>{heading}</h1>
  {content}
</main>
</body>
</html>
'''


def normalize_first_letter(text: str) -> str:
    if not text:
        return ''
    first = text[0]
    base = unicodedata.normalize('NFKD', first)
    base = ''.join(ch for ch in base if not unicodedata.combining(ch))
    return base.lower()


def letter_key_lt(word: str) -> str:
    if not word:
        return 'a'
    first = word[0].lower()
    if first == 'ß':
        return 'ss'
    base = normalize_first_letter(word)
    return base[0] if base and base[0].isalpha() else first


def letter_key_de(word: str) -> str:
    if not word:
        return 'a'
    first = word[0].lower()
    if first == 'ü':
        return 'ue'
    base = normalize_first_letter(word)
    return base[0] if base and base[0].isalpha() else first


def parse_entries_from_start_html(path: Path = SRC):
    text = path.read_text(encoding='utf-8')
    lines = text.splitlines()
    start_index = None
    for i, line in enumerate(lines):
        if line.strip().lower().startswith('german, lithuanian'):
            start_index = i + 1
            break
    if start_index is None:
        raise RuntimeError('Could not locate dictionary header line in start.html')

    entries = []
    for line in lines[start_index:]:
        if not line.strip():
            continue
        parts = [part.strip() for part in line.split(',') if part.strip()]
        if not parts:
            continue
        headword = parts[0]
        translations = [translation for translation in parts[1:] if translation]
        if not translations:
            continue
        entries.append({'headword': headword, 'translations': translations})
    return entries


def parse_entries_from_dictionary_json(path: Path = DICTIONARY_JSON):
    payload = json.loads(path.read_text(encoding='utf-8'))
    entries = payload.get('entries', [])
    return [
        {'headword': entry['headword'], 'translations': entry.get('translations', [])}
        for entry in entries
    ]


def parse_entries(path: Path | None = None):
    if path is None:
        path = DICTIONARY_JSON if DICTIONARY_JSON.exists() else SRC
    if path == DICTIONARY_JSON or path.suffix == '.json':
        return parse_entries_from_dictionary_json(path)
    return parse_entries_from_start_html(path)


def build_reverse(entries):
    reverse = OrderedDict()
    for entry in entries:
        german = entry['headword']
        for lith in entry['translations']:
            if lith not in reverse:
                reverse[lith] = []
            if german not in reverse[lith]:
                reverse[lith].append(german)
    return reverse


def render_list(items):
    if not items:
        return '  <div class="card">\n    <h2>No entries available yet for this letter.</h2>\n  </div>'
    rows = []
    for headword, translations in items:
        text = ' ; '.join(translations).replace(' ; ', '; ')
        rows.append(f'      <li><strong>{headword}</strong> — {text}</li>')
    return '  <div class="card">\n    <h2>Entries starting with {display_letter}</h2>\n    <ul>\n' + '\n'.join(rows) + '\n    </ul>\n  </div>'


def render_page(title, heading, content):
    return HTML_HEAD.format(title=title, heading=heading, content=content)


def render_letter_page(direction, key, display_letter, items, back_label, back_href, heading):
    nav = NAV_LT_DE if direction == 'lt-de' else NAV_DE_LT
    list_items = []
    for headword, translations in items:
        joined = '; '.join(translations)
        list_items.append(f'      <li><strong>{headword}</strong> — {joined}</li>')
    if list_items:
        content = f'  <div class="nav">{nav}</div>\n  <p><a href="{back_href}">{back_label}</a></p>\n  <p><a href="search.html">Search | Lexicon Lithuanicum dictionary</a></p>\n  <div class="card">\n    <h2>Entries starting with {display_letter}</h2>\n    <ul>\n' + '\n'.join(list_items) + '\n    </ul>\n  </div>'
    else:
        content = f'  <div class="nav">{nav}</div>\n  <p><a href="{back_href}">{back_label}</a></p>\n  <p><a href="search.html">Search | Lexicon Lithuanicum dictionary</a></p>\n  <div class="card">\n    <h2>Entries starting with {display_letter}</h2>\n    <ul>\n      <li>No entries available yet for this letter.</li>\n    </ul>\n  </div>'
    return render_page(title=f'A-Z Directory {direction.upper()} — {display_letter}', heading=heading, content=content)


def main():
    entries = parse_entries()
    reverse = build_reverse(entries)

    # German-to-Lithuanian pages
    german_pages = {key: [] for key in DE_LT_PAGE_KEYS}
    for entry in entries:
        page = letter_key_de(entry['headword'])
        if page not in german_pages:
            continue
        german_pages[page].append((entry['headword'], entry['translations']))

    for key in DE_LT_PAGE_KEYS:
        display_letter = 'Ü' if key == 'ue' else key.upper()
        items = sorted(german_pages[key], key=lambda pair: pair[0].casefold())
        page_content = render_letter_page(
            direction='de-lt',
            key=key,
            display_letter=display_letter,
            items=items,
            back_label='Back to DE-LT directory',
            back_href='az-directory-de-lt.html',
            heading=f'A-Z Directory DE-LT — {display_letter}',
        )
        Path(f'az-directory-de-lt-{key}.html').write_text(page_content, encoding='utf-8')

    # Lithuanian-to-German pages
    lt_pages = {key: [] for key in LT_DE_PAGE_KEYS}
    for lith, german_words in reverse.items():
        page = letter_key_lt(lith)
        if page not in lt_pages:
            continue
        lt_pages[page].append((lith, german_words))

    for key in LT_DE_PAGE_KEYS:
        display_letter = 'ß' if key == 'ss' else key.upper()
        items = sorted(lt_pages[key], key=lambda pair: pair[0].casefold())
        page_content = render_letter_page(
            direction='lt-de',
            key=key,
            display_letter=display_letter,
            items=items,
            back_label='Back to LT-DE directory',
            back_href='az-directory-lt-de.html',
            heading=f'A-Z Directory LT-DE — {display_letter}',
        )
        Path(f'az-directory-lt-de-{key}.html').write_text(page_content, encoding='utf-8')

    # main pages
    main_lt_de = render_page(
        title='A-Z Directory LT-DE',
        heading='A-Z Directory LT-DE',
        content=f'  <p>Browse the Lithuanian-to-German dictionary alphabetically.</p>\n  <div class="nav">{NAV_LT_DE}</div>\n  <div class="card">\n    <p>Select a letter to see the available Lithuanian entries and their German translations.</p>\n  </div>\n  <p><a href="search.html">Back to search</a></p>'
    )
    Path('az-directory-lt-de.html').write_text(main_lt_de, encoding='utf-8')

    main_de_lt = render_page(
        title='A-Z Directory DE-LT',
        heading='A-Z Directory DE-LT',
        content=f'  <p>Browse the German-to-Lithuanian dictionary alphabetically.</p>\n  <div class="nav">{NAV_DE_LT}</div>\n  <div class="card">\n    <p>Select a letter to see the available German entries and their Lithuanian translations.</p>\n  </div>\n  <p><a href="search.html">Back to search</a></p>'
    )
    Path('az-directory-de-lt.html').write_text(main_de_lt, encoding='utf-8')

    print('Regenerated DE-LT and LT-DE directory pages.')


if __name__ == '__main__':
    main()

import json
import tempfile
import unittest
from pathlib import Path
import importlib.util

MODULE_PATH = Path(__file__).resolve().parents[1] / 'generate_directory_pages.py'
spec = importlib.util.spec_from_file_location('generate_directory_pages', MODULE_PATH)
generate_directory_pages = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate_directory_pages)


class GenerateDirectoryPagesTests(unittest.TestCase):
    def test_load_entries_from_dictionary_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / 'dictionary.json'
            json_path.write_text(
                json.dumps(
                    {
                        'entries': [
                            {'headword': 'aal', 'translations': ['ungurys']},
                            {'headword': 'aarß', 'translations': ['subine', 'szikkinne']},
                        ]
                    }
                ),
                encoding='utf-8',
            )

            entries = generate_directory_pages.parse_entries_from_dictionary_json(json_path)

            self.assertEqual(entries[0]['headword'], 'aal')
            self.assertEqual(entries[0]['translations'], ['ungurys'])
            self.assertEqual(entries[1]['headword'], 'aarß')
            self.assertEqual(entries[1]['translations'], ['subine', 'szikkinne'])


if __name__ == '__main__':
    unittest.main()

# coding: utf-8
import os
import sys
import types
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'res', 'scripts', 'client', 'gui', 'mods'))
from wotstat_local_maps import localization


class LocalizationTest(unittest.TestCase):
    def test_client_locale_variants_and_fallback(self):
        self.assertEqual(localization.texts('ru_RU')['back'], u'НАЗАД')
        self.assertEqual(localization.texts('EN-us')['back'], u'BACK')
        for code in ('ja', ''):
            self.assertEqual(localization.texts(code), localization.texts('en'))
        self.assertEqual(localization.texts('uk-UA')['back'], u'НАЗАД')

    def test_automatic_selection_uses_client_language(self):
        original = sys.modules.get('helpers')
        helpers = types.ModuleType('helpers')
        helpers.getClientLanguage = lambda: 'pl'
        sys.modules['helpers'] = helpers
        try:
            self.assertEqual(localization.texts(), localization.texts('pl'))
            self.assertEqual(localization.text('close'), u'Zamknij')
            helpers.getClientLanguage = lambda: None
            self.assertEqual(localization.texts(), localization.texts('en'))
        finally:
            if original is None:
                del sys.modules['helpers']
            else:
                sys.modules['helpers'] = original

    def test_all_languages_are_complete_unicode_and_independent(self):
        keys = set(localization.texts('en'))
        for code in ('en', 'ru', 'pl', 'de', 'cs', 'uk', 'fr', 'es', 'it', 'tr', 'hu'):
            labels = localization.texts(code)
            self.assertEqual(set(labels), keys, code)
            self.assertTrue(all(isinstance(value, unicode) and value.strip() for value in labels.values()), code)
            labels['title'] = u'changed'
            self.assertNotEqual(localization.texts(code)['title'], u'changed')


if __name__ == '__main__':
    unittest.main()

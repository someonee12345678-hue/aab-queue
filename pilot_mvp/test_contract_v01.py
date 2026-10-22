"""AAB-001 frozen acceptance contract v0.1. Standard library only.

Candidate implementation must be supplied as pilot_impl.py beside this file.
Tests are reviewer-owned; do not change them to manufacture a pass.
"""
import copy
import unittest

from pilot_impl import normalize_label, unique_labels


class NormalizeLabelTests(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(normalize_label(' USB  Adapter 2 '), 'usb-adapter-2')
        self.assertEqual(normalize_label('A--B'), 'a-b')
        self.assertEqual(normalize_label('abc123'), 'abc123')

    def test_ascii_punctuation(self):
        self.assertEqual(normalize_label('..Hello___WORLD!!'), 'hello-world')
        self.assertEqual(normalize_label('!!!'), 'item')
        self.assertEqual(normalize_label(''), 'item')

    def test_non_ascii_and_types(self):
        self.assertEqual(normalize_label('Été'), 't')
        for bad in (None, 123, ['a']):
            with self.subTest(bad=bad):
                with self.assertRaises(TypeError):
                    normalize_label(bad)


class UniqueLabelsTests(unittest.TestCase):
    def test_dependencies_and_order(self):
        self.assertEqual(unique_labels(['Alpha','alpha','alpha-2','ALPHA']),
                         ['alpha','alpha-2','alpha-2-2','alpha-3'])

    def test_empty_and_collision(self):
        self.assertEqual(unique_labels(['', '!!!', 'item']),
                         ['item', 'item-2', 'item-3'])
        self.assertEqual(unique_labels([]), [])

    def test_does_not_mutate(self):
        vals=['A B', 'a--b', 'C']
        old=copy.deepcopy(vals)
        self.assertEqual(unique_labels(vals), ['a-b','a-b-2','c'])
        self.assertEqual(vals,old)

    def test_types(self):
        for bad in (None, 'abc', 3, ('a',)):
            with self.subTest(bad=bad):
                with self.assertRaises(TypeError):
                    unique_labels(bad)
        with self.assertRaises(TypeError):
            unique_labels(['good', 7])


if __name__ == '__main__':
    unittest.main()

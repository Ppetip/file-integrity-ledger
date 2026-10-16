import unittest
import tool

class BehaviorTests(unittest.TestCase):
    def test_case_0(self):
        self.assertEqual([x["kind"] for x in tool.analyze({'before': {}, 'after': {}})], [])

    def test_case_1(self):
        self.assertEqual([x["kind"] for x in tool.analyze({'before': {'a': '1', 'b': '2'}, 'after': {'a': '3', 'c': '4'}})], ['modified', 'removed', 'added'])

    def test_case_2(self):
        self.assertEqual([x["kind"] for x in tool.analyze({'before': {'x': 'a'}, 'after': {'x': 'a'}})], [])

    def test_missing_required_input(self):
        with self.assertRaises((KeyError, ValueError, TypeError)):
            tool.analyze({})


    def test_snapshot_detects_actual_modification(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'a'; path.write_text('first')
            baseline=tool.snapshot(directory)
            path.write_text('second')
            self.assertEqual(tool.analyze(dict(before=baseline,after=tool.snapshot(directory))),[dict(kind='modified',path='a')])
    def test_snapshot_budget(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory)/'a').write_bytes(b'123')
            with self.assertRaises(ValueError): tool.snapshot(directory,2)

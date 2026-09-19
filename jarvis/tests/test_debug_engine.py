import unittest
from jarvis.debug_engine import DebugEngine

class TestDebugEngine(unittest.TestCase):
    def test_diagnose(self):
        d = DebugEngine().diagnose(ValueError("bad"), "x")
        r = DebugEngine().propose_fix(d)
        self.assertEqual(r.diagnostic.error_type, "ValueError")
        self.assertTrue(r.fix)

if __name__ == "__main__":
    unittest.main()

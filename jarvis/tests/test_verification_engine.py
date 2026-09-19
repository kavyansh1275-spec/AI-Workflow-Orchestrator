import unittest
from jarvis.verification_engine import VerificationEngine

class TestVerificationEngine(unittest.TestCase):
    def test_checks(self):
        e = VerificationEngine()
        e.register("ok", lambda: True)
        e.register("bad", lambda: False)
        r = e.verify()
        self.assertTrue(r[0].passed)
        self.assertFalse(r[1].passed)

if __name__ == "__main__":
    unittest.main()

import unittest
from jarvis.self_debugger import SelfDebugger

class TestSelfDebugger(unittest.TestCase):
    def test_recovery(self):
        state = [0]
        def check():
            state[0] += 1
            return state[0] >= 2
        r = SelfDebugger(3).run_check(check)
        self.assertTrue(r.fixed)
        self.assertEqual(r.attempts, 2)

if __name__ == "__main__":
    unittest.main()

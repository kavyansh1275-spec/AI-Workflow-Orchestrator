import unittest
from jarvis.system_status import SystemStatus
class TestSystemStatus(unittest.TestCase):
    def test_ready(self):
        self.assertTrue(SystemStatus(True,True,True,True,True).ready)
if __name__=="__main__": unittest.main()

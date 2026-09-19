import unittest
from jarvis.browser_tool import BrowserTool
class TestBrowserTool(unittest.TestCase):
    def test_url_validation(self):
        self.assertTrue(BrowserTool().open_url("https://example.com").ok)
        self.assertFalse(BrowserTool().open_url("file:///secret").ok)
if __name__ == "__main__": unittest.main()

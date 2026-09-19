import unittest
from jarvis.creative_agent import CreativeAgent
class TestCreativeAgent(unittest.TestCase):
    def test_plan(self):
        a=CreativeAgent(max_tasks=3)
        self.assertEqual([x.role for x in a.plan("cartoon")],["director","storyboarder","asset_designer"])
    def test_handler(self):
        a=CreativeAgent(); a.register("director",lambda x:"approved")
        self.assertEqual(a.execute("scene")[0],("director","approved"))
    def test_bad_role(self):
        with self.assertRaises(ValueError): CreativeAgent().register("hacker",lambda x:x)
if __name__=="__main__": unittest.main()

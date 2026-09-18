import unittest
from jarvis.creative_studio_engine import CreativeStudioEngine

class TestCreativeStudioEngine(unittest.TestCase):
    def setUp(self): self.engine = CreativeStudioEngine()
    def test_project_types(self):
        p = self.engine.create_project("Kids Cartoon", "animation")
        self.assertIn("storyboard", p.stages)
        self.assertEqual(self.engine.validate_project(p), ())
    def test_asset(self):
        a = self.engine.add_asset("Hero", "character", format="blend")
        self.assertEqual(a.metadata["format"], "blend")
    def test_invalid_medium(self):
        with self.assertRaises(ValueError): self.engine.create_project("x", "unknown")
    def test_workflows(self):
        self.assertIn("render", self.engine.blender_workflow())
        self.assertIn("export", self.engine.video_workflow())

if __name__ == "__main__": unittest.main()

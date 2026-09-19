import json, unittest
from jarvis.creative_studio_engine import CreativeStudioEngine
class TestCreativeStudioEngine(unittest.TestCase):
    def setUp(self): self.e=CreativeStudioEngine(".")
    def test_project_and_manifest(self):
        p=self.e.create_project("Kids Cartoon","animation")
        a=self.e.add_asset("Hero","character",format="blend")
        data=json.loads(self.e.create_manifest(p,[a]))
        self.assertEqual(data["medium"],"animation"); self.assertEqual(data["assets"][0]["name"],"Hero")
    def test_render_plan(self):
        r=self.e.plan_blender_render("scene.blend","render/frame")
        self.assertIn("-b",r.command); self.assertTrue(r.dry_run)
    def test_invalid(self):
        with self.assertRaises(ValueError): self.e.create_project("x","unknown")
if __name__=="__main__": unittest.main()

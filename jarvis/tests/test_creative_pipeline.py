import unittest
from jarvis.creative_pipeline import CreativePipeline
from jarvis.creative_studio_engine import CreativeAsset
class TestCreativePipeline(unittest.TestCase):
    def test_build(self):
        p=CreativePipeline(".")
        r=p.build("Forest Story","animation",[CreativeAsset("Hero","character",{})],"scene.blend","out/frame",True)
        self.assertTrue(r.valid); self.assertIsNotNone(r.render_plan)
    def test_missing_pair(self):
        r=CreativePipeline(".").build("x","image",blend_file="scene.blend")
        self.assertFalse(r.valid)
if __name__=="__main__": unittest.main()

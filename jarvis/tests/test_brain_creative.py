import unittest
from jarvis.brain import JarvisBrain
from jarvis.config import Config

class TestBrainCreative(unittest.TestCase):
    def test_creative_pipeline_is_available(self):
        c=Config("local-model","local",True,12,":memory:")
        brain=JarvisBrain(c)
        result=brain.handle("Create a 3D cartoon character in Blender")
        self.assertIn("Creative Pipeline: READY",result)
        self.assertIn("Medium: animation",result)

if __name__=="__main__": unittest.main()

import importlib
import unittest
from jarvis.skills.registry import SkillRegistry

class TestSkillModules(unittest.TestCase):
    def test_every_registered_skill_has_module(self):
        registry = SkillRegistry()
        for name in registry.list():
            module = importlib.import_module(f"jarvis.skills.{name}")
            self.assertEqual(module.get_skill().name, name)

if __name__ == "__main__":
    unittest.main()

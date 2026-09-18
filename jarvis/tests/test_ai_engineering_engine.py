import unittest

from jarvis.ai_engineering_engine import AIEngineeringEngine


class TestAIEngineeringEngine(unittest.TestCase):
    def setUp(self):
        self.engine = AIEngineeringEngine()

    def test_plan_transformer(self):
        plan = self.engine.plan_model("text classification")
        self.assertEqual(plan.architecture, "transformer")
        self.assertIn("attention", plan.components)
        self.assertTrue(plan.evaluation)

    def test_inspect_dataset(self):
        report = self.engine.inspect_dataset([
            {"x": 1, "y": 2},
            {"x": 1, "y": 2},
            {"x": None, "y": 3},
        ])
        self.assertEqual(report.rows, 3)
        self.assertEqual(report.columns, 2)
        self.assertEqual(report.missing_values, 1)
        self.assertEqual(report.duplicate_rows, 1)

    def test_validate_training_config(self):
        errors = self.engine.validate_training_config({
            "epochs": 0,
            "batch_size": -1,
            "learning_rate": 0,
            "validation_split": 1,
        })
        self.assertEqual(len(errors), 4)

    def test_valid_config(self):
        self.assertEqual(
            self.engine.validate_training_config({
                "epochs": 3,
                "batch_size": 8,
                "learning_rate": 0.001,
                "validation_split": 0.2,
            }),
            [],
        )


if __name__ == "__main__":
    unittest.main()

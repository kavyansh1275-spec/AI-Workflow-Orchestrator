import unittest
from jarvis.ai_engineering_engine import AIEngineeringEngine

class TestAIEngineeringEngine(unittest.TestCase):
    def setUp(self): self.engine = AIEngineeringEngine()
    def test_plan_and_dataset(self):
        p = self.engine.plan_model("text classification")
        self.assertIn("attention", p.components)
        r = self.engine.inspect_dataset([{"x":1,"y":2},{"x":1,"y":2},{"x":None,"y":3}])
        self.assertEqual((r.rows,r.columns,r.missing_values,r.duplicate_rows),(3,2,1,1))
    def test_training_config(self):
        self.assertEqual(len(self.engine.validate_training_config({"epochs":0,"batch_size":-1,"learning_rate":0,"validation_split":1})),4)
        self.assertEqual(self.engine.validate_training_config({"epochs":3,"batch_size":8,"learning_rate":.001,"validation_split":.2}),[])
    def test_metrics(self):
        a=self.engine.classification_accuracy(["a","b","a"],["a","x","a"])
        self.assertAlmostEqual(a.value,2/3)
        m=self.engine.regression_mae([2,4],[1,7])
        self.assertAlmostEqual(m.value,2)
    def test_rag(self):
        self.assertGreaterEqual(len(self.engine.rag_pipeline_plan()),7)
        self.assertEqual(self.engine.validate_rag_config({"chunk_size":500,"top_k":5}),[])

if __name__ == "__main__": unittest.main()

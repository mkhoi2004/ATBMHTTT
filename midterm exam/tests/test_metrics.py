"""
Kiểm thử đơn vị cho mô-đun evaluate.py (các độ đo phân loại và FPR).
"""

import unittest
import numpy as np
from src.evaluate import calculate_metrics


class TestMetrics(unittest.TestCase):
    def test_perfect_classification(self):
        y_true = np.array([0, 0, 1, 1])
        y_pred = np.array([0, 0, 1, 1])
        y_prob = np.array([0.1, 0.2, 0.8, 0.9])

        m = calculate_metrics(y_true, y_pred, y_prob)
        self.assertEqual(m["accuracy"], 1.0)
        self.assertEqual(m["precision"], 1.0)
        self.assertEqual(m["recall"], 1.0)
        self.assertEqual(m["f1"], 1.0)
        self.assertEqual(m["fpr"], 0.0)
        self.assertEqual(m["roc_auc"], 1.0)

    def test_imperfect_classification(self):
        # 2 TN, 1 FP, 1 FN, 2 TP
        y_true = np.array([0, 0, 0, 1, 1, 1])
        y_pred = np.array([0, 0, 1, 0, 1, 1])

        m = calculate_metrics(y_true, y_pred)
        self.assertAlmostEqual(m["accuracy"], 4 / 6)
        self.assertEqual(m["tp"], 2)
        self.assertEqual(m["fp"], 1)
        self.assertEqual(m["tn"], 2)
        self.assertEqual(m["fn"], 1)
        self.assertAlmostEqual(m["fpr"], 1 / 3)  # FP / (FP + TN) = 1 / 3
        self.assertAlmostEqual(m["recall"], 2 / 3)  # TP / (TP + FN) = 2 / 3


if __name__ == "__main__":
    unittest.main()

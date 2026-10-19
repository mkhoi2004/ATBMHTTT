"""
Kiểm thử đơn vị cho mô-đun data_loader.py và features.py.
"""

import unittest
import numpy as np
import pandas as pd
from src.features import parse_ember_record_to_features, FeaturePreprocessor, PE_HEADER_FEATURES
from src.data_loader import get_random_split, get_temporal_split


class TestDataLoaderAndFeatures(unittest.TestCase):
    def setUp(self):
        self.mock_ember_record = {
            "sha256": "abcdef123456",
            "appeared": "2018-05",
            "label": 1,
            "general": {
                "size": 10240,
                "vsize": 20480,
                "has_debug": 1,
                "exports": 0,
                "imports": 25,
                "has_relocations": 1,
                "has_resources": 1,
                "has_signature": 0,
                "has_tls": 0,
                "symbols": 0,
            },
            "header": {
                "coff": {
                    "timestamp": 1525132800,
                    "machine": "I386",
                    "characteristics": 258,
                },
                "optional": {
                    "subsystem": "WINDOWS_GUI",
                    "dll_characteristics": 33088,
                    "magic": "PE32",
                    "major_image_version": 1,
                    "minor_image_version": 0,
                    "major_linker_version": 14,
                    "minor_linker_version": 0,
                    "major_operating_system_version": 6,
                    "minor_operating_system_version": 0,
                    "major_subsystem_version": 6,
                    "minor_subsystem_version": 0,
                    "sizeof_code": 4096,
                    "sizeof_headers": 1024,
                    "sizeof_heap_commit": 4096,
                },
            },
            "section": {
                "sections": [
                    {"name": ".text", "size": 4096, "entropy": 6.2, "vsize": 4000},
                    {"name": ".data", "size": 2048, "entropy": 3.1, "vsize": 1800},
                ]
            },
            "datadirectories": [
                {"name": "IMPORT_TABLE", "size": 128},
                {"name": "RESOURCE_TABLE", "size": 512},
            ],
        }

    def test_parse_record(self):
        row = parse_ember_record_to_features(self.mock_ember_record)
        self.assertEqual(row["sha256"], "abcdef123456")
        self.assertEqual(row["appeared"], "2018-05")
        self.assertEqual(row["label"], 1)
        self.assertEqual(row["sections_count"], 2)
        self.assertAlmostEqual(row["sections_mean_size"], (4096 + 2048) / 2)
        self.assertEqual(row["machine_type"], 332)  # I386 code
        for feat in PE_HEADER_FEATURES:
            self.assertIn(feat, row, f"Missing feature: {feat}")

    def test_temporal_split(self):
        data = {
            "appeared": ["2018-01", "2018-03", "2018-08", "2018-09", "2018-12"],
            "label": [0, 1, 0, 1, 0],
            "val": [1, 2, 3, 4, 5],
        }
        df = pd.DataFrame(data)
        train_df, test_df = get_temporal_split(df, train_months=["2018-01", "2018-03", "2018-08"], test_months=["2018-09", "2018-12"])

        self.assertEqual(len(train_df), 3)
        self.assertEqual(len(test_df), 2)
        # Kiểm tra không có rò rỉ tháng
        self.assertTrue(set(train_df["appeared"]).isdisjoint(set(test_df["appeared"])))

    def test_preprocessor_no_fit_raises(self):
        pre = FeaturePreprocessor(feature_names=["f1", "f2"])
        df = pd.DataFrame({"f1": [1, 2], "f2": [3, 4]})
        with self.assertRaises(RuntimeError):
            pre.transform(df)


if __name__ == "__main__":
    unittest.main()

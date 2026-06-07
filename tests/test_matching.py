"""Tests for the ATS matching and scoring logic."""

import unittest

from src.llm_client import AppError
from src.scoring import calculate_match_score, extract_keywords, ROLE_PRESETS
from src.database import metrics_summary
from src.routes import _validate_training_file, _validate_text_inputs


class MatchingTests(unittest.TestCase):
    def test_backend_keywords_match_resume(self):
        result = calculate_match_score(
            "Built Python Flask APIs with SQL and Git.",
            "Need Python backend developer with Flask, SQL, REST API, Git, and testing.",
            "backend",
        )
        self.assertGreaterEqual(result["score"], 50)
        self.assertIn("python", result["matched_keywords"])

    def test_training_dataset_is_valid(self):
        result = _validate_training_file()
        self.assertTrue(result["valid"], result["issues"])
        self.assertGreaterEqual(result["count"], 4)

    def test_rejects_invalid_role(self):
        with self.assertRaises(AppError):
            _validate_text_inputs("Python resume", "Python job", "invalid-role", "professional")

    def test_metrics_summary_shape(self):
        result = metrics_summary()
        self.assertIn("runs", result)
        self.assertIn("feedback", result)

    def test_all_role_presets_have_skills(self):
        for key, preset in ROLE_PRESETS.items():
            self.assertIn("label", preset, f"Missing label for role: {key}")
            self.assertIn("skills", preset, f"Missing skills for role: {key}")
            self.assertGreater(len(preset["skills"]), 0, f"Empty skills for role: {key}")

    def test_empty_resume_empty_job_raises(self):
        with self.assertRaises(AppError):
            _validate_text_inputs("", "", "backend", "professional")

    def test_extract_keywords_limits_output(self):
        keywords = extract_keywords(
            "python flask sql api git docker testing django fastapi postgresql mysql rest api",
            role_key="backend",
            limit=5,
        )
        self.assertLessEqual(len(keywords), 5)

    def test_score_zero_on_no_overlap(self):
        result = calculate_match_score(
            "Graphic designer with Photoshop.",
            "Python backend developer with Flask, SQL.",
            "backend",
        )
        self.assertLessEqual(result["score"], 30)

    def test_rejects_invalid_tone(self):
        with self.assertRaises(AppError):
            _validate_text_inputs("resume", "job", "backend", "invalid-tone")


if __name__ == "__main__":
    unittest.main()

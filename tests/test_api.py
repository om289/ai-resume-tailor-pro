"""Tests for resume tailor Flask API endpoints."""

import unittest

from app import create_app


class TestWebRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_index_get(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Resume Tailor", resp.data)

    def test_health_endpoint(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("prompt_version", data)
        self.assertIn("training_dataset", data)

    def test_metrics_endpoint(self):
        resp = self.client.get("/metrics")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("runs", data)
        self.assertIn("feedback", data)
        self.assertIn("average_score", data)

    def test_api_runs_empty(self):
        resp = self.client.get("/api/runs")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("runs", data)

    def test_api_run_not_found(self):
        resp = self.client.get("/api/runs/nonexistent")
        self.assertEqual(resp.status_code, 404)

    def test_export_not_found(self):
        resp = self.client.get("/export/nonexistent.txt")
        self.assertEqual(resp.status_code, 404)

    def test_api_analyze_local_mode(self):
        resp = self.client.post(
            "/api/analyze",
            json={
                "resume_text": "Python developer with Flask, SQL, Git experience.",
                "job_text": "Junior backend developer with Python, Flask, SQL, Git, testing.",
                "role": "backend",
                "tone": "professional",
                "use_ai": False,
                "model_profile": "base",
            },
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("score", data)
        self.assertIn("output", data)
        self.assertIn("run_id", data)
        self.assertEqual(data["source"], "local")

    def test_api_analyze_empty_inputs(self):
        resp = self.client.post(
            "/api/analyze",
            json={"resume_text": "", "job_text": ""},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_api_analyze_invalid_role(self):
        resp = self.client.post(
            "/api/analyze",
            json={
                "resume_text": "Some resume",
                "job_text": "Some job",
                "role": "invalid-role",
            },
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_api_feedback_invalid_run(self):
        resp = self.client.post(
            "/api/feedback",
            json={"run_id": "fake", "rating": 5},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 404)

    def test_api_feedback_invalid_rating(self):
        # First create a run to get a valid run_id
        run_resp = self.client.post(
            "/api/analyze",
            json={
                "resume_text": "Python dev with Flask.",
                "job_text": "Need Python Flask developer.",
                "role": "backend",
                "tone": "professional",
                "use_ai": False,
            },
            content_type="application/json",
        )
        run_id = run_resp.get_json()["run_id"]

        resp = self.client.post(
            "/api/feedback",
            json={"run_id": run_id, "rating": 10},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)


class TestScoringIntegration(unittest.TestCase):
    """Test the scoring module via the API for end-to-end validation."""

    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_high_match_score(self):
        resp = self.client.post(
            "/api/analyze",
            json={
                "resume_text": "Built Python Flask REST APIs with SQL, Git, Docker, and testing.",
                "job_text": "Python backend developer with Flask, SQL, REST API, Git, Docker, and testing.",
                "role": "backend",
                "tone": "professional",
                "use_ai": False,
            },
            content_type="application/json",
        )
        data = resp.get_json()
        self.assertGreaterEqual(data["score"], 50)

    def test_low_match_score(self):
        resp = self.client.post(
            "/api/analyze",
            json={
                "resume_text": "Graphic designer with Photoshop and Illustrator experience.",
                "job_text": "Python backend developer with Flask, SQL, REST API, Git, Docker.",
                "role": "backend",
                "tone": "professional",
                "use_ai": False,
            },
            content_type="application/json",
        )
        data = resp.get_json()
        self.assertLessEqual(data["score"], 30)


if __name__ == "__main__":
    unittest.main()

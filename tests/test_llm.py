"""Tests for the resume tailor LLM client — mocked API calls, retry, and errors."""

import unittest
from unittest.mock import MagicMock, patch

from src.config import Settings
from src.llm_client import AppError, LLMAPIError, LLMRateLimitError, LLMTimeoutError


class TestTailorClient(unittest.TestCase):
    def _make_client(self):
        """Create a TailorClient with a mocked OpenAI constructor."""
        with patch.dict("os.environ", {"AI_API_KEY": "test-key"}, clear=False):
            from src.llm_client import TailorClient
            cfg = Settings()
            with patch("src.llm_client.OpenAI"):
                client = TailorClient(cfg, model_profile="base")
        return client

    @patch("src.llm_client.OpenAI")
    def test_generate_returns_content(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        mock_choice = MagicMock()
        mock_choice.message.content = "1. Match Summary\nGreat match."
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        with patch.dict("os.environ", {"AI_API_KEY": "test-key"}, clear=False):
            from src.llm_client import TailorClient
            cfg = Settings()
            client = TailorClient(cfg)
            output, model = client.generate(
                "Python dev", "Python job", "backend", "professional", {"score": 80, "matched_keywords": [], "missing_keywords": []}
            )

        self.assertIn("Match Summary", output)
        self.assertTrue(model)

    def test_no_api_key_raises(self):
        with patch.dict("os.environ", {"AI_API_KEY": ""}, clear=False):
            from src.llm_client import TailorClient
            cfg = Settings()
            with self.assertRaises(AppError) as ctx:
                TailorClient(cfg)
            self.assertEqual(ctx.exception.status_code, 503)

    @patch("src.llm_client.OpenAI")
    @patch("src.llm_client.time.sleep")  # skip real sleep
    def test_retries_on_connection_error(self, mock_sleep, mock_openai_cls):
        from openai import APIConnectionError
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.side_effect = APIConnectionError(request=MagicMock())

        with patch.dict("os.environ", {"AI_API_KEY": "test-key", "LLM_MAX_RETRIES": "2"}, clear=False):
            from src.llm_client import TailorClient
            cfg = Settings()
            client = TailorClient(cfg)
            with self.assertRaises(LLMAPIError):
                client.generate(
                    "resume", "job", "backend", "professional",
                    {"score": 50, "matched_keywords": [], "missing_keywords": []},
                )

        self.assertEqual(mock_client.chat.completions.create.call_count, 2)


if __name__ == "__main__":
    unittest.main()

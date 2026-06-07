"""AI Resume Tailor Pro — Application factory and CLI."""

import argparse
import json
import logging
from pathlib import Path

from flask import Flask

from src.config import load_dotenv, settings
from src.database import init_db
from src.llm_client import TailorClient
from src.prompts import PROMPT_VERSION, build_local_output
from src.routes import bp, register_error_handlers, _validate_text_inputs, _validate_training_file
from src.scoring import ROLE_PRESETS, calculate_match_score


def _setup_logging() -> None:
    """Configure structured logging."""
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    if settings.LOG_FORMAT == "json":
        fmt = '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","msg":"%(message)s"}'
    else:
        fmt = "%(asctime)s %(levelname)s %(name)s %(message)s"

    logging.basicConfig(level=level, format=fmt, force=True)


def create_app() -> Flask:
    """Flask application factory."""
    load_dotenv()
    _setup_logging()

    application = Flask(__name__)
    application.config["SECRET_KEY"] = settings.SECRET_KEY
    application.config["MAX_CONTENT_LENGTH"] = settings.MAX_CONTENT_LENGTH

    # Security headers
    @application.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response

    application.register_blueprint(bp)
    register_error_handlers(application)

    init_db()

    logger = logging.getLogger("resume_tailor")
    for warning in settings.validate():
        logger.warning(warning)

    return application


def _cli_analyze(
    resume_text: str,
    job_text: str,
    role_key: str,
    tone: str,
    use_ai: bool,
    model_profile: str,
) -> str:
    """Run the analysis pipeline from the CLI."""
    _validate_text_inputs(resume_text, job_text, role_key, tone)
    match_report = calculate_match_score(resume_text, job_text, role_key)

    if use_ai:
        client = TailorClient(settings, model_profile=model_profile)
        output, _ = client.generate(resume_text, job_text, role_key, tone, match_report)
    else:
        output = build_local_output(match_report, role_key)

    return output


def main() -> None:
    """CLI entry point."""
    load_dotenv()
    _setup_logging()

    parser = argparse.ArgumentParser(description="Production-style AI resume tailor.")
    parser.add_argument("--resume", help="Path to resume text file for CLI mode.")
    parser.add_argument("--job", help="Path to job description text file for CLI mode.")
    parser.add_argument("--role", default="backend", choices=ROLE_PRESETS.keys())
    parser.add_argument("--tone", default="professional")
    parser.add_argument("--model-profile", default="base", choices=["base", "fine_tuned"])
    parser.add_argument("--use-ai", action="store_true", help="Call the LLM API.")
    parser.add_argument("--validate-data", action="store_true", help="Validate JSONL training data.")
    parser.add_argument("--host", default="127.0.0.1", help="Host for the web app.")
    parser.add_argument("--port", default=5002, type=int, help="Port for the web app.")
    args = parser.parse_args()

    if args.validate_data:
        print(json.dumps(_validate_training_file(), indent=2))
        return

    if args.resume and args.job:
        resume_text = Path(args.resume).read_text(encoding="utf-8")
        job_text = Path(args.job).read_text(encoding="utf-8")
        print(_cli_analyze(resume_text, job_text, args.role, args.tone, args.use_ai, args.model_profile))
        return

    application = create_app()
    application.run(host=args.host, port=args.port, debug=False, use_reloader=False)


app = create_app()


if __name__ == "__main__":
    main()

"""Flask routes — web UI and JSON API endpoints for resume tailor."""

from __future__ import annotations

import json
import logging
import os
import re
import uuid

from flask import Blueprint, Response, jsonify, render_template, request
from pathlib import Path

from src.config import settings
from src.database import (
    get_run,
    load_history,
    metrics_summary,
    save_feedback,
    save_run,
)
from src.llm_client import AppError, TailorClient
from src.prompts import PROMPT_VERSION, build_local_output
from src.scoring import ROLE_PRESETS, calculate_match_score

logger = logging.getLogger("resume_tailor")

bp = Blueprint("main", __name__)


def _sanitize_input(text: str) -> str:
    """Pass text unchanged. Sanitizing resumes/JDs by stripping <...> destroys content (e.g. skills, comparisons)."""
    return text


def _request_id() -> str:
    return uuid.uuid4().hex[:10]


def _check_api_key() -> None:
    """If APP_API_KEY is configured, require X-API-Key header on API routes."""
    if not settings.API_KEY:
        return
    provided = request.headers.get("X-API-Key", "")
    if provided != settings.API_KEY:
        raise AppError("Invalid or missing API key.", status_code=401)


def _validate_text_inputs(resume_text: str, job_text: str, role_key: str, tone: str) -> None:
    if not resume_text.strip() or not job_text.strip():
        raise AppError("Please provide both resume text and job description text.")
    if len(resume_text) > settings.MAX_RESUME_CHARS:
        raise AppError(f"Resume is too long. Limit it to {settings.MAX_RESUME_CHARS} characters.")
    if len(job_text) > settings.MAX_JOB_CHARS:
        raise AppError(f"Job description is too long. Limit it to {settings.MAX_JOB_CHARS} characters.")
    if role_key not in ROLE_PRESETS:
        raise AppError("Invalid role preset.")
    if tone not in {"professional", "confident", "student-friendly", "concise"}:
        raise AppError("Invalid writing tone.")


def _validate_training_file(path: Path | None = None) -> dict:
    """Validate the JSONL training dataset."""
    target = path or settings.TRAINING_PATH
    issues: list[str] = []
    count = 0
    if not target.exists():
        return {"valid": False, "count": 0, "issues": [f"Missing file: {target}"]}

    for line_number, line in enumerate(target.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        count += 1
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            issues.append(f"Line {line_number}: invalid JSON: {exc}")
            continue
        messages = item.get("messages")
        if not isinstance(messages, list) or len(messages) < 3:
            issues.append(f"Line {line_number}: messages must contain system, user, assistant")
            continue
        roles = [m.get("role") for m in messages if isinstance(m, dict)]
        if roles[:3] != ["system", "user", "assistant"]:
            issues.append(f"Line {line_number}: expected system/user/assistant roles")
        for mi, m in enumerate(messages, 1):
            if not isinstance(m.get("content"), str) or not m["content"].strip():
                issues.append(f"Line {line_number}, message {mi}: empty content")

    return {"valid": not issues, "count": count, "issues": issues}


def _analyze_application(
    resume_text: str,
    job_text: str,
    role_key: str,
    tone: str,
    use_ai: bool,
    model_profile: str = "base",
) -> dict:
    """Core analysis pipeline — scoring + optional LLM tailoring."""
    _validate_text_inputs(resume_text, job_text, role_key, tone)
    if model_profile not in {"base", "fine_tuned"}:
        raise AppError("Invalid model profile.")

    match_report = calculate_match_score(resume_text, job_text, role_key)

    if use_ai:
        client = TailorClient(settings, model_profile=model_profile)
        generated_output, selected_model = client.generate(
            resume_text, job_text, role_key, tone, match_report
        )
        source = "llm"
    else:
        generated_output = build_local_output(match_report, role_key)
        selected_model = "local-keyword-engine"
        source = "local"

    payload = {
        "role": role_key,
        "tone": tone,
        "source": source,
        "model_profile": model_profile,
        "model_name": selected_model,
        "score": match_report["score"],
        "match_report": match_report,
        "output": generated_output,
        "prompt_version": PROMPT_VERSION,
    }
    payload["run_id"] = save_run(payload)
    payload["id"] = payload["run_id"]
    return payload


def _sample_resume() -> str:
    if settings.SAMPLE_RESUME_PATH.exists():
        return settings.SAMPLE_RESUME_PATH.read_text(encoding="utf-8")
    return ""


def _sample_job() -> str:
    if settings.SAMPLE_JOB_PATH.exists():
        return settings.SAMPLE_JOB_PATH.read_text(encoding="utf-8")
    return ""


def _base_template_context(**overrides) -> dict:
    """Build the default template context, with optional overrides."""
    ctx = {
        "resume_text": _sample_resume(),
        "job_text": _sample_job(),
        "result": None,
        "error": None,
        "role_presets": ROLE_PRESETS,
        "selected_role": "backend",
        "tone": "professional",
        "use_ai": False,
        "model_profile": "base",
        "history": load_history(),
        "dataset_status": _validate_training_file(),
        "metrics": metrics_summary(),
        "model": settings.AI_MODEL,
    }
    ctx.update(overrides)
    return ctx


# ---------------------------------------------------------------------------
# Web routes
# ---------------------------------------------------------------------------

@bp.route("/", methods=["GET", "POST"])
def index():
    resume_text = _sanitize_input(request.form.get("resume_text", _sample_resume()))
    job_text = _sanitize_input(request.form.get("job_text", _sample_job()))
    role_key = request.form.get("role", "backend")
    tone = request.form.get("tone", "professional")
    model_profile = request.form.get("model_profile", "base")
    use_ai = request.form.get("use_ai") == "on"
    result = None
    error = None

    if request.method == "POST":
        try:
            result = _analyze_application(
                resume_text, job_text, role_key, tone, use_ai, model_profile
            )
        except AppError as exc:
            error = str(exc)
        except Exception as exc:
            logger.exception("Unexpected analysis failure")
            error = f"Unexpected error: {exc}"

    return render_template(
        "index.html",
        **_base_template_context(
            resume_text=resume_text,
            job_text=job_text,
            result=result,
            error=error,
            selected_role=role_key,
            tone=tone,
            use_ai=use_ai,
            model_profile=model_profile,
        ),
    )


@bp.post("/feedback")
def feedback_form():
    run_id = request.form.get("run_id", "")
    rating = int(request.form.get("rating", "0"))
    comment = _sanitize_input(request.form.get("comment", ""))
    save_feedback(run_id, rating, comment)
    return Response("Feedback saved. You can go back to the app.", mimetype="text/plain")


# ---------------------------------------------------------------------------
# JSON API routes
# ---------------------------------------------------------------------------

@bp.post("/api/analyze")
def api_analyze():
    _check_api_key()
    data = request.get_json(silent=True) or {}
    result = _analyze_application(
        _sanitize_input(data.get("resume_text", "")),
        _sanitize_input(data.get("job_text", "")),
        data.get("role", "backend"),
        data.get("tone", "professional"),
        bool(data.get("use_ai", False)),
        data.get("model_profile", "base"),
    )
    return jsonify(result)


@bp.get("/api/runs")
def api_runs():
    _check_api_key()
    limit = min(int(request.args.get("limit", 25)), 100)
    return jsonify({"runs": load_history(limit=limit)})


@bp.get("/api/runs/<run_id>")
def api_run(run_id: str):
    _check_api_key()
    record = get_run(run_id)
    if not record:
        return jsonify({"error": "Run not found"}), 404
    return jsonify(record)


@bp.post("/api/feedback")
def api_feedback():
    _check_api_key()
    data = request.get_json(silent=True) or {}
    feedback = save_feedback(
        data.get("run_id", ""),
        int(data.get("rating", 0)),
        _sanitize_input(data.get("comment", "")),
    )
    return jsonify(feedback), 201


@bp.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "model": settings.AI_MODEL,
        "fine_tuned_model_configured": settings.has_fine_tuned_model,
        "prompt_version": PROMPT_VERSION,
        "training_dataset": _validate_training_file(),
    })


@bp.get("/metrics")
def metrics():
    return jsonify(metrics_summary())


@bp.get("/export/<run_id>.txt")
def export_run(run_id: str):
    record = get_run(run_id)
    if not record:
        return Response("Run not found", status=404)
    text = f"""AI Resume Tailor Export
Run ID: {record["id"]}
Created: {record["created_at"]}
Role: {record["role"]}
Score: {record["score"]}%
Source: {record["source"]}
Model: {record["model_name"]}
Prompt Version: {record["prompt_version"]}

{record["output"]}
"""
    return Response(
        text,
        mimetype="text/plain",
        headers={"Content-Disposition": f"attachment; filename=resume-tailor-{run_id}.txt"},
    )


# ---------------------------------------------------------------------------
# Error handler (registered by the app factory)
# ---------------------------------------------------------------------------

def register_error_handlers(app):
    """Register error handlers on the Flask app."""

    @app.errorhandler(AppError)
    def handle_app_error(exc: AppError):
        if request.path.startswith("/api/"):
            return jsonify({"error": str(exc)}), exc.status_code
        return render_template(
            "index.html",
            **_base_template_context(
                resume_text=_sanitize_input(request.form.get("resume_text", _sample_resume())),
                job_text=_sanitize_input(request.form.get("job_text", _sample_job())),
                error=str(exc),
                selected_role=request.form.get("role", "backend"),
                tone=request.form.get("tone", "professional"),
                use_ai=request.form.get("use_ai") == "on",
                model_profile=request.form.get("model_profile", "base"),
            ),
        ), exc.status_code

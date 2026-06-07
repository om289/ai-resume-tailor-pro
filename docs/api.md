# API Reference

Base URL for local development:

```text
http://127.0.0.1:5002
```

## Health

```text
GET /health
```

Returns service status, active model config, prompt version, and training dataset health.

## Metrics

```text
GET /metrics
```

Returns total runs, feedback count, average score, and average rating.

## Analyze Resume

```text
POST /api/analyze
Content-Type: application/json
```

Request:

```json
{
  "resume_text": "Python intern with Flask, SQL, and Git experience.",
  "job_text": "Junior backend developer with Python, Flask, SQL, REST APIs, Git, and testing.",
  "role": "backend",
  "tone": "professional",
  "use_ai": false,
  "model_profile": "base"
}
```

Response includes:

- `score`
- `match_report`
- `output`
- `run_id`
- `model_name`
- `prompt_version`

## List Runs

```text
GET /api/runs?limit=25
```

## Get Run

```text
GET /api/runs/<run_id>
```

## Save Feedback

```text
POST /api/feedback
Content-Type: application/json
```

Request:

```json
{
  "run_id": "abc123",
  "rating": 5,
  "comment": "Good rewrite, but add more testing suggestions."
}
```

## Export Result

```text
GET /export/<run_id>.txt
```

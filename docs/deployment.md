# Deployment Notes

## Local Production-Like Run

Use Gunicorn on Linux/macOS:

```bash
gunicorn --bind 0.0.0.0:5002 wsgi:app
```

On Windows, use the Flask development server for demos:

```powershell
python app.py
```

## Docker

Create `.env` from `.env.example`, then run:

```bash
docker compose up --build
```

The app will be available at:

```text
http://127.0.0.1:5002
```

## Persistent Storage

The app uses SQLite at:

```text
storage/app.db
```

Docker Compose mounts `./storage` so run history and feedback survive container restarts.

## Production Checklist

- Set `AI_API_KEY` through environment variables
- Set `AI_FINE_TUNED_MODEL` after fine-tuning
- Put the app behind HTTPS
- Add authentication before storing real user resumes
- Replace SQLite with Postgres for multi-user production
- Add scheduled database backups
- Review privacy policy before collecting real applicant data

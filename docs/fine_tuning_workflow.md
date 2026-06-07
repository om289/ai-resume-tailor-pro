# Fine-Tuning Workflow

This project is designed to work in three stages.

## 1. Prompt-Based Prototype

The Flask app sends resume and job-description text to an LLM API with a strict system prompt. This proves the user workflow before training a custom model.

## 2. Dataset Collection

Training examples are stored in `data/train_examples.jsonl`. Each line contains a `messages` array with:

- `system`: behavior rules
- `user`: resume and job description
- `assistant`: ideal tailored output

Run validation:

```powershell
python app.py --validate-data
```

Or:

```powershell
python scripts/validate_dataset.py data/train_examples.jsonl
```

## 3. Fine-Tuning And Evaluation

After collecting enough examples, upload the JSONL file to a provider that supports chat fine-tuning. Then compare the base model and fine-tuned model using `data/eval_cases.jsonl`.

Useful metrics:

- Keyword recall
- Output section completeness
- Truthfulness against the original resume
- Human rating for clarity and relevance

For a college submission, 25-50 examples can demonstrate the pipeline. For a stronger production-like system, collect 150-500 examples across different roles.

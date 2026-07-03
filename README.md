# SafeX AI FAQ Assistant

A small AI/ML prototype for SafeX Solutions. It answers visitor questions using curated public website content from SafeX and serves a clean chat interface that can be deployed on Render.

## Why this prototype

The FAQ chatbot is the strongest first intern project because it is visible, deployable, business-focused, and clearly AI-related. It demonstrates how SafeX could reduce repetitive website inquiries and help visitors discover services faster.

## Features

- FastAPI backend with `/api/chat`
- Lightweight TF-IDF retrieval model, no paid API key required
- Curated SafeX knowledge base in `data/safex_knowledge.json`
- Responsive web chat UI
- Source links returned with each grounded answer
- Render-ready deployment configuration

## Run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Test

```bash
python -m unittest discover -s tests
```

## Deploy on Render

1. Push this project to GitHub.
2. Create a new Render Web Service.
3. Connect the GitHub repo.
4. Use these commands:

```text
Build command: pip install -r requirements.txt
Start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

The included `render.yaml` can also be used as a blueprint.

## Data sources

- https://safexsolutions.com/
- https://safexsolutions.com/sdc/
- https://safexsolutions.com/contact/

## Notes

This is a prototype, not an official SafeX production chatbot. The knowledge base should be reviewed by a SafeX team member before public deployment.



# Story Prose Generator ✍️

Turn narrative beats into vivid, emotionally grounded prose — co-authored with AI.

---

## 🧠 Why I Built This

As a fiction writer and AI engineer, I’ve always wanted a tool that could turn structured narrative inputs — the story beats we scribble, outline, and obsess over — into full, expressive prose that *feels* alive.

This project explores the intersection of creativity and computation. It’s a place where memory strategies, metadata, and language models come together to shape writing that isn’t just coherent, but human.

---

## 🚀 Live Demo

Want to try it?

[Explore the interactive API](https://story-prose-generator-415817045199.us-central1.run.app/docs#/default/test_route_api_test_get)

---

## ⚙️ Tech Stack

- **FastAPI** for the API layer
- **Anthropic Claude 3** for generative prose
- **LangChain** for prompt and memory logic
- **spaCy** for semantic evaluation
- **Google Cloud Run** for deployment
- **GitHub Actions** (coming soon) for CI/CD

---

## 📩 Endpoint

### `POST /api/generate`

Takes a list of story beats and optional metadata, and returns:

- Final prose
- Beat-level evaluations
- Optional coherence checks
- Optional metadata adherence scoring

---

## 🔐 Setup

1. Clone the repo
2. Add your `.env` file with your `ANTHROPIC_KEY`
3. Run locally:

```bash
uvicorn app.main:app --reload
```

---

## 💬 Want to collaborate?

I’m always open to ideas — especially if they sit at the edge of structured story and generative systems. Reach out or fork the project if you want to build on top of it.
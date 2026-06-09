# Job Search Assistant

A local, private job search workspace built with Streamlit and Ollama.  
All AI runs **on your machine** — no API keys, no subscriptions, no data leaving your computer.

---

## What it does

| Feature | Description |
|---|---|
| **Resume Feedback** | Upload your resume + paste a JD → keyword gap analysis, match score, health checks, and AI-written suggestions |
| **Cover Letter Generator** | Enter your experience and the job posting → a tailored, non-generic cover letter |
| **Application Tracker** | Track every application with status, dates, and notes |
| **Interview Prep** | Role-specific questions with guidance on what strong answers look like |

---

## Stack

- **Frontend / App**: [Streamlit](https://streamlit.io)
- **Local LLM**: [Ollama](https://ollama.com) running `llama3.2:3b`
- **NLP baseline**: scikit-learn TF-IDF (works offline, no Ollama required)
- **Database**: MongoDB with transparent in-memory fallback (runs without Mongo)
- **Auth**: bcrypt password hashing

The app works without Ollama and without MongoDB — both degrade gracefully.

---

## Quick start

### 1. Clone and install

```bash
git clone https://github.com/YOUR_USERNAME/job-search-assistant
cd job-search-assistant
pip install -r requirements.txt
```

### 2. Set up Ollama (for AI features)

```bash
# Install Ollama: https://ollama.com/download
ollama pull llama3.2:3b
ollama serve
```

The app shows a status indicator in the sidebar — green means AI features are live.

### 3. Set up MongoDB (optional)

If you skip this, the app uses in-memory storage (data resets on restart).

```bash
# macOS
brew install mongodb-community && brew services start mongodb-community

# Or use Docker
docker run -d -p 27017:27017 --name mongo mongo:7
```

Create your first user:

```bash
python create_user.py
```

### 4. Run

```bash
streamlit run app.py
```

---

## Configuration

Copy `.streamlit/secrets.toml` and set your MongoDB URI if needed:

```toml
MONGODB_URI = "mongodb://localhost:27017"
```

Or set the environment variable: `export MONGODB_URI="mongodb://localhost:27017"`

---

## Project structure

```
job-search-assistant/
├── app.py                    # Entry point, sidebar, routing
├── create_user.py            # CLI tool to create MongoDB users
├── requirements.txt
├── .streamlit/
│   ├── config.toml           # Streamlit theme
│   └── secrets.toml          # Local secrets (not committed)
├── utils/
│   ├── auth.py               # Login / register UI + bcrypt helpers
│   ├── database.py           # MongoDB client with in-memory fallback
│   ├── ollama_client.py      # All Ollama/LLM calls
│   ├── nlp_utils.py          # Local TF-IDF resume analysis (no API needed)
│   └── style.py              # CSS injection + HTML component helpers
└── views/
    ├── Resume_Feedback.py
    ├── Cover_Letter.py
    ├── Application_Tracker.py
    └── Interview_Prep.py
```

---

## Design decisions

**Why local AI?** Privacy. Your resume and job search data are sensitive. Nothing here phones home.

**Why the in-memory fallback?** Lower the barrier to running it. Clone, install, run — it works. MongoDB is opt-in for persistence.

**Why TF-IDF alongside Ollama?** The local analysis is instant and deterministic. The AI layer adds qualitative reasoning on top. If Ollama is unavailable, you still get a useful analysis.

---

## Limitations

- Scanned PDF resumes (image-based) will not parse — the text must be selectable
- The `llama3.2:3b` model is fast but not GPT-4. Expect good, not perfect, output
- Interview reminders are UI-only — no actual notification system

---

## License

MIT

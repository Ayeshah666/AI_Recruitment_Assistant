import requests
import json
from typing import Generator

OLLAMA_BASE = "http://localhost:11434"
MODEL = "llama3.2:3b"
TIMEOUT = 120  # seconds — 3b is fast but be generous


def _chat(messages: list[dict], stream: bool = False) -> tuple[str, bool]:
    """
    Send a chat request to Ollama.
    messages: list of {"role": "user"|"assistant"|"system", "content": str}
    Returns (text, success).
    """
    try:
        resp = requests.post(
            f"{OLLAMA_BASE}/api/chat",
            json={"model": MODEL, "messages": messages, "stream": False},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["message"]["content"].strip(), True
    except requests.exceptions.ConnectionError:
        return (
            "Cannot reach Ollama. Make sure it is running: `ollama serve`",
            False,
        )
    except requests.exceptions.Timeout:
        return "Ollama timed out. The model may still be loading — try again.", False
    except Exception as e:
        return f"Ollama error: {e}", False


def _stream_chat(messages: list[dict]) -> Generator[str, None, None]:
    """
    Streaming version — yields text chunks.
    Falls back to a single error string on failure.
    """
    try:
        with requests.post(
            f"{OLLAMA_BASE}/api/chat",
            json={"model": MODEL, "messages": messages, "stream": True},
            timeout=TIMEOUT,
            stream=True,
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if not chunk.get("done"):
                        yield chunk["message"]["content"]
    except requests.exceptions.ConnectionError:
        yield "\n\n⚠️ Cannot reach Ollama. Run `ollama serve` and reload."
    except Exception as e:
        yield f"\n\n⚠️ Error: {e}"


# ─────────────────────────────────────────────
# High-level task functions
# ─────────────────────────────────────────────

def analyze_resume(resume_text: str, job_description: str) -> tuple[str, bool]:
    """
    Compare a resume against a job description.
    Returns structured markdown feedback.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You are a senior technical recruiter who also writes great code. "
                "Give honest, specific, actionable resume feedback. "
                "Never pad your answer with generic advice. "
                "Use markdown formatting: ## headings, bullet points, and bold for key terms. "
                "Be concise — every sentence must earn its place."
            ),
        },
        {
            "role": "user",
            "content": (
                f"## Job Description\n{job_description}\n\n"
                f"## Resume\n{resume_text}\n\n"
                "Provide feedback in exactly these sections:\n"
                "## Match Score\n"
                "Give an estimated match percentage and one sentence explaining it.\n\n"
                "## Missing Keywords\n"
                "List keywords from the JD not present in the resume (max 10, as bullet points).\n\n"
                "## Strong Points\n"
                "What the resume does well for this role (3–5 bullets).\n\n"
                "## Critical Gaps\n"
                "What is missing or weak that would hurt the application (3–5 bullets).\n\n"
                "## Top 3 Actions\n"
                "Specific, concrete edits to make right now. Not generic advice."
            ),
        },
    ]
    return _chat(messages)


def generate_cover_letter(
    resume_text: str,
    job_description: str,
    company: str,
    position: str,
    tone: str,
) -> tuple[str, bool]:
    """
    Write a tailored cover letter.
    """
    tone_guide = {
        "Professional": "formal and confident, no slang",
        "Enthusiastic": "warm, energetic, genuine excitement — not sycophantic",
        "Concise": "tight and direct, under 250 words",
        "Creative": "shows personality, opens with a hook, avoids clichés",
    }.get(tone, "professional and confident")

    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert career coach who writes cover letters that get interviews. "
                "You write from the candidate's voice — never use hollow phrases like "
                "'I am excited to apply' or 'I am a team player'. "
                "Every claim must connect directly to evidence from the resume."
            ),
        },
        {
            "role": "user",
            "content": (
                f"## Resume\n{resume_text}\n\n"
                f"## Job Description\n{job_description}\n\n"
                f"Write a cover letter for the **{position}** role at **{company}**.\n"
                f"Tone: {tone_guide}\n\n"
                "Structure:\n"
                "- Opening paragraph: one specific thing from the JD that connects to a concrete achievement from the resume.\n"
                "- Middle paragraph: 2–3 skills/experiences from the resume that directly address requirements in the JD.\n"
                "- Closing paragraph: clear call to action, no filler.\n\n"
                "Output the letter only — no commentary before or after. "
                "Use placeholders [Your Name], [Your Email], [Your Phone] at the end."
            ),
        },
    ]
    return _chat(messages)


def generate_interview_questions(position: str, job_description: str = "") -> tuple[str, bool]:
    """
    Generate role-specific interview questions with guidance on how to answer them.
    """
    context = f"Job description context:\n{job_description}\n\n" if job_description else ""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a senior hiring manager who has conducted hundreds of interviews. "
                "Generate realistic, specific interview questions — not the tired generic ones. "
                "For each question, add a brief tip on what a strong answer looks like."
            ),
        },
        {
            "role": "user",
            "content": (
                f"{context}"
                f"Generate 8 interview questions for a **{position}** role.\n\n"
                "Format each as:\n"
                "**Q1. [Question]**\n"
                "_What a strong answer covers:_ [1–2 sentences]\n\n"
                "Mix: 3 technical/role-specific, 2 behavioral (STAR format), "
                "2 situational, 1 culture/motivation. "
                "Number them Q1 through Q8."
            ),
        },
    ]
    return _chat(messages)


def stream_cover_letter(
    resume_text: str,
    job_description: str,
    company: str,
    position: str,
    tone: str,
) -> Generator[str, None, None]:
    """Streaming version of generate_cover_letter for real-time display."""
    tone_guide = {
        "Professional": "formal and confident, no slang",
        "Enthusiastic": "warm, energetic, genuine excitement — not sycophantic",
        "Concise": "tight and direct, under 250 words",
        "Creative": "shows personality, opens with a hook, avoids clichés",
    }.get(tone, "professional and confident")

    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert career coach who writes cover letters that get interviews. "
                "You write from the candidate's voice — never use hollow phrases like "
                "'I am excited to apply' or 'I am a team player'. "
                "Every claim must connect directly to evidence from the resume."
            ),
        },
        {
            "role": "user",
            "content": (
                f"## Resume\n{resume_text}\n\n"
                f"## Job Description\n{job_description}\n\n"
                f"Write a cover letter for the **{position}** role at **{company}**.\n"
                f"Tone: {tone_guide}\n\n"
                "Structure:\n"
                "- Opening paragraph: one specific thing from the JD that connects to a concrete achievement from the resume.\n"
                "- Middle paragraph: 2–3 skills/experiences from the resume that directly address requirements in the JD.\n"
                "- Closing paragraph: clear call to action, no filler.\n\n"
                "Output the letter only. "
                "Use placeholders [Your Name], [Your Email], [Your Phone] at the end."
            ),
        },
    ]
    yield from _stream_chat(messages)


def check_ollama() -> tuple[bool, str]:
    """Ping Ollama and verify the model is available."""
    try:
        resp = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=5)
        resp.raise_for_status()
        models = [m["name"] for m in resp.json().get("models", [])]
        model_base = MODEL.split(":")[0]
        available = any(m.startswith(model_base) for m in models)
        if available:
            return True, f"Ollama running · {MODEL}"
        return False, f"Model '{MODEL}' not found. Run: ollama pull {MODEL}"
    except requests.exceptions.ConnectionError:
        return False, "Ollama not running. Start it with: ollama serve"
    except Exception as e:
        return False, f"Ollama check failed: {e}"

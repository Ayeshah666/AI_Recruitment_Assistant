import streamlit as st
import datetime
import re
from utils.database import db
from utils.style import fancy_divider, question_card, ollama_pill
from utils.ollama_client import check_ollama, generate_interview_questions
from utils.nlp_utils import ResumeAnalyzer


def _parse_questions(raw: str) -> list[tuple[str, str]]:
    """
    Parse Ollama output into (question, tip) pairs.
    Handles formats like:
        **Q1. Question text**
        _What a strong answer covers:_ tip text
    Falls back to splitting on numbered lines.
    """
    pairs: list[tuple[str, str]] = []

    # Try structured format first
    blocks = re.split(r"\*\*Q\d+[.:]\s*", raw)
    for block in blocks:
        if not block.strip():
            continue
        # Split on tip marker
        parts = re.split(r"_What a strong answer covers:?_\s*", block, flags=re.I)
        question = parts[0].strip().strip("*").strip()
        tip      = parts[1].strip() if len(parts) > 1 else ""
        if question:
            pairs.append((question, tip))

    # Fallback: plain numbered list  "1. Some question"
    if not pairs:
        for line in raw.splitlines():
            m = re.match(r"^\d+[.)]\s+(.+)", line.strip())
            if m:
                pairs.append((m.group(1).strip(), ""))

    # Last resort: split on blank lines, take non-empty chunks
    if not pairs:
        chunks = [c.strip() for c in re.split(r"\n\n+", raw) if c.strip()]
        for chunk in chunks:
            pairs.append((chunk.splitlines()[0].strip(), ""))

    return pairs


def main():
    st.markdown("""
    <div style="margin-bottom:24px;">
        <h1 style="margin-bottom:4px;">Interview Prep</h1>
        <p style="color:#6B7280;font-size:0.93rem;margin:0;">
            Role-specific questions with guidance on what strong answers look like.
        </p>
    </div>
    """, unsafe_allow_html=True)

    ollama_ok, ollama_msg = check_ollama()
    ollama_pill(ollama_ok, ollama_msg)

    st.markdown("<br>", unsafe_allow_html=True)
    fancy_divider()

    # ── Input ──────────────────────────────────────────────────────────────────
    c1, c2 = st.columns(2)
    with c1:
        position = st.text_input("Position Title",
                                  placeholder="e.g. Senior Software Engineer, Product Manager")
    with c2:
        company  = st.text_input("Company (optional)",
                                  placeholder="e.g. Google, early-stage startup")

    job_description = st.text_area(
        "Job Description (optional — strongly recommended)",
        height=140,
        placeholder="Paste the JD here for highly targeted questions…",
    )

    num_questions = st.slider("Number of questions", 4, 12, 8)

    fancy_divider()

    generate_clicked = st.button("Generate Questions", use_container_width=True)

    if generate_clicked:
        if not position.strip():
            st.warning("Enter a position title first.")
            return

        full_context = f"{position} at {company}" if company.strip() else position

        with st.spinner(f"Generating {num_questions} interview questions…"):
            if ollama_ok:
                raw, success = generate_interview_questions(full_context, job_description)
                if not success:
                    st.warning(f"AI unavailable ({raw}). Using built-in question bank.")
                    analyzer = ResumeAnalyzer()
                    questions_list, _ = analyzer.generate_interview_questions(position, n=num_questions)
                    pairs = [(q, "") for q in questions_list]
                else:
                    pairs = _parse_questions(raw)
                    # Cap to requested number
                    pairs = pairs[:num_questions]
            else:
                analyzer = ResumeAnalyzer()
                questions_list, _ = analyzer.generate_interview_questions(position, n=num_questions)
                pairs = [(q, "") for q in questions_list]

        if not pairs:
            st.error("Could not generate questions. Please try again.")
            return

        st.markdown(f"### Questions for **{position}**"
                    + (f" at *{company}*" if company.strip() else ""))

        for i, (q_text, tip) in enumerate(pairs, 1):
            st.markdown(question_card(i, q_text, tip), unsafe_allow_html=True)

        # Download
        download_text = "\n\n".join(
            f"Q{i}. {q}" + (f"\n   → {t}" if t else "")
            for i, (q, t) in enumerate(pairs, 1)
        )
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            "Download Questions",
            data=download_text,
            file_name=f"interview_questions_{position.replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    # ── Notes & reminders (from Application Tracker interviews) ───────────────
    fancy_divider()
    with st.expander("My Upcoming Interviews"):
        user_id      = st.session_state.get("user", "demo_user")
        applications = db.get_applications(user_id, status="Interview")
        if not applications:
            st.info("No applications currently at Interview stage. "
                    "Update an application's status in the Tracker to see it here.")
        else:
            for app in applications:
                pos     = app.get("position", "Unknown Role")
                comp    = app.get("company",  "Unknown Company")
                st.markdown(f"**{pos}** at {comp}")

    with st.expander("Interview Tips"):
        st.markdown("""
        **Before:**
        - Research the company's recent news, product, culture, and competitors
        - Review the JD line by line — be ready to address every requirement
        - Prepare 3–5 thoughtful questions to ask (not "what's the culture like")

        **During:**
        - Use STAR (Situation → Task → Action → Result) for behavioural questions
        - If you don't know, say so clearly and explain how you'd find out
        - Speak to specifics — generic answers don't stand out

        **After:**
        - Send a follow-up thank-you email within 24 hours
        - Reference a specific topic from the conversation
        - Follow up politely if you haven't heard back in 5–7 business days
        """)


if __name__ == "__main__":
    main()
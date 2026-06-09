import streamlit as st
from datetime import datetime
from utils.style import fancy_divider, ollama_pill
from utils.ollama_client import check_ollama, generate_cover_letter, stream_cover_letter


# ── Fallback template generator (used when Ollama is offline) ─────────────────
import re
from typing import List, Optional


def _extract_skills(text: str) -> List[str]:
    patterns = [
        "Python","Java","JavaScript","TypeScript","SQL","AWS","Azure","GCP",
        "Docker","Kubernetes","React","Angular","Vue.js","Node.js","Django",
        "Flask","Machine Learning","Data Analysis","Project Management",
        "Agile","Scrum","Leadership","Communication",
    ]
    found = [s for s in patterns if re.search(r"\b" + re.escape(s) + r"\b", text, re.I)]
    return list(dict.fromkeys(found))[:6]


def _extract_experience(text: str) -> Optional[str]:
    m = re.search(r"(\d+)\+?\s*years?\s*(?:of\s*)?experience", text, re.I)
    return m.group(0) if m else None


def _template_letter(job_desc: str, resume_text: str,
                     company: str, position: str, tone: str) -> str:
    skills = _extract_skills(resume_text)
    exp    = _extract_experience(resume_text)
    today  = datetime.now().strftime("%B %d, %Y")

    openers = {
        "Professional": f"I am writing to apply for the {position or 'open position'} role at {company or 'your organisation'}.",
        "Direct":       f"I am applying for the {position or 'open position'} position at {company or 'your organisation'}.",
        "Thoughtful":   f"After researching {company or 'your organisation'} and the {position or 'open position'} role, I am compelled to apply.",
    }
    closers = {
        "Professional": f"I look forward to the opportunity to discuss how my background can contribute to {company or 'your team'}.",
        "Direct":       "I am available for an interview at short notice and welcome the chance to discuss further.",
        "Thoughtful":   f"I would appreciate the chance to explore how my experience aligns with {company or 'your'} goals.",
    }

    skill_str = ", ".join(skills) if skills else "relevant technical and soft skills"
    exp_str   = f"With {exp}, I" if exp else "I"

    lines = [
        today, "",
        "Dear Hiring Manager,", "",
        f"{openers.get(tone, openers['Professional'])} {exp_str} bring hands-on experience in {skill_str}.",
        "",
        f"Throughout my career I have consistently delivered results by applying {skills[0] if skills else 'core competencies'} "
        f"to real-world challenges. I take a pragmatic, outcomes-first approach and am committed to continuous improvement.",
        "",
        f"{closers.get(tone, closers['Professional'])}",
        "",
        "Thank you for your time and consideration.",
        "",
        "Sincerely,",
        "",
        "[Your Full Name]",
        "[Your Email Address]",
        "[Your Phone Number]",
        "[LinkedIn Profile URL]",
    ]
    return "\n".join(lines)


# ── Streamlit view ────────────────────────────────────────────────────────────
def main():
    st.markdown("""
    <div style="margin-bottom:24px;">
        <h1 style="margin-bottom:4px;">Cover Letter Generator</h1>
        <p style="color:#6B7280;font-size:0.93rem;margin:0;">
            A tailored cover letter in seconds — AI-generated when Ollama is running,
            template-based otherwise.
        </p>
    </div>
    """, unsafe_allow_html=True)

    ollama_ok, ollama_msg = check_ollama()
    ollama_pill(ollama_ok, ollama_msg)
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("#### Job Details")
        company  = st.text_input("Company Name",    placeholder="e.g. Acme Corp")
        position = st.text_input("Position Title",  placeholder="e.g. Senior Software Engineer")
        job_desc = st.text_area("Job Description",  height=180,
                                 placeholder="Paste the full job posting here…")

    with col2:
        st.markdown("#### Your Profile")
        resume_text = st.text_area("Experience & Skills Summary", height=180,
                                    placeholder="Paste your resume text or a concise summary of your experience…")
        tone = st.selectbox("Tone", ["Professional", "Direct", "Thoughtful"],
                             help="Match the company culture you're applying to")

    fancy_divider()

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        generate_clicked = st.button("Generate Cover Letter", use_container_width=True)

    if generate_clicked:
        if not resume_text.strip():
            st.warning("Please provide your experience summary.")
            return

        with st.spinner("Writing your cover letter…"):
            if ollama_ok:
                letter, success = generate_cover_letter(
                    resume_text, job_desc or "", company, position, tone
                )
                if not success:
                    st.warning(f"AI generation failed ({letter}). Falling back to template.")
                    letter = _template_letter(job_desc or "", resume_text, company, position, tone)
            else:
                letter = _template_letter(job_desc or "", resume_text, company, position, tone)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Your Cover Letter")
        st.markdown(f'<div class="letter-preview">{letter}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("Edit before downloading"):
            letter = st.text_area("Make your changes:", value=letter,
                                   height=380, label_visibility="collapsed")

        st.download_button(
            label="Download as .txt",
            data=letter,
            file_name=f"Cover_Letter_{company or 'Application'}_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True,
        )

        with st.expander("Before you send"):
            st.markdown("""
            - Replace all `[bracketed]` placeholders with your real details
            - Add a specific metric or achievement to the middle paragraph
            - Proofread once more — grammar errors kill applications
            - Save or print as PDF for professional formatting
            """)


if __name__ == "__main__":
    main()

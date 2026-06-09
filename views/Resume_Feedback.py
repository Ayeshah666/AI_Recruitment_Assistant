import streamlit as st
import io
from datetime import datetime
from PyPDF2 import PdfReader
from docx import Document
from utils.style import fancy_divider, ollama_pill
from utils.database import db
from utils.ollama_client import check_ollama, analyze_resume as ollama_analyze
from utils.nlp_utils import ResumeAnalyzer


def _extract_text(file_bytes: bytes, filename: str) -> tuple[str, bool]:
    try:
        fn = filename.lower()
        if fn.endswith(".pdf"):
            reader = PdfReader(io.BytesIO(file_bytes))
            text   = "\n".join(p.extract_text() for p in reader.pages if p.extract_text())
        elif fn.endswith(".docx"):
            doc  = Document(io.BytesIO(file_bytes))
            text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        else:
            return "Unsupported file type. Upload a PDF or DOCX.", False
        return text.strip(), bool(text.strip())
    except Exception as e:
        return f"Could not read file: {e}", False


def main():
    st.markdown("""
    <div style="margin-bottom:24px;">
        <h1 style="margin-bottom:4px;">Resume Feedback</h1>
        <p style="color:#6B7280;font-size:0.93rem;margin:0;">
            Upload your resume and a job description — get a detailed match analysis
            and concrete suggestions to improve your chances.
        </p>
    </div>
    """, unsafe_allow_html=True)

    ollama_ok, ollama_msg = check_ollama()
    ollama_pill(ollama_ok, ollama_msg)
    if ollama_ok:
        st.caption("AI-powered analysis available. Local keyword analysis is always on as a baseline.")
    else:
        st.caption("Ollama offline — using local keyword + similarity analysis. Start Ollama for AI feedback.")

    st.markdown("<br>", unsafe_allow_html=True)
    fancy_divider()

    # ── Progress tracker ───────────────────────────────────────────────────────
    has_resume = bool(st.session_state.get("resume_text"))
    has_jd     = bool(st.session_state.get("job_description"))

    step_style = lambda done, active: "done" if done else ("active" if active else ""
    )
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(
            f'<div class="prog-step {"done" if has_jd else "active"}">'
            f'{"✅" if has_jd else "1."} Add Job Description</div>',
            unsafe_allow_html=True,
        )
    with s2:
        st.markdown(
            f'<div class="prog-step {"done" if has_resume else ("active" if has_jd else "")}">'
            f'{"✅" if has_resume else "2."} Upload Resume</div>',
            unsafe_allow_html=True,
        )
    with s3:
        st.markdown(
            '<div class="prog-step">3. Review Feedback</div>',
            unsafe_allow_html=True,
        )

    fancy_divider()

    col1, col2 = st.columns([2, 3], gap="large")

    # ── Left: inputs ───────────────────────────────────────────────────────────
    with col1:
        st.markdown("#### Job Description")
        jd_text = st.text_area(
            "Paste the full job posting",
            height=180,
            placeholder="Include requirements, responsibilities, and qualifications.",
            label_visibility="collapsed",
        )
        if st.button("Add Job Description", use_container_width=True):
            if jd_text.strip():
                st.session_state["job_description"] = jd_text
                if "analyzer" not in st.session_state:
                    st.session_state["analyzer"] = ResumeAnalyzer()
                st.session_state["analyzer"].add_job_description(jd_text)
                count = len(st.session_state["analyzer"].jd_texts)
                st.success(f"Added! ({count} JD{'s' if count > 1 else ''} loaded)")
            else:
                st.warning("Paste a job description first.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Resume")
        resume_file = st.file_uploader(
            "Upload PDF or DOCX",
            type=["pdf", "docx"],
            label_visibility="collapsed",
        )
        if resume_file:
            text, ok = _extract_text(resume_file.getvalue(), resume_file.name)
            if ok:
                st.session_state["resume_text"] = text
                st.success(f"Loaded — {len(text.split())} words extracted.")
            else:
                st.error(text)

    # ── Right: results ─────────────────────────────────────────────────────────
    with col2:
        if has_resume and has_jd:
            if st.button("Analyse Resume", use_container_width=True):
                resume_text = st.session_state["resume_text"]
                jd          = st.session_state["job_description"]
                user_id     = st.session_state.get("user", "demo_user")

                # Always run local NLP first — fast and always available
                if "analyzer" not in st.session_state:
                    st.session_state["analyzer"] = ResumeAnalyzer()
                    st.session_state["analyzer"].add_job_description(jd)

                local_feedback, local_ok = st.session_state["analyzer"].analyze_resume(resume_text)

                # Try AI on top if available
                if ollama_ok:
                    with st.spinner("Running AI analysis…"):
                        ai_feedback, ai_ok = ollama_analyze(resume_text, jd)
                    if ai_ok:
                        st.markdown("#### AI Analysis")
                        st.markdown(ai_feedback)
                        fancy_divider()
                        with st.expander("Local keyword analysis (always on)"):
                            st.markdown(local_feedback)
                        result_for_download = f"# AI Analysis\n\n{ai_feedback}\n\n---\n\n# Keyword Analysis\n\n{local_feedback}"
                    else:
                        st.warning(f"AI analysis failed: {ai_feedback}")
                        st.markdown(local_feedback)
                        result_for_download = local_feedback
                else:
                    st.markdown("#### Analysis")
                    st.markdown(local_feedback)
                    result_for_download = local_feedback

                # Save to DB
                try:
                    db.save_analysis(user_id, {
                        "resume_name": st.session_state.get("resume_filename", "resume"),
                        "feedback": result_for_download,
                        "timestamp": datetime.now(),
                    })
                except Exception:
                    pass

                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button(
                    "Download Report",
                    data=result_for_download,
                    file_name=f"resume_feedback_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

        elif has_resume and not has_jd:
            st.markdown("""
            <div class="glass-card" style="text-align:center; padding:40px 20px;">
                <div style="font-size:2.5rem; margin-bottom:12px;">📋</div>
                <div style="font-weight:600; color:#111827; margin-bottom:6px;">Add a Job Description</div>
                <div style="color:#6B7280; font-size:0.87rem;">
                    Paste the job posting on the left to start the analysis.
                </div>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.markdown("""
            <div class="glass-card" style="text-align:center; padding:60px 20px;">
                <div style="font-size:3rem; margin-bottom:14px;">📝</div>
                <div style="font-weight:700; font-size:1.1rem; color:#111827; margin-bottom:8px;">
                    Ready to analyse
                </div>
                <div style="color:#6B7280; font-size:0.87rem; max-width:300px; margin:0 auto; line-height:1.6;">
                    Add a job description and upload your resume to get a keyword
                    match score, gap analysis, and actionable recommendations.
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Tips ───────────────────────────────────────────────────────────────────
    fancy_divider()
    with st.expander("Tips for best results"):
        st.markdown("""
        **Resume:**
        - Upload a text-based PDF or DOCX (not a scanned image)
        - Make sure text is selectable — if you can't copy-paste it, the parser can't read it either

        **Job Description:**
        - Paste the complete posting — the more detail, the better the keyword match
        - Add multiple JDs to compare your fit across similar roles

        **What the analysis checks:**
        - TF-IDF keyword similarity between your resume and the JD
        - Missing keywords you should add where truthful
        - Resume health: quantified achievements, action verbs, length, links
        - Skill taxonomy across 6 categories: Languages, Frameworks, Data/ML, Cloud, DBs, Soft Skills
        """)


if __name__ == "__main__":
    main()        
from typing import List, Dict, Tuple
import re
import io
from PyPDF2 import PdfReader
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ── Comprehensive skill taxonomy ──────────────────────────────────────────────
SKILL_TAXONOMY: Dict[str, List[str]] = {
    "Languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
        "swift", "kotlin", "ruby", "php", "scala", "r", "matlab", "bash", "shell",
    ],
    "Web & Frameworks": [
        "react", "angular", "vue", "node.js", "django", "flask", "fastapi", "spring",
        "express", "next.js", "nuxt", "svelte", "graphql", "rest api", "microservices",
    ],
    "Data & ML": [
        "machine learning", "deep learning", "nlp", "tensorflow", "pytorch",
        "scikit-learn", "pandas", "numpy", "spark", "hadoop", "tableau", "power bi",
        "data analysis", "statistical analysis", "a/b testing", "sql", "nosql",
    ],
    "Cloud & DevOps": [
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins",
        "ci/cd", "linux", "git", "github actions", "ansible", "helm",
    ],
    "Databases": [
        "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "sqlite",
        "oracle", "dynamodb", "cassandra", "snowflake",
    ],
    "Soft Skills": [
        "leadership", "communication", "teamwork", "agile", "scrum", "project management",
        "problem solving", "mentoring", "stakeholder management",
    ],
}

# Flat list for quick lookup
ALL_SKILLS = [s for group in SKILL_TAXONOMY.values() for s in group]


class ResumeAnalyzer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        self.jd_texts: List[str] = []
        self._keywords: List[str] = []

    # ── Text extraction ───────────────────────────────────────────────────────

    def extract_text(self, file_bytes: bytes, filename: str) -> Tuple[str, bool]:
        """Extract text from PDF or DOCX. Returns (text, success)."""
        try:
            filename = filename.lower()
            text = ""

            if filename.endswith(".pdf"):
                reader = PdfReader(io.BytesIO(file_bytes))
                text = "\n".join(
                    page.extract_text() for page in reader.pages if page.extract_text()
                )

            elif filename.endswith(".docx"):
                doc = Document(io.BytesIO(file_bytes))
                text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())

            text = self.clean_text(text)
            return (text, bool(text.strip()))

        except Exception as e:
            print(f"Extraction failed: {e}")
            return ("", False)

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = re.sub(r"[^\w\s\-•·●.,;:!?()/]", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    # ── JD management ─────────────────────────────────────────────────────────

    def add_job_description(self, jd_text: str) -> bool:
        if not jd_text or not isinstance(jd_text, str):
            return False
        cleaned = self.clean_text(jd_text)
        if cleaned:
            self.jd_texts.append(cleaned)
            self._extract_keywords()
            return True
        return False

    def _extract_keywords(self, n: int = 20) -> List[str]:
        if not self.jd_texts:
            return []
        try:
            tfidf = TfidfVectorizer(stop_words="english", max_features=1000)
            matrix = tfidf.fit_transform(self.jd_texts)
            feature_names = tfidf.get_feature_names_out()
            scores = zip(feature_names, matrix.sum(axis=0).tolist()[0])
            sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
            self._keywords = [w for w, _ in sorted_scores[:n]]
            return self._keywords
        except Exception as e:
            print(f"Keyword extraction failed: {e}")
            return []

    # ── Resume analysis ───────────────────────────────────────────────────────

    def analyze_resume(self, resume_text: str) -> Tuple[str, bool]:
        """Full local resume analysis — no paid API required."""
        if not self.jd_texts:
            return ("Please add at least one job description first.", False)
        if not resume_text:
            return ("Invalid resume content.", False)

        cleaned = self.clean_text(resume_text)
        if not cleaned:
            return ("Could not process resume content.", False)

        try:
            # 1. TF-IDF similarity
            all_texts = self.jd_texts + [cleaned]
            matrix = self.vectorizer.fit_transform(all_texts)
            resume_vec = matrix[-1]
            jd_vecs = matrix[:-1]
            similarities = cosine_similarity(resume_vec, jd_vecs)[0]
            avg_score = float(similarities.mean()) if len(similarities) else 0.0

            # 2. Keyword gap
            resume_words = set(re.findall(r"\b\w+\b", cleaned.lower()))
            missing_kw = [kw for kw in self._keywords if kw.lower() not in resume_words]
            present_kw = [kw for kw in self._keywords if kw.lower() in resume_words]

            # 3. Skill detection
            detected_skills: Dict[str, List[str]] = {}
            for category, skills in SKILL_TAXONOMY.items():
                found = [s for s in skills if re.search(r"\b" + re.escape(s) + r"\b", cleaned, re.I)]
                if found:
                    detected_skills[category] = found

            # 4. Resume health checks
            health: List[Tuple[bool, str]] = [
                (bool(re.search(r"\d+\s*[%+x]|\$[\d,]+|\d+\s*(users|clients|projects|team)", cleaned, re.I)),
                 "Quantified achievements (numbers, percentages, metrics)"),
                (bool(re.search(r"\b(led|managed|built|developed|designed|delivered|launched|reduced|increased|improved)\b", cleaned, re.I)),
                 "Strong action verbs"),
                (bool(re.search(r"(experience|work history|employment)", cleaned, re.I)),
                 "Work Experience section"),
                (bool(re.search(r"(education|university|bachelor|master|degree|diploma)", cleaned, re.I)),
                 "Education section"),
                (bool(re.search(r"(skills|technologies|tools|competencies)", cleaned, re.I)),
                 "Skills section"),
                (bool(re.search(r"(linkedin|github|portfolio|github\.com|linkedin\.com)", cleaned, re.I)),
                 "LinkedIn / GitHub / Portfolio link"),
                (500 <= len(cleaned.split()) <= 1200,
                 f"Ideal length ({len(cleaned.split())} words — target 500–1 200)"),
            ]

            # ── Build feedback report ─────────────────────────────────────────
            lines = ["## Resume Analysis Report", ""]

            # Score gauge
            score_pct = int(avg_score * 100)
            bar_filled = int(avg_score * 25)
            bar = "█" * bar_filled + "░" * (25 - bar_filled)
            grade = (
                "Excellent" if score_pct >= 70
                else "Good" if score_pct >= 50
                else "Needs Work" if score_pct >= 30
                else "Low Match"
            )
            lines += [
                f"### Overall Match Score — {score_pct}% ({grade})",
                f"`{bar}`",
                "",
            ]

            if len(similarities) > 1:
                lines.append("### Per-JD Match Scores")
                for i, s in enumerate(sorted(similarities, reverse=True)[:5], 1):
                    b = "█" * int(s * 20) + "░" * (20 - int(s * 20))
                    lines.append(f"- **JD {i}**: `{b}` {s:.0%}")
                lines.append("")

            # Health checks
            lines.append("### Resume Health Check")
            for passed, label in health:
                icon = "✅" if passed else "❌"
                lines.append(f"- {icon} {label}")
            lines.append("")

            # Detected skills
            if detected_skills:
                lines.append("### Skills Detected in Your Resume")
                for cat, skills in detected_skills.items():
                    lines.append(f"**{cat}:** " + " · ".join(f"`{s}`" for s in skills))
                lines.append("")

            # Keyword gaps
            if missing_kw:
                lines.append("### Missing Keywords from Job Description")
                lines.append(
                    "Add these to your resume where truthful and relevant:"
                )
                lines.append("  \n".join(f"- `{kw}`" for kw in missing_kw[:12]))
                lines.append("")

            if present_kw:
                lines.append("### Keywords Already Present — Good")
                lines.append(", ".join(f"`{kw}`" for kw in present_kw[:12]))
                lines.append("")

            # Actionable recommendations
            lines.append("### Recommendations")
            recs = []
            if not health[0][0]:
                recs.append("**Quantify your impact** — add numbers, percentages, or dollar figures to at least 3 bullet points.")
            if not health[1][0]:
                recs.append("**Use action verbs** — start bullets with Led, Built, Designed, Reduced, Improved, etc.")
            if not health[5][0]:
                recs.append("**Add online presence** — include a GitHub or LinkedIn URL.")
            if len(cleaned.split()) < 500:
                recs.append("**Expand your resume** — it looks too sparse. Add more detail to your experience bullets.")
            if len(cleaned.split()) > 1200:
                recs.append("**Trim your resume** — aim for 1–2 pages. Cut older or less relevant roles.")
            if missing_kw:
                recs.append(f"**Close the keyword gap** — naturally weave in: {', '.join(missing_kw[:5])}.")
            if avg_score < 0.3:
                recs.append("**Tailor this resume** — your match score is low. Mirror the language from the job posting more closely.")

            # Always-good advice
            recs += [
                "**Summary / Objective** — a 2–3 line professional summary at the top quickly tells recruiters why you're the right fit.",
                "**ATS-friendly formatting** — avoid tables, columns, and graphics; plain text parses best.",
                "**Proofread** — run a spell-check and ask someone to read it for clarity.",
            ]

            for i, rec in enumerate(recs, 1):
                lines.append(f"{i}. {rec}")

            return ("\n".join(lines), True)

        except Exception as e:
            print(f"Analysis error: {e}")
            return ("Could not complete analysis — please try again.", False)

    # ── Interview questions ───────────────────────────────────────────────────

    def generate_interview_questions(self, position: str, n: int = 5) -> Tuple[List[str], bool]:
        position = position.lower().strip()
        if not position:
            return ([], False)

        question_bank = {
            "data scientist": [
                "Walk me through how you would handle a large dataset with significant missing values.",
                "Explain the bias–variance tradeoff in plain English.",
                "How do you decide which ML model to use for a given problem?",
                "Describe how you would validate a model in production.",
                "What metrics would you use to evaluate a classifier on an imbalanced dataset?",
                "Tell me about a time your analysis changed a business decision.",
                "How do you communicate uncertainty in your results to non-technical stakeholders?",
                "What's your approach to feature engineering?",
            ],
            "software engineer": [
                "How do you approach code reviews — both giving and receiving feedback?",
                "Walk me through how you'd design a URL shortener at scale.",
                "How do you deal with technical debt in a fast-moving codebase?",
                "Explain a time you had to debug a difficult production issue.",
                "What does good API design look like to you?",
                "How do you decide when to refactor vs rewrite?",
                "Describe your testing strategy for a new feature.",
                "How do you stay current with new tools and practices?",
            ],
            "product manager": [
                "How do you prioritise a backlog when everything feels urgent?",
                "Tell me about a feature you killed — why and how?",
                "How do you measure product-market fit?",
                "Describe a time you had to say no to a stakeholder.",
                "How do you balance user needs with business objectives?",
                "Walk me through how you'd launch a new feature with limited engineering resources.",
                "How do you use data to inform product decisions?",
            ],
            "business analyst": [
                "How do you gather requirements from stakeholders who aren't sure what they want?",
                "Describe your process for turning a business problem into a data question.",
                "How do you handle conflicting requirements from different stakeholders?",
                "Walk me through how you'd measure the success of a new internal process.",
                "Tell me about a time your analysis revealed an unexpected insight.",
                "How do you prioritise which requirements to tackle first?",
            ],
            "marketing": [
                "How do you measure the ROI of a content marketing campaign?",
                "Tell me about a campaign that didn't perform as expected — what did you learn?",
                "How do you segment an audience for a new product launch?",
                "Describe your approach to A/B testing a landing page.",
                "How do you balance brand consistency with localisation?",
                "Walk me through your process for creating a go-to-market strategy.",
            ],
            "designer": [
                "Walk me through your design process from discovery to delivery.",
                "How do you handle pushback on a design decision from an engineer or PM?",
                "Describe a time user research changed your initial design direction.",
                "How do you balance business goals with user needs?",
                "What does a good design system look like to you?",
                "How do you design for accessibility?",
            ],
            "project manager": [
                "How do you manage scope creep on a project?",
                "Walk me through how you communicate a project delay to a senior stakeholder.",
                "How do you keep a distributed team aligned?",
                "Describe a project recovery you led.",
                "How do you decide which risks to escalate vs manage yourself?",
                "What does a healthy project retrospective look like?",
            ],
        }

        # Match to the closest category
        matched = None
        for key in question_bank:
            if key in position or any(word in position for word in key.split()):
                matched = key
                break

        questions = question_bank.get(
            matched,
            [
                "Tell me about yourself and what drew you to this role.",
                "Why are you leaving (or considering leaving) your current position?",
                "Describe a challenging project and how you handled it.",
                "How do you handle tight deadlines and competing priorities?",
                "Tell me about a time you disagreed with a teammate — how did you resolve it?",
                "What does success look like in the first 90 days for you?",
                "What's your biggest professional achievement in the last two years?",
                "Do you have any questions for us?",
            ],
        )

        return (questions[:n], True)

    def get_suggested_skills(self) -> List[str]:
        if not self._keywords:
            self._extract_keywords()
        return self._keywords or []
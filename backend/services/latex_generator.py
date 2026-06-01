"""
LaTeX Generator + PDF Compiler
Takes structured resume dict → LaTeX code → PDF file
Uses Jake's Resume template style (popular CS resume format)
"""
import os
import subprocess
import tempfile


def generate_latex(resume: dict) -> str:
    """
    Generate LaTeX code from structured resume dict.
    Uses a clean, ATS-friendly professional template.
    """
    name = resume.get("name", "Your Name")
    email = resume.get("email", "")
    phone = resume.get("phone", "")
    location = resume.get("location", "")
    linkedin = resume.get("linkedin", "")
    github = resume.get("github", "")
    portfolio = resume.get("portfolio", "")
    summary = resume.get("summary", "")

    skills = resume.get("skills", {})
    tech_skills = skills.get("technical", [])
    tools = skills.get("tools", [])
    soft_skills = skills.get("soft", [])
    languages = skills.get("languages", [])

    experience = resume.get("experience", [])
    education = resume.get("education", [])
    projects = resume.get("projects", [])
    certifications = resume.get("certifications", [])
    achievements = resume.get("achievements", [])

    # Build contact line
    contact_parts = []
    if phone:
        contact_parts.append(_escape(phone))
    if email:
        contact_parts.append(f"\\href{{mailto:{_escape(email)}}}{{{_escape(email)}}}")
    if linkedin:
        contact_parts.append(f"\\href{{{_escape(linkedin)}}}{{LinkedIn}}")
    if github:
        contact_parts.append(f"\\href{{{_escape(github)}}}{{GitHub}}")
    if portfolio:
        contact_parts.append(f"\\href{{{_escape(portfolio)}}}{{Portfolio}}")
    if location:
        contact_parts.append(_escape(location))

    contact_line = " $|$ ".join(contact_parts)

    # Build skills section
    skills_lines = []
    if tech_skills:
        skills_lines.append(f"\\textbf{{Technical Skills:}} {_escape(', '.join(tech_skills))}")
    if tools:
        skills_lines.append(f"\\textbf{{Tools \\& Platforms:}} {_escape(', '.join(tools))}")
    if soft_skills:
        skills_lines.append(f"\\textbf{{Soft Skills:}} {_escape(', '.join(soft_skills))}")
    if languages:
        skills_lines.append(f"\\textbf{{Languages:}} {_escape(', '.join(languages))}")

    # Build experience section
    exp_latex = ""
    for exp in experience:
        title = _escape(exp.get("title", ""))
        company = _escape(exp.get("company", ""))
        loc = _escape(exp.get("location", ""))
        start = _escape(exp.get("start_date", ""))
        end = _escape(exp.get("end_date", "Present"))
        bullets = exp.get("bullets", [])

        bullet_items = "\n".join(
            f"      \\item {_escape(b)}" for b in bullets if b
        )

        exp_latex += f"""
  \\resumeSubheading
    {{{title}}}{{{start} -- {end}}}
    {{{company}}}{{{loc}}}
    \\resumeItemListStart
{bullet_items}
    \\resumeItemListEnd
"""

    # Build education section
    edu_latex = ""
    for edu in education:
        degree = _escape(edu.get("degree", ""))
        institution = _escape(edu.get("institution", ""))
        loc = _escape(edu.get("location", ""))
        year = _escape(edu.get("graduation_year", ""))
        gpa = edu.get("gpa", "")
        courses = edu.get("relevant_courses", [])

        gpa_str = f" \\textbf{{GPA: {_escape(gpa)}}}" if gpa else ""
        courses_str = ""
        if courses:
            courses_str = f"\n    \\resumeItem{{Relevant Courses: {_escape(', '.join(courses[:6]))}}}"

        edu_latex += f"""
  \\resumeSubheading
    {{{degree}}}{{{year}}}
    {{{institution}}}{{{loc}}}{gpa_str}
    \\resumeItemListStart{courses_str}
    \\resumeItemListEnd
"""

    # Build projects section
    proj_latex = ""
    for proj in projects:
        pname = _escape(proj.get("name", ""))
        tech = _escape(", ".join(proj.get("tech_stack", [])))
        link = proj.get("link", "")
        bullets = proj.get("bullets", [proj.get("description", "")])

        link_str = f"\\href{{{_escape(link)}}}{{\\underline{{Link}}}}" if link else ""
        bullet_items = "\n".join(
            f"      \\item {_escape(b)}" for b in bullets if b
        )

        proj_latex += f"""
  \\resumeProjectHeading
    {{\\textbf{{{pname}}} $|$ \\emph{{{tech}}}  {link_str}}}{{}}
    \\resumeItemListStart
{bullet_items}
    \\resumeItemListEnd
"""

    # Build certifications section
    cert_latex = ""
    if certifications:
        cert_items = "\n".join(
            f"  \\resumeItem{{\\textbf{{{_escape(c.get('name', ''))}}} -- {_escape(c.get('issuer', ''))} ({_escape(str(c.get('year', '')))})  }}"
            for c in certifications
        )
        cert_latex = f"""
\\section{{Certifications}}
  \\resumeItemListStart
{cert_items}
  \\resumeItemListEnd
"""

    # Build achievements section
    ach_latex = ""
    if achievements:
        ach_items = "\n".join(
            f"  \\resumeItem{{{_escape(a)}}}" for a in achievements
        )
        ach_latex = f"""
\\section{{Achievements}}
  \\resumeItemListStart
{ach_items}
  \\resumeItemListEnd
"""

    # Summary section
    summary_latex = ""
    if summary:
        summary_latex = f"""
\\section{{Professional Summary}}
\\small{{{_escape(summary)}}}
\\vspace{{4pt}}
"""

    # Full LaTeX document
    newline = "\n"
    separator = "     \\\\\\\\"
    skills_block = (newline + separator).join(skills_lines) if skills_lines else "Skills to be added"
    latex = f"""
%-------------------------
% ResumeForge Generated Resume
% Based on Jake's Resume Template
%-------------------------

\\documentclass[letterpaper,11pt]{{article}}

\\usepackage{{latexsym}}
\\usepackage[empty]{{fullpage}}
\\usepackage{{titlesec}}
\\usepackage{{marvosym}}
\\usepackage[usenames,dvipsnames]{{color}}
\\usepackage{{verbatim}}
\\usepackage{{enumitem}}
\\usepackage[hidelinks]{{hyperref}}
\\usepackage{{fancyhdr}}
\\usepackage[english]{{babel}}
\\usepackage{{tabularx}}
\\input{{glyphtounicode}}

\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyfoot{{}}
\\renewcommand{{\\headrulewidth}}{{0pt}}
\\renewcommand{{\\footrulewidth}}{{0pt}}

\\addtolength{{\\oddsidemargin}}{{-0.5in}}
\\addtolength{{\\evensidemargin}}{{-0.5in}}
\\addtolength{{\\textwidth}}{{1in}}
\\addtolength{{\\topmargin}}{{-.5in}}
\\addtolength{{\\textheight}}{{1.0in}}

\\urlstyle{{same}}
\\raggedbottom
\\raggedright
\\setlength{{\\tabcolsep}}{{0in}}

\\titleformat{{\\section}}{{
  \\vspace{{-4pt}}\\scshape\\raggedright\\large
}}{{}}{{0em}}{{}}[\\color{{black}}\\titlerule \\vspace{{-5pt}}]

\\pdfgentounicode=1

%--- Custom Commands ---%
\\newcommand{{\\resumeItem}}[1]{{
  \\item\\small{{
    {{#1 \\vspace{{-2pt}}}}
  }}
}}

\\newcommand{{\\resumeSubheading}}[4]{{
  \\vspace{{-2pt}}\\item
    \\begin{{tabular*}}{{0.97\\textwidth}}[t]{{l@{{\\extracolsep{{\\fill}}}}r}}
      \\textbf{{#1}} & #2 \\\\
      \\textit{{\\small#3}} & \\textit{{\\small #4}} \\\\
    \\end{{tabular*}}\\vspace{{-7pt}}
}}

\\newcommand{{\\resumeProjectHeading}}[2]{{
    \\item
    \\begin{{tabular*}}{{0.97\\textwidth}}{{l@{{\\extracolsep{{\\fill}}}}r}}
      \\small#1 & #2 \\\\
    \\end{{tabular*}}\\vspace{{-7pt}}
}}

\\newcommand{{\\resumeSubItem}}[1]{{\\resumeItem{{#1}}\\vspace{{-4pt}}}}
\\renewcommand\\labelitemii{{$\\vcenter{{\\hbox{{\\tiny$\\bullet$}}}}$}}
\\newcommand{{\\resumeSubHeadingListStart}}{{\\begin{{itemize}}[leftmargin=0.15in, label={{}}]}}
\\newcommand{{\\resumeSubHeadingListEnd}}{{\\end{{itemize}}}}
\\newcommand{{\\resumeItemListStart}}{{\\begin{{itemize}}}}
\\newcommand{{\\resumeItemListEnd}}{{\\end{{itemize}}\\vspace{{-5pt}}}}

%========== DOCUMENT START ==========%
\\begin{{document}}

%--- HEADER ---%
\\begin{{center}}
    \\textbf{{\\Huge \\scshape {_escape(name)}}} \\\\ \\vspace{{1pt}}
    \\small {contact_line}
\\end{{center}}

{summary_latex}

%--- SKILLS ---%
\\section{{Technical Skills}}
 \\begin{{itemize}}[leftmargin=0.15in, label={{}}]
    \\small{{\\item{{
     {skills_block}
    }}}}
 \\end{{itemize}}

%--- EXPERIENCE ---%
\\section{{Experience}}
  \\resumeSubHeadingListStart
{exp_latex}
  \\resumeSubHeadingListEnd

%--- EDUCATION ---%
\\section{{Education}}
  \\resumeSubHeadingListStart
{edu_latex}
  \\resumeSubHeadingListEnd

%--- PROJECTS ---%
\\section{{Projects}}
    \\resumeSubHeadingListStart
{proj_latex}
    \\resumeSubHeadingListEnd

{cert_latex}
{ach_latex}

\\end{{document}}
"""
    return latex


def compile_to_pdf(latex_code: str, session_id: str) -> str:
    """
    Compile LaTeX to PDF using pdflatex.
    Returns path to PDF file.
    Requires: pdflatex installed on system (texlive)
    """
    output_dir = f"/tmp/resumes/{session_id}"
    os.makedirs(output_dir, exist_ok=True)

    tex_path = os.path.join(output_dir, "resume.tex")
    pdf_path = os.path.join(output_dir, "resume.pdf")

    # Write LaTeX file
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex_code)

    # Check if pdflatex is available
    result = subprocess.run(["which", "pdflatex"], capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(
            "pdflatex not found. Install with: sudo apt-get install texlive-latex-base texlive-fonts-recommended"
        )

    # Compile twice for proper rendering
    for _ in range(2):
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-output-directory", output_dir, tex_path],
            capture_output=True,
            text=True,
            timeout=30
        )

    if not os.path.exists(pdf_path):
        raise RuntimeError(f"PDF compilation failed.\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}")

    return pdf_path


def _escape(text: str) -> str:
    """Escape special LaTeX characters"""
    if not text:
        return ""
    text = str(text)
    replacements = [
        ("\\", "\\textbackslash{}"),
        ("&", "\\&"),
        ("%", "\\%"),
        ("$", "\\$"),
        ("#", "\\#"),
        ("_", "\\_"),
        ("{", "\\{"),
        ("}", "\\}"),
        ("~", "\\textasciitilde{}"),
        ("^", "\\textasciicircum{}"),
    ]
    for char, escaped in replacements:
        text = text.replace(char, escaped)
    return text

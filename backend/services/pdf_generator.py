"""
pdf_generator.py  –  ResumeForge
Generates a professional PDF resume matching the clean typographic style:
ruled section dividers, bold name header, two-column skills table, bullet
experience entries, right-aligned dates.

Accepts resume_data as:
  • dict  – structured resume (best output)
  • str   – plain/markdown text (heuristic parser)
"""

import os, re
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

# ── Palette ───────────────────────────────────────────────────────────────────
BLACK      = colors.HexColor('#0d0d0d')
DARK_GREY  = colors.HexColor('#333333')
MID_GREY   = colors.HexColor('#555555')
LIGHT_GREY = colors.HexColor('#888888')
RULE_COLOR = colors.HexColor('#222222')

def make_styles():
    return {
        'name': ParagraphStyle('Name', fontName='Helvetica-Bold', fontSize=20,
            leading=24, textColor=BLACK, alignment=TA_CENTER, spaceAfter=3),
        'contact': ParagraphStyle('Contact', fontName='Helvetica', fontSize=9,
            leading=13, textColor=DARK_GREY, alignment=TA_CENTER, spaceAfter=0),
        'section': ParagraphStyle('Section', fontName='Helvetica-Bold', fontSize=10.5,
            leading=14, textColor=BLACK, spaceBefore=10, spaceAfter=3),
        'entry_title': ParagraphStyle('EntryTitle', fontName='Helvetica-Bold', fontSize=9.5,
            leading=13, textColor=BLACK, spaceAfter=0),
        'entry_sub': ParagraphStyle('EntrySub', fontName='Helvetica-Oblique', fontSize=9,
            leading=12, textColor=MID_GREY, spaceAfter=1),
        'body': ParagraphStyle('Body', fontName='Helvetica', fontSize=9,
            leading=13, textColor=DARK_GREY, spaceAfter=3),
        'bullet': ParagraphStyle('Bullet', fontName='Helvetica', fontSize=9,
            leading=13, textColor=DARK_GREY, leftIndent=12, spaceAfter=2),
        'skill_label': ParagraphStyle('SkillLabel', fontName='Helvetica-Bold', fontSize=9,
            leading=13, textColor=BLACK),
        'skill_value': ParagraphStyle('SkillValue', fontName='Helvetica', fontSize=9,
            leading=13, textColor=DARK_GREY),
        'date': ParagraphStyle('Date', fontName='Helvetica', fontSize=9,
            leading=13, textColor=LIGHT_GREY, alignment=TA_RIGHT),
    }

def section_header(title, styles):
    return [
        HRFlowable(width='100%', thickness=0.8, color=RULE_COLOR, spaceAfter=2, spaceBefore=8),
        Paragraph(title.upper(), styles['section']),
    ]

def bullet_para(text, styles):
    clean = re.sub(r'^[•·\-–\*\s]+', '', text).strip()
    return Paragraph(f"• \xa0{clean}", styles['bullet'])

def two_col_row(left_cells, right_text, styles, cw):
    t = Table([[left_cells, Paragraph(right_text or '', styles['date'])]], colWidths=cw)
    t.setStyle(TableStyle([
        ('VALIGN',       (0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',  (0,0),(-1,-1),0),
        ('RIGHTPADDING', (0,0),(-1,-1),0),
        ('TOPPADDING',   (0,0),(-1,-1),0),
        ('BOTTOMPADDING',(0,0),(-1,-1),2),
    ]))
    return t

# ── Dict builder ──────────────────────────────────────────────────────────────
def build_from_dict(data, styles, W):
    story = []
    cw = [W*0.72, W*0.28]

    # Header
    name = (data.get('name') or data.get('full_name') or 'Resume').upper()
    story.append(Paragraph(name, styles['name']))
    parts = []
    for k in ('location','email','phone'):
        v = data.get(k)
        if v: parts.append(str(v))
    if data.get('linkedin'): parts.append('LinkedIn')
    if data.get('github'):   parts.append('GitHub')
    if parts:
        story.append(Paragraph(' \u2014 '.join(parts), styles['contact']))
    story.append(Spacer(1,6))
    story.append(HRFlowable(width='100%', thickness=1.2, color=RULE_COLOR))

    # Objective/Summary
    for key in ('objective','summary','profile'):
        val = data.get(key)
        if val:
            story += section_header(key, styles)
            story.append(Paragraph(str(val), styles['body']))
            break

    # Education
    edus = data.get('education',[])
    if not isinstance(edus, list): edus = [edus]
    if edus:
        story += section_header('Education', styles)
        for edu in edus:
            if not isinstance(edu, dict): edu = {'institution': str(edu)}
            inst  = edu.get('institution','')
            loc_e = edu.get('location','')
            deg   = edu.get('degree','')
            start = str(edu.get('start_date') or edu.get('start') or '')
            end   = str(edu.get('graduation_year') or edu.get('end_date') or edu.get('end') or '')
            date_str = f"{start} \u2013 {end}" if start else end
            left_top = f"{inst}{', '+loc_e if loc_e else ''}"
            left_cells = [Paragraph(left_top, styles['entry_title']),
                          Paragraph(deg, styles['entry_sub'])]
            story.append(two_col_row(left_cells, date_str, styles, cw))
            courses = edu.get('relevant_courses') or edu.get('courses')
            if courses:
                if isinstance(courses, list): courses = ', '.join(courses)
                story.append(Paragraph(f"<i>Relevant Coursework:</i> {courses}", styles['body']))
            story.append(Spacer(1,4))

    # Experience
    exps = data.get('experience',[])
    if not isinstance(exps, list): exps = [exps]
    if exps:
        story += section_header('Experience', styles)
        for exp in exps:
            if not isinstance(exp, dict): exp = {'company': str(exp)}
            company = exp.get('company','')
            loc_e   = exp.get('location','')
            title   = exp.get('title','')
            start   = str(exp.get('start_date') or exp.get('start',''))
            end     = str(exp.get('end_date')   or exp.get('end',''))
            date_str = f"{start} \u2013 {end}" if start and end else (start or end)
            left_top = f"{company}{', '+loc_e if loc_e else ''}"
            left_cells = [Paragraph(left_top, styles['entry_title']),
                          Paragraph(title, styles['entry_sub'])]
            story.append(two_col_row(left_cells, date_str, styles, cw))
            bullets = exp.get('bullets') or exp.get('responsibilities',[])
            if isinstance(bullets, str):
                bullets = [b.strip() for b in bullets.split('\n') if b.strip()]
            for b in bullets:
                story.append(bullet_para(b, styles))
            story.append(Spacer(1,4))

    # Projects
    projs = data.get('projects',[])
    if not isinstance(projs, list): projs = [projs]
    if projs:
        story += section_header('Projects', styles)
        for proj in projs:
            if not isinstance(proj, dict): proj = {'name': str(proj)}
            pname = proj.get('name','')
            year  = str(proj.get('year') or proj.get('date') or '')
            tech  = proj.get('tech_stack') or proj.get('technologies') or []
            if isinstance(tech, list): tech = ' \xb7 '.join(tech)
            left_cells = [Paragraph(pname, styles['entry_title']),
                          Paragraph(tech or '', styles['entry_sub'])]
            story.append(two_col_row(left_cells, year, styles, cw))
            bullets = proj.get('bullets',[])
            if isinstance(bullets, str):
                bullets = [b.strip() for b in bullets.split('\n') if b.strip()]
            if not bullets and proj.get('description'):
                story.append(Paragraph(proj['description'], styles['body']))
            for b in bullets:
                story.append(bullet_para(b, styles))
            story.append(Spacer(1,4))

    # Technical Skills
    skills = data.get('skills') or data.get('technical_skills')
    if skills:
        story += section_header('Technical Skills', styles)
        rows = []
        if isinstance(skills, dict):
            for cat, vals in skills.items():
                if isinstance(vals, list): vals = ', '.join(str(v) for v in vals)
                rows.append([Paragraph(cat.replace('_',' ').title(), styles['skill_label']),
                             Paragraph(str(vals), styles['skill_value'])])
        elif isinstance(skills, list):
            for s in skills:
                if isinstance(s, dict):
                    for k,v in s.items():
                        if isinstance(v, list): v = ', '.join(v)
                        rows.append([Paragraph(str(k), styles['skill_label']),
                                     Paragraph(str(v), styles['skill_value'])])
                else:
                    rows.append([Paragraph('', styles['skill_label']),
                                 Paragraph(str(s), styles['skill_value'])])
        else:
            rows.append([Paragraph('', styles['skill_label']),
                         Paragraph(str(skills), styles['skill_value'])])
        if rows:
            st = Table(rows, colWidths=[W*0.28, W*0.72], hAlign='LEFT')
            st.setStyle(TableStyle([
                ('VALIGN',       (0,0),(-1,-1),'TOP'),
                ('LEFTPADDING',  (0,0),(-1,-1),0),
                ('RIGHTPADDING', (0,0),(-1,-1),4),
                ('TOPPADDING',   (0,0),(-1,-1),1),
                ('BOTTOMPADDING',(0,0),(-1,-1),3),
            ]))
            story.append(st)

    # Leadership / Volunteering
    leadership = data.get('leadership') or data.get('volunteering') or []
    if not isinstance(leadership, list): leadership = [leadership]
    if any(leadership):
        story += section_header('Leadership & Volunteering', styles)
        for item in leadership:
            if not isinstance(item, dict): item = {'role': str(item)}
            role = item.get('role') or item.get('title','')
            org  = item.get('organization') or item.get('company','')
            loc_l = item.get('location','')
            year  = str(item.get('year') or item.get('date',''))
            left_sub = f"{org}{', '+loc_l if loc_l else ''}" if org else ''
            left_cells = [Paragraph(role, styles['entry_title']),
                          Paragraph(left_sub, styles['entry_sub'])]
            story.append(two_col_row(left_cells, year, styles, cw))
            for b in (item.get('bullets') or []):
                story.append(bullet_para(b, styles))
            story.append(Spacer(1,4))

    # Certifications
    certs = data.get('certifications',[])
    if certs:
        story += section_header('Certifications', styles)
        for c in certs:
            if isinstance(c, dict):
                story.append(Paragraph(
                    f"<b>{c.get('name','')}</b>  <i>{c.get('issuer','')}</i>  {c.get('year','')}",
                    styles['body']))
            else:
                story.append(Paragraph(str(c), styles['body']))

    # Achievements
    achievements = data.get('achievements',[])
    if achievements:
        story += section_header('Achievements', styles)
        for a in achievements:
            story.append(bullet_para(str(a), styles))

    # Additional Information
    extras = []
    langs = data.get('languages')
    avail = data.get('availability')
    if langs:
        if isinstance(langs, list): langs = ', '.join(langs)
        extras.append(f"<b>Languages:</b> {langs}")
    if avail:
        extras.append(f"<b>Availability:</b> {avail}")
    if extras:
        story += section_header('Additional Information', styles)
        for line in extras:
            story.append(Paragraph(line, styles['body']))

    return story

# ── String heuristic builder ──────────────────────────────────────────────────
KNOWN_SECTIONS = {
    'OBJECTIVE','SUMMARY','PROFILE','EDUCATION','EXPERIENCE','PROJECTS',
    'SKILLS','TECHNICAL SKILLS','CERTIFICATIONS','ACHIEVEMENTS','LEADERSHIP',
    'VOLUNTEERING','ADDITIONAL','ADDITIONAL INFORMATION','LANGUAGES','AWARDS',
}

def build_from_str(text, styles, W):
    cw = [W*0.72, W*0.28]
    lines = text.strip().splitlines()
    story = []
    idx = 0
    first = True
    second_pending = False

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()

        if not stripped:
            story.append(Spacer(1,4))
            continue

        if first:
            story.append(Paragraph(stripped.upper(), styles['name']))
            story.append(Spacer(1,2))
            first = False
            second_pending = True
            continue

        if second_pending:
            story.append(Paragraph(stripped, styles['contact']))
            story.append(Spacer(1,6))
            story.append(HRFlowable(width='100%', thickness=1.2, color=RULE_COLOR))
            second_pending = False
            continue

        up = stripped.upper()
        if up in KNOWN_SECTIONS or (stripped.isupper() and 3 < len(stripped) < 45):
            story += section_header(stripped, styles)
            continue

        if stripped[0] in '•·-–*':
            story.append(bullet_para(stripped, styles))
            continue

        if ' · ' in stripped and len(stripped) < 120:
            story.append(Paragraph(f"<i>{stripped}</i>", styles['entry_sub']))
            continue

        # Line with trailing year and leading text separated by wide space
        m = re.match(r'^(.+?)\s{3,}((19|20)\d{2}[\w\s\-–]*)$', stripped)
        if m:
            t = Table([[Paragraph(m.group(1), styles['entry_title']),
                        Paragraph(m.group(2).strip(), styles['date'])]], colWidths=cw)
            t.setStyle(TableStyle([
                ('VALIGN',(0,0),(-1,-1),'TOP'),
                ('LEFTPADDING',(0,0),(-1,-1),0),
                ('RIGHTPADDING',(0,0),(-1,-1),0),
                ('TOPPADDING',(0,0),(-1,-1),0),
                ('BOTTOMPADDING',(0,0),(-1,-1),2),
            ]))
            story.append(t)
            continue

        story.append(Paragraph(stripped, styles['body']))

    return story

# ── Main entry ────────────────────────────────────────────────────────────────
def generate_pdf(resume_data, output_path: str):
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    M = 0.65 * inch
    doc = SimpleDocTemplate(output_path, pagesize=letter,
        leftMargin=M, rightMargin=M, topMargin=0.6*inch, bottomMargin=0.6*inch,
        title="Resume")

    W = letter[0] - 2*M
    S = make_styles()

    if isinstance(resume_data, dict):
        story = build_from_dict(resume_data, S, W)
    else:
        story = build_from_str(str(resume_data), S, W)

    doc.build(story)

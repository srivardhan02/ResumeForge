"""
matcher.py  –  ResumeForge
Keyword matching between resume and job description.
No LLM — pure text NLP.
Returns: ats_score, matched_keywords, missing_keywords, high_priority_missing, recommendations.
"""

import re

STOP_WORDS = {
    "the","a","an","and","or","but","in","on","at","to","for","of","with",
    "by","from","is","are","was","were","be","been","have","has","had","do",
    "does","did","will","would","could","should","may","might","must","can",
    "this","that","these","those","we","you","they","he","she","it","our",
    "your","their","its","experience","strong","ability","work","working",
    "using","use","used","good","excellent","well","also","both","including",
    "as","such","other","new","etc","any","all","who","what","when","where",
    "how","not","if","so","up","out","about","into","than","more","just",
    "over","after","while","through","during","before","between","following",
}

# High-value tech keywords — used to flag high_priority_missing
TECH_KEYWORDS = {
    # Languages
    "python","javascript","typescript","java","c++","c#","go","rust","ruby",
    "php","swift","kotlin","scala","matlab","bash","r",
    # Robotics / UAV
    "ros","mavlink","ardupilot","px4","pixhawk","sitl","gazebo","rviz",
    "mission planner","qgroundcontrol","dronekit","mavsdk","betaflight",
    # Embedded / IoT
    "embedded","arduino","stm32","esp32","raspberry pi","rtos","freertos",
    "can bus","uart","spi","i2c","pwm","firmware",
    # CV / ML
    "opencv","yolo","tensorflow","pytorch","scikit-learn","keras",
    "machine learning","deep learning","computer vision","nlp","numpy","pandas",
    # Control / Math
    "pid","kalman","kalman filter","sensor fusion","imu","lidar","slam",
    "path planning","control systems","kinematics","dynamics",
    # Cloud / DevOps
    "aws","gcp","azure","docker","kubernetes","git","linux","ubuntu","ci/cd",
    # General tech
    "api","rest","sql","postgresql","mongodb","redis","microservices","agile",
}


def keyword_match(structured: dict, job_description: str) -> dict:
    resume_text = _flatten_resume(structured).lower()
    jd_keywords = _extract_keywords(job_description.lower())

    matched = []
    missing = []
    for kw in jd_keywords:
        (matched if kw in resume_text else missing).append(kw)

    total = len(jd_keywords) or 1
    ats_score = round(len(matched) / total * 100)

    high_priority_missing = [kw for kw in missing if kw in TECH_KEYWORDS]
    normal_missing        = [kw for kw in missing if kw not in TECH_KEYWORDS]

    return {
        "ats_score":             ats_score,
        "matched_keywords":      matched[:20],
        "missing_keywords":      missing[:20],
        "high_priority_missing": high_priority_missing[:10],
        "total_jd_keywords":     len(jd_keywords),
        "total_matched":         len(matched),
        "recommendations":       _recommendations(matched, high_priority_missing, ats_score),
    }


def _extract_keywords(text: str) -> list:
    found = []
    # Multi-word tech terms first
    for tech in sorted(TECH_KEYWORDS, key=len, reverse=True):
        if " " in tech and tech in text:
            found.append(tech)

    # Single tokens
    tokens = re.findall(r'\b[a-z][a-z0-9+#.\-]*\b', text)
    seen = set(found)
    for t in tokens:
        t = t.strip('-.')
        if len(t) >= 3 and t not in STOP_WORDS and t not in seen:
            seen.add(t)
            found.append(t)
    return found


def _flatten_resume(structured: dict) -> str:
    parts = []
    def walk(obj):
        if isinstance(obj, dict):
            for v in obj.values(): walk(v)
        elif isinstance(obj, list):
            for i in obj: walk(i)
        elif isinstance(obj, str):
            parts.append(obj)
    walk(structured)
    return " ".join(parts)


def _recommendations(matched, high_priority_missing, score) -> list:
    recs = []
    if   score < 40: recs.append("Low keyword overlap. Heavily rewrite skills and summary.")
    elif score < 60: recs.append("Moderate match. Add missing keywords in experience bullets.")
    elif score < 80: recs.append("Good match. A few targeted additions will improve your score.")
    else:            recs.append("Excellent keyword match!")

    if high_priority_missing:
        recs.append(f"High-priority skills to add: {', '.join(high_priority_missing[:5])}")
    if matched:
        recs.append(f"Strong matches: {', '.join(matched[:5])} — keep these prominent.")
    return recs

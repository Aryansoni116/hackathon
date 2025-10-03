import re
import PyPDF2


SKILLS_DATABASE = {
    "python": ["python", "py", "django", "flask"],
    "java": ["java", "spring", "j2ee"],
    "javascript": ["javascript", "js", "react", "angular", "vue", "node"],
    "html": ["html", "html5"],
    "css": ["css", "css3", "sass", "scss"],
    "sql": ["sql", "mysql", "postgresql", "mongodb", "database"],
    "machine learning": ["machine learning", "ml", "ai", "tensorflow", "pytorch", "keras"],
    "data analysis": ["data analysis", "pandas", "numpy", "analytics"],
    "cloud": ["aws", "azure", "gcp", "cloud"],
    "devops": ["docker", "kubernetes", "jenkins", "ci/cd"]
}

def extract_skills_from_text(text):
    """Extract skills from text using keyword matching"""
    text = text.lower()
    found_skills = set()
    
    for skill, keywords in SKILLS_DATABASE.items():
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                found_skills.add(skill)
                break
    
    return list(found_skills)

def parse_resume(filepath):
    text = ""

    try:
        if filepath.lower().endswith(".pdf"):
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + " "
        else:
            
            encodings = ['utf-8', 'latin-1', 'iso-8859-1']
            for encoding in encodings:
                try:
                    with open(filepath, "r", encoding=encoding) as f:
                        text = f.read()
                    break
                except UnicodeDecodeError:
                    continue
    except Exception as e:
        print(f"Error parsing resume: {e}")
        return []

    return extract_skills_from_text(text)
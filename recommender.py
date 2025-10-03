import json
import os
from difflib import SequenceMatcher

ROLE_FILE = os.path.join(os.path.dirname(__file__), "role_catalog.json")

def skill_similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def recommend_roles(user_skills):
    try:
        with open(ROLE_FILE, "r") as f:
            roles = json.load(f)
    except FileNotFoundError:
        print("Role catalog not found, using default roles")
        roles = {
            "Frontend Developer": ["html", "css", "javascript", "react"],
            "Backend Developer": ["python", "flask", "django", "node", "sql"],
            "Data Analyst": ["python", "sql", "pandas", "numpy"],
            "ML Engineer": ["python", "ml", "tensorflow", "pandas", "numpy"],
            "Full Stack Developer": ["html", "css", "javascript", "react", "python", "flask", "sql"]
        }

    recommendations = []
    user_skills_lower = [skill.lower() for skill in user_skills]
    
    for role, required_skills in roles.items():
        matched_skills = []
        for req_skill in required_skills:
            req_skill_lower = req_skill.lower()
            if req_skill_lower in user_skills_lower:
                matched_skills.append(req_skill)
            else:
                for user_skill in user_skills:
                    if skill_similarity(req_skill_lower, user_skill.lower()) > 0.8:
                        matched_skills.append(req_skill)
                        break
        
        match_score = len(matched_skills)
        match_percentage = int((match_score / len(required_skills)) * 100) if required_skills else 0
        
        if match_score > 0:
            recommendations.append({
                "role": role,
                "match": match_score,
                "match_percentage": match_percentage,
                "required_skills": required_skills,
                "matched_skills": matched_skills
            })

    return sorted(recommendations, key=lambda x: x["match_percentage"], reverse=True)[:5]

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from recommender import recommend_roles
from resume_parser import parse_resume

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

RESOURCES_FILE = os.path.join(os.path.dirname(__file__), "resources.json")

def get_learning_resources(skills):
    try:
        with open(RESOURCES_FILE, "r") as f:
            resources = json.load(f)
        
        learning_resources = []
        for skill in skills:
            if skill.lower() in resources:
                learning_resources.extend(resources[skill.lower()])
        return learning_resources
    except Exception as e:
        print(f"Error loading resources: {e}")
        return []

@app.route("/")
def home():
    return jsonify({"message": "AI Career Mentor Backend is running ✅"})

@app.route("/upload_resume", methods=["POST"])
def upload_resume():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    skills = parse_resume(filepath)
    recommendations = recommend_roles(skills)

    return jsonify({"skills": skills, "recommendations": recommendations})

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()
    if not data or "skills" not in data:
        return jsonify({"error": "No skills provided"}), 400

    recommendations = recommend_roles(data["skills"])
    return jsonify({"recommendations": recommendations})

@app.route("/analyze_profile", methods=["POST"])
def analyze_profile():
    data = request.get_json()
    if not data or "resume_text" not in data:
        return jsonify({"error": "Invalid input"}), 400

    resume_text = data["resume_text"]
    skills = data.get("skills", [])
    interests = data.get("interests", [])

    recommendations = recommend_roles(skills)

    roles = []
    for rec in recommendations:
        matched_skills = list(set(skills) & set(rec["required_skills"]))
        missing_skills = list(set(rec["required_skills"]) - set(skills))
        missing_resources = get_learning_resources(missing_skills)
        
        roles.append({
            "role": rec["role"],
            "score": rec["match"],
            "description": f"A career as a {rec['role']} could be a great fit based on your skills.",
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "learning_path": generate_learning_path(rec["role"], missing_skills),
            "resources": missing_resources[:3]
        })

    return jsonify({
        "roles": roles,
        "profile_summary": {
            "total_skills": len(skills),
            "matched_roles": len(roles),
            "top_interests": interests[:3]
        }
    })

def generate_learning_path(role, missing_skills):
    if not missing_skills:
        return [
            {"week": 1, "goals": ["Advanced topics"], "tasks": ["Explore advanced concepts in your field"]},
            {"week": 2, "goals": ["Portfolio enhancement"], "tasks": ["Build complex projects"]},
            {"week": 3, "goals": ["Industry trends"], "tasks": ["Research latest industry developments"]}
        ]
    
    return [
        {"week": 1, "goals": [f"Learn {missing_skills[0]}"], "tasks": ["Complete beginner tutorials", "Practice basic exercises"]},
        {"week": 2, "goals": [f"Master {missing_skills[0]}", "Start project"], "tasks": ["Build small project", "Study intermediate concepts"]},
        {"week": 3, "goals": ["Deepen knowledge", "Portfolio development"], "tasks": ["Create portfolio piece", "Study advanced topics"]},
        {"week": 4, "goals": ["Interview preparation"], "tasks": ["Practice coding challenges", "Study interview questions"]}
    ]

@app.route("/health")
def health_check():
    return jsonify({"status": "healthy", "service": "AI Career Mentor"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

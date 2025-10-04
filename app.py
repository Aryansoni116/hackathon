from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import google.generativeai as genai

# === Flask setup ===
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# === Gemini setup ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        GEMINI_ENABLED = True
        print("✅ Gemini API configured successfully")
    except Exception as e:
        print(f"❌ Error configuring Gemini: {e}")
        GEMINI_ENABLED = False
else:
    print("⚠️  GEMINI_API_KEY not set. Chat endpoint will not work.")
    GEMINI_ENABLED = False

# === Chat memory store ===
chat_history = []

# Load learning resources with fallback
def get_learning_resources(skills):
    """Return learning resources for a given list of skills."""
    try:
        RESOURCES_FILE = os.path.join(os.path.dirname(__file__), "resources.json")
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

# Fallback functions if recommender.py or resume_parser.py are missing
def recommend_roles(skills):
    """Fallback recommendation function"""
    try:
        from recommender import recommend_roles as rr
        return rr(skills)
    except ImportError:
        # Simple fallback recommendations
        roles = []
        if any(skill.lower() in ['python', 'machine learning', 'ai'] for skill in skills):
            roles.append({"role": "AI/ML Engineer", "match": 85, "required_skills": ["Python", "Machine Learning"]})
        if any(skill.lower() in ['javascript', 'html', 'css'] for skill in skills):
            roles.append({"role": "Web Developer", "match": 78, "required_skills": ["JavaScript", "HTML", "CSS"]})
        if not roles:
            roles.append({"role": "Software Developer", "match": 70, "required_skills": ["Programming"]})
        return roles

def parse_resume(filepath):
    """Fallback resume parsing function"""
    try:
        from resume_parser import parse_resume as pr
        return pr(filepath)
    except ImportError:
        # Return some default skills
        return ["Python", "Problem Solving", "Communication"]

@app.route("/")
def home():
    return jsonify({
        "message": "AI Career Mentor Backend is running ✅",
        "chat_enabled": GEMINI_ENABLED
    })

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
    """Generate a personalized learning path."""
    if not missing_skills:
        return [
            {"week": 1, "goals": ["Advanced topics"], "tasks": ["Explore advanced concepts"]},
            {"week": 2, "goals": ["Portfolio enhancement"], "tasks": ["Build complex projects"]},
            {"week": 3, "goals": ["Industry trends"], "tasks": ["Research latest developments"]}
        ]

    return [
        {"week": 1, "goals": [f"Learn {missing_skills[0]}"], "tasks": ["Complete tutorials", "Practice exercises"]},
        {"week": 2, "goals": [f"Master {missing_skills[0]}"], "tasks": ["Build project", "Study concepts"]},
        {"week": 3, "goals": ["Portfolio development"], "tasks": ["Create portfolio piece"]},
        {"week": 4, "goals": ["Interview preparation"], "tasks": ["Practice challenges"]}
    ]

# === Gemini Chatbot Endpoint - FIXED VERSION ===
@app.route("/chat", methods=["POST"])
def chat():
    if not GEMINI_ENABLED:
        return jsonify({
            "error": "Gemini API not configured",
            "message": "Please set GEMINI_API_KEY environment variable to enable chat features."
        }), 503

    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data received"}), 400
        
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Keep conversation history (last 10 messages)
        chat_history.append({"role": "user", "content": user_message})
        if len(chat_history) > 10:
            chat_history.pop(0)

        # Create context for career-focused responses - FIXED PROMPT
        context = """You are an AI Career Mentor assistant. You help users with:
        - Career guidance and advice
        - Skill development recommendations  
        - Job search strategies
        - Interview preparation
        - Learning path suggestions
        - Resume and portfolio tips
        
        Be helpful, encouraging, and professional. Provide practical, actionable advice.
        
        Conversation history:
        """
        
        history_text = "\n".join(
            [f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history[-6:]]  # Last 6 messages
        )
        
        # FIX: Include the current user message in the prompt
        full_prompt = context + history_text + f"\nUser: {user_message}\nAssistant:"

        response = model.generate_content(full_prompt)
        
        if response and hasattr(response, 'text'):
            reply = response.text
        else:
            reply = "I apologize, but I couldn't generate a response at the moment. Please try again."

        # Save assistant reply to memory
        chat_history.append({"role": "assistant", "content": reply})

        return jsonify({"reply": reply})
        
    except Exception as e:
        print(f"Gemini API Error: {e}")
        # Return a helpful response instead of error 500
        return jsonify({
            "reply": "I'm currently experiencing technical difficulties. Please try again in a moment or check if your Gemini API key is properly configured."
        })

@app.route("/health")
def health_check():
    return jsonify({
        "status": "healthy", 
        "service": "AI Career Mentor",
        "gemini_enabled": GEMINI_ENABLED,
        "endpoints": {
            "chat": "/chat",
            "health": "/health", 
            "analyze_profile": "/analyze_profile",
            "upload_resume": "/upload_resume"
        }
    })

if __name__ == "__main__":
    print(f"🚀 Starting AI Career Mentor Backend...")
    print(f"💬 Gemini Chat: {'✅ Enabled' if GEMINI_ENABLED else '❌ Disabled'}")
    app.run(host="0.0.0.0", port=5000, debug=False)  # Set debug=False for production

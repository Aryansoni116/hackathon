from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import google.generativeai as genai
import random

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
    print("⚠️  GEMINI_API_KEY not set. Using mock responses.")
    GEMINI_ENABLED = False

# === Chat memory store ===
chat_history = []

# Mock responses for career advice
MOCK_RESPONSES = [
    "Hello! I'm your AI Career Assistant. I can help you with career guidance, skill recommendations, and learning paths!",
    "Hi there! I see you're interested in career development. Tell me about your skills or career goals!",
    "Welcome! I specialize in career advice and skill development. How can I assist you today?",
    "Hello! I can help you explore career options based on your skills and interests. What would you like to know?",
    "Hi! I'm here to help with your career journey. Ask me about job roles, skills to learn, or career paths!"
]

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
        if any(skill.lower() in ['python', 'machine learning', 'ai', 'data science'] for skill in skills):
            roles.append({"role": "AI/ML Engineer", "match": 85, "required_skills": ["Python", "Machine Learning", "Data Analysis"]})
        if any(skill.lower() in ['javascript', 'html', 'css', 'react', 'web'] for skill in skills):
            roles.append({"role": "Web Developer", "match": 78, "required_skills": ["JavaScript", "HTML", "CSS", "React"]})
        if any(skill.lower() in ['sql', 'data analysis', 'excel', 'statistics'] for skill in skills):
            roles.append({"role": "Data Analyst", "match": 75, "required_skills": ["SQL", "Data Analysis", "Statistics"]})
        if not roles:
            roles.append({"role": "Software Developer", "match": 70, "required_skills": ["Programming", "Problem Solving"]})
        return roles

def parse_resume(filepath):
    """Fallback resume parsing function"""
    try:
        from resume_parser import parse_resume as pr
        return pr(filepath)
    except ImportError:
        # Return some default skills
        return ["Python", "Problem Solving", "Communication", "Teamwork"]

@app.route("/")
def home():
    return jsonify({
        "message": "AI Career Mentor Backend is running ✅",
        "chat_enabled": True,
        "gemini_enabled": GEMINI_ENABLED,
        "endpoints": ["/health", "/chat", "/analyze_profile", "/upload_resume"]
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
            "top_interests": interests[:3] if interests else ["Technology", "Development", "Analysis"]
        }
    })

def generate_learning_path(role, missing_skills):
    """Generate a personalized learning path."""
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

# === WORKING Chatbot Endpoint ===
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
            
        user_message = data.get("message", "").strip().lower()
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # If Gemini is enabled and working, use it
        if GEMINI_ENABLED:
            try:
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                # Create context for career-focused responses
                prompt = f"""You are an AI Career Mentor assistant. You help users with career guidance, skill development, job search strategies, interview preparation, and learning path suggestions. Be helpful, encouraging, and professional. Provide practical, actionable advice.

                User message: {user_message}

                Provide a helpful career-focused response:"""
                
                response = model.generate_content(prompt)
                
                if response and hasattr(response, 'text'):
                    reply = response.text
                else:
                    # Fallback to mock responses if Gemini fails
                    reply = get_mock_response(user_message)
                    
            except Exception as e:
                print(f"Gemini API error, using mock response: {e}")
                reply = get_mock_response(user_message)
        else:
            # Use mock responses
            reply = get_mock_response(user_message)
        
        return jsonify({"reply": reply, "gemini_used": GEMINI_ENABLED and "Gemini" in reply})
        
    except Exception as e:
        print(f"Chat endpoint error: {e}")
        return jsonify({"reply": "Hello! I'm your AI Career Assistant. How can I help you with your career today?"})

def get_mock_response(user_message):
    """Get appropriate mock response based on user message"""
    if any(word in user_message for word in ['hi', 'hello', 'hey', 'hola']):
        return random.choice(MOCK_RESPONSES)
    elif 'python' in user_message:
        return "Python is a great skill! It's used in web development (Django/Flask), data science (pandas, numpy), and AI (TensorFlow, PyTorch). I recommend building real projects to practice."
    elif 'javascript' in user_message or 'js' in user_message:
        return "JavaScript is essential for web development! Consider learning React for frontend or Node.js for backend development. Great career options include Frontend Developer or Full Stack Engineer."
    elif 'machine learning' in user_message or 'ml' in user_message or 'ai' in user_message:
        return "Machine Learning and AI are high-demand fields! Start with Python, then learn libraries like scikit-learn, TensorFlow, or PyTorch. Build projects with real datasets to showcase your skills."
    elif 'web development' in user_message or 'web dev' in user_message:
        return "Web development has great opportunities! Focus on HTML/CSS, JavaScript, and a framework like React. For backend, learn Node.js, Python (Django/Flask), or Java. Build portfolio projects to demonstrate your skills."
    elif 'data' in user_message or 'analysis' in user_message:
        return "Data skills are in high demand! Learn SQL for databases, Python with pandas for analysis, and visualization tools like Tableau or matplotlib. Practice with real datasets on platforms like Kaggle."
    elif 'career' in user_message or 'job' in user_message or 'role' in user_message:
        return "I can help you explore career paths! Popular tech roles include: Software Developer, Data Scientist, Web Developer, AI Engineer, DevOps Engineer, and Product Manager. What skills do you currently have?"
    elif 'skill' in user_message or 'learn' in user_message:
        return "Top skills to learn in 2024: Python, JavaScript, React, SQL, Data Analysis, Machine Learning, Cloud Computing (AWS/Azure), and DevOps. Which area interests you most? I can provide specific learning resources."
    elif 'salary' in user_message or 'pay' in user_message:
        return "Tech salaries vary by role, experience, and location. Typical ranges:\n• Entry-level: $60,000 - $80,000\n• Mid-level: $80,000 - $120,000\n• Senior: $120,000 - $180,000+\n• Specialized roles (AI/ML): $100,000 - $200,000+"
    elif 'interview' in user_message:
        return "For tech interviews, practice:\n1. Coding challenges (LeetCode, HackerRank)\n2. System design questions\n3. Behavioral questions (STAR method)\n4. Your projects and experience\nPrepare a portfolio and practice explaining your code."
    elif 'project' in user_message:
        return "Great projects for your portfolio:\n• Web app with user authentication\n• Data analysis with visualizations\n• Machine learning model deployment\n• Mobile app\n• API development\nChoose projects that solve real problems!"
    else:
        return "I'm here to help with career advice! You can ask me about:\n• Career paths and job roles\n• Skills to learn and resources\n• Salary expectations\n• Interview preparation\n• Project ideas for your portfolio\n• Learning roadmaps\n\nWhat would you like to know about your career development?"

@app.route("/health")
def health_check():
    return jsonify({
        "status": "healthy", 
        "service": "AI Career Mentor",
        "chat_enabled": True,
        "gemini_enabled": GEMINI_ENABLED,
        "endpoints": {
            "chat": "/chat (POST)",
            "health": "/health (GET)", 
            "analyze_profile": "/analyze_profile (POST)",
            "upload_resume": "/upload_resume (POST)",
            "recommend": "/recommend (POST)"
        }
    })

if __name__ == "__main__":
    print(f"🚀 Starting AI Career Mentor Backend...")
    print(f"💬 Gemini Chat: {'✅ Enabled' if GEMINI_ENABLED else '❌ Disabled (using mock responses)'}")
    print(f"🌐 Health check: https://hackathon-78xd.onrender.com/health")
    app.run(host="0.0.0.0", port=5000, debug=False)

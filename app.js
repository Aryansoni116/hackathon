const API = "https://hackathon-78xd.onrender.com";
const rolesContainer = document.getElementById("rolesContainer");
const results = document.getElementById("results");

window.onload = () => {
  document.getElementById("name").value = "Aryan Soni";
  document.getElementById("email").value = "aryan.soni@example.com";
  document.getElementById("education").value = "B.Tech in Computer Science (2021-2025)";
  document.getElementById("skills").value = "Python, Machine Learning, SQL, HTML, CSS, JavaScript";
  document.getElementById("projects").value =
    "1. AI Chatbot using Python and NLP\n2. Portfolio Website\n3. Sales Data Analysis with Pandas";
  document.getElementById("interests").value =
    "Artificial Intelligence, Web Development, Data Analysis";
};

function updateProgress(step) {
  const progressBar = document.getElementById("progressBar");
  const percentage = (step / 6) * 100;
  progressBar.style.width = `${percentage}%`;

  const steps = document.querySelectorAll(".progress-step");
  steps.forEach((s, index) => {
    if (index < step) s.classList.add("active");
    else s.classList.remove("active");
  });
}

function nextStep(currentStep) {
  if (!validateStep(currentStep)) return;
  document.getElementById(`step${currentStep}`).classList.add("hidden");
  document.getElementById(`step${currentStep + 1}`).classList.remove("hidden");
  updateProgress(currentStep + 1);
}

function validateStep(step) {
  switch (step) {
    case 1:
      const name = document.getElementById("name").value.trim();
      if (!name) {
        alert("Please enter your name");
        return false;
      }
      break;
    case 2:
      const email = document.getElementById("email").value.trim();
      if (!email || !isValidEmail(email)) {
        alert("Please enter a valid email address");
        return false;
      }
      break;
    case 4:
      const skills = document.getElementById("skills").value.trim();
      if (!skills) {
        alert("Please enter at least one skill");
        return false;
      }
      break;
  }
  return true;
}

function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

async function submitProfile() {
  if (!validateStep(6)) return;

  const name = document.getElementById("name").value.trim();
  const email = document.getElementById("email").value.trim();
  const education = document.getElementById("education").value.trim();
  const skills = document
    .getElementById("skills")
    .value.split(",")
    .map((s) => s.trim())
    .filter(Boolean);
  const projects = document.getElementById("projects").value.trim();
  const interests = document
    .getElementById("interests")
    .value.split(",")
    .map((s) => s.trim())
    .filter(Boolean);

  const resumeText = `
Name: ${name}
Email: ${email}
Education: ${education}
Skills: ${skills.join(", ")}
Projects: ${projects}
Interests: ${interests.join(", ")}
  `;

  const payload = {
    resume_text: resumeText,
    skills: skills.map((s) => s.toLowerCase()),
    interests: interests.map((i) => i.toLowerCase()),
  };

  try {
    showLoading(true);

    const res = await fetch(`${API}/analyze_profile`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

    const data = await res.json();
    displayResults(data.roles, data.profile_summary);
  } catch (err) {
    console.error("Error analyzing profile:", err);
    alert(" Failed to analyze profile. Make sure backend is running on http://localhost:5000");
  } finally {
    showLoading(false);
  }
}

function showLoading(show) {
  const submitBtn = document.querySelector("#step6 .btn");
  if (show) {
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
    submitBtn.disabled = true;
  } else {
    submitBtn.innerHTML = "Get Recommendations <i class='fas fa-rocket'></i>";
    submitBtn.disabled = false;
  }
}

function displayResults(roles, summary) {
  results.classList.remove("hidden");
  document.getElementById("stepForm").classList.add("hidden");

  rolesContainer.innerHTML = "";

  if (!roles || roles.length === 0) {
    rolesContainer.innerHTML = `
      <div class="role-card">
        <h3>No matches found</h3>
        <p>Try adding more skills or broadening your interests.</p>
      </div>
    `;
    return;
  }

  roles.forEach((r, index) => {
    setTimeout(() => {
      const div = document.createElement("div");
      div.className = "role-card fade-in";

      const safeResources = (r.resources || []).map((res) => {
        const url = res.url && res.url.startsWith("http") ? res.url : "https://www.w3schools.com/";
        return { title: res.title || "Learning Resource", url };
      });

      div.innerHTML = `
        <div class="role-header">
          <h3>${r.role}</h3>
          <span class="match-badge">${r.match_percentage || r.score}% Match</span>
        </div>
        <p>${r.description}</p>
        
        <div class="skills-section">
          <div class="skill-group">
            <strong> Matched Skills:</strong> 
            ${r.matched_skills?.length > 0 ? r.matched_skills.join(", ") : "None"}
          </div>
          <div class="skill-group">
            <strong> To Learn:</strong> 
            ${r.missing_skills?.length > 0 ? r.missing_skills.join(", ") : "You have all required skills!"}
          </div>
        </div>
        
        <div class="learning-path">
          <strong> Learning Path:</strong>
          <ul>
            ${r.learning_path
              ?.map(
                (w) => `
              <li>
                <strong>Week ${w.week}:</strong> ${w.goals.join(", ")}
                <br><em>→ ${w.tasks.join(", ")}</em>
              </li>
            `
              )
              .join("") || ""}
          </ul>
        </div>
        
        ${
          safeResources.length > 0
            ? `
        <div class="resources">
          <strong> Recommended Resources:</strong>
          <ul>
            ${safeResources
              .map((res) => `<li><a href="${res.url}" target="_blank">${res.title}</a></li>`)
              .join("")}
          </ul>
        </div>
        `
            : ""
        }
      `;
      rolesContainer.appendChild(div);
    }, index * 200);
  });
}

function restartProcess() {
  results.classList.add("hidden");
  document.getElementById("dashboard").classList.add("hidden");
  document.getElementById("stepForm").classList.remove("hidden");

  document.querySelectorAll(".form-step").forEach((s, i) => {
    if (i === 0) s.classList.remove("hidden");
    else s.classList.add("hidden");
  });

  updateProgress(1);

  rolesContainer.innerHTML = "";

  document.getElementById("name").value = "";
  document.getElementById("email").value = "";
  document.getElementById("education").value = "";
  document.getElementById("skills").value = "";
  document.getElementById("projects").value = "";
  document.getElementById("interests").value = "";
}

document.addEventListener("keypress", function (e) {
  if (e.key === "Enter") {
    const visibleStep = document.querySelector(".form-step:not(.hidden)");
    if (visibleStep) {
      const stepNumber = parseInt(visibleStep.id.replace("step", ""));
      if (stepNumber < 6) nextStep(stepNumber);
      else submitProfile();
    }
  }
});

// Dashboard Functions
function showDashboard() {
  document.getElementById("results").classList.add("hidden");
  document.getElementById("dashboard").classList.remove("hidden");
  populateDashboard();
}

function showResults() {
  document.getElementById("dashboard").classList.add("hidden");
  document.getElementById("results").classList.remove("hidden");
}

function populateDashboard() {
  document.getElementById("dashboard-name").textContent = document.getElementById("name").value;
  document.getElementById("dashboard-education").textContent = document.getElementById("education").value;
  document.getElementById("dashboard-skills").textContent = document.getElementById("skills").value;
  document.getElementById("dashboard-interests").textContent = document.getElementById("interests").value;
  
  populateCareerProgress();
  populateSkillTracker();
  populateLearningGoals();
  populateProgressTimeline();
  populateRecommendedActions();
}

function populateCareerProgress() {
  const rolesContainer = document.getElementById("rolesContainer");
  const careerProgressChart = document.getElementById("careerProgressChart");
  
  if (!rolesContainer.children.length) {
    careerProgressChart.innerHTML = "<p>No career matches yet. Complete the assessment to see your matches.</p>";
    return;
  }
  
  let progressHTML = "";
  const roleCards = rolesContainer.getElementsByClassName("role-card");
  
  for (let card of roleCards) {
    const roleTitle = card.querySelector("h3").textContent;
    const matchPercentage = card.querySelector(".match-badge").textContent;
    const percentageValue = parseInt(matchPercentage);
    
    progressHTML += `
      <div class="progress-item">
        <div class="progress-role">
          <span>${roleTitle}</span>
          <span>${matchPercentage}</span>
        </div>
        <div class="progress-bar-container">
          <div class="progress-bar-fill" style="width: ${percentageValue}%"></div>
        </div>
      </div>
    `;
  }
  
  careerProgressChart.innerHTML = progressHTML;
}

function populateSkillTracker() {
  const skillsInput = document.getElementById("skills").value;
  const currentSkills = skillsInput.split(",").map(skill => skill.trim()).filter(Boolean);
  
  let currentSkillsHTML = "";
  currentSkills.forEach(skill => {
    currentSkillsHTML += `<span class="skill-tag">${skill}</span>`;
  });
  
  document.getElementById("currentSkills").innerHTML = currentSkillsHTML;
  
  const skillsToDevelop = ["Machine Learning", "Deep Learning", "Cloud Computing", "Docker", "Kubernetes"];
  let skillsToDevelopHTML = "";
  skillsToDevelop.forEach(skill => {
    skillsToDevelopHTML += `<span class="skill-tag to-learn">${skill}</span>`;
  });
  
  document.getElementById("skillsToDevelop").innerHTML = skillsToDevelopHTML;
}

function populateLearningGoals() {
  const goals = [
    { text: "Complete Python for Data Science course", completed: false },
    { text: "Build a machine learning project", completed: false },
    { text: "Learn about cloud deployment", completed: false }
  ];
  
  let goalsHTML = "";
  goals.forEach((goal, index) => {
    goalsHTML += `
      <div class="goal-item ${goal.completed ? 'completed' : ''}">
        <input type="checkbox" ${goal.completed ? 'checked' : ''} onchange="toggleGoal(${index})">
        <span>${goal.text}</span>
      </div>
    `;
  });
  
  document.getElementById("learningGoalsList").innerHTML = goalsHTML;
}

function addLearningGoal() {
  const newGoalInput = document.getElementById("newGoal");
  const goalText = newGoalInput.value.trim();
  
  if (goalText) {
    const goalsList = document.getElementById("learningGoalsList");
    const goalItem = document.createElement("div");
    goalItem.className = "goal-item";
    goalItem.innerHTML = `
      <input type="checkbox" onchange="toggleGoal(this)">
      <span>${goalText}</span>
    `;
    
    goalsList.appendChild(goalItem);
    newGoalInput.value = "";
  }
}

function toggleGoal(checkbox) {
  const goalItem = checkbox.parentElement;
  goalItem.classList.toggle('completed');
}

function populateProgressTimeline() {
  const timeline = [
    { date: "Today", content: "Completed career assessment" },
    { date: "This Week", content: "Review recommended career paths" },
    { date: "Next 2 Weeks", content: "Start first learning goal" },
    { date: "Next Month", content: "Complete first project" }
  ];
  
  let timelineHTML = "";
  timeline.forEach(item => {
    timelineHTML += `
      <div class="timeline-item">
        <div class="timeline-date">${item.date}</div>
        <div class="timeline-content">${item.content}</div>
      </div>
    `;
  });
  
  document.getElementById("progressTimeline").innerHTML = timelineHTML;
}

function populateRecommendedActions() {
  const actions = [
    { type: "success", icon: "fas fa-book", text: "Review the learning resources for your top career match" },
    { type: "warning", icon: "fas fa-exclamation-triangle", text: "Focus on developing your missing skills" },
    { type: "success", icon: "fas fa-project-diagram", text: "Start a small project to apply your current skills" }
  ];
  
  let actionsHTML = "";
  actions.forEach(action => {
    actionsHTML += `
      <div class="action-item ${action.type === 'warning' ? 'warning' : ''}">
        <i class="${action.icon}"></i>
        <span>${action.text}</span>
      </div>
    `;
  });
  
  document.getElementById("recommendedActions").innerHTML = actionsHTML;
}

function exportDashboard() {
  alert("Dashboard export functionality would be implemented here. In a real application, this would generate a PDF report of your career progress.");
}

updateProgress(1);

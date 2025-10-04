const API = "https://hackathon-78xd.onrender.com";
const rolesContainer = document.getElementById("rolesContainer");
const results = document.getElementById("results");

// Chatbot elements
const chatbot = document.getElementById('chatbot');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendMessageBtn = document.getElementById('sendMessage');
const closeChatBtn = document.querySelector('.close-btn');
const aiAssistantBtn = document.querySelector('.ai-assistant');
const typingIndicator = document.getElementById('typingIndicator');

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
    alert("Failed to analyze profile. Please try again.");
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

// === Chatbot functionality ===

// Toggle chatbot visibility
aiAssistantBtn.addEventListener('click', () => {
  chatbot.classList.toggle('hidden');
  if (!chatbot.classList.contains('hidden')) {
    chatInput.focus();
  }
});

closeChatBtn.addEventListener('click', () => {
  chatbot.classList.add('hidden');
});

// Send message when button is clicked
sendMessageBtn.addEventListener('click', sendMessage);

// Send message when Enter key is pressed
chatInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    sendMessage();
  }
});

// Add message to chat
function addMessageToChat(message, sender) {
  const messageDiv = document.createElement('div');
  messageDiv.className = sender;
  
  const messageP = document.createElement('p');
  messageP.textContent = message;
  
  messageDiv.appendChild(messageP);
  chatMessages.appendChild(messageDiv);
  
  // Scroll to bottom
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Show typing indicator
function showTypingIndicator() {
  typingIndicator.classList.add('show');
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Hide typing indicator
function hideTypingIndicator() {
  typingIndicator.classList.remove('show');
}

// Send message to backend
async function sendMessage() {
  const message = chatInput.value.trim();
  if (!message) return;

  // Add user message to chat
  addMessageToChat(message, 'user');
  chatInput.value = '';
  
  // Show typing indicator
  showTypingIndicator();
  
  try {
    const response = await fetch(`${API}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: message })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    // Hide typing indicator
    hideTypingIndicator();
    
    // Add AI response to chat
    if (data.reply) {
      addMessageToChat(data.reply, 'ai');
    } else if (data.error) {
      addMessageToChat(`Error: ${data.error}`, 'ai');
    } else {
      addMessageToChat("I'm sorry, I couldn't process your request. Please try again.", 'ai');
    }
  } catch (error) {
    console.error('Error sending message:', error);
    hideTypingIndicator();
    addMessageToChat("Sorry, I'm having trouble connecting to the chat service. Please make sure the backend server is running and try again.", 'ai');
  }
}

// Test backend connection on load
async function testBackendConnection() {
  try {
    const response = await fetch(`${API}/health`);
    if (response.ok) {
      console.log('✅ Backend connection successful');
    } else {
      console.log('❌ Backend connection failed');
    }
  } catch (error) {
    console.log('❌ Backend connection failed:', error);
  }
}

// Initialize
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

// Test connection when page loads
window.addEventListener('load', () => {
  testBackendConnection();
});

updateProgress(1);

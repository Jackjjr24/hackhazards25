function toggleDropdown(el) {
  const content = el.nextElementSibling;
  const icon = el.querySelector('.dropdown-icon');
  content.classList.toggle('active');
  icon.textContent = content.classList.contains('active') ? '▲' : '▼';
}

function switchTab(id) {
  document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  document.querySelector(`.tab[onclick="switchTab('${id}')"]`).classList.add('active');
}

function connectDB() {
  const payload = {
    db_type: document.getElementById("dbType").value,
    user: document.getElementById("username").value,
    password: document.getElementById("password").value,
    host: document.getElementById("host").value,
    port: document.getElementById("port").value,
    database: document.getElementById("dbname").value,
  };

  fetch("http://localhost:8000/api/connect", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  }).then(res => res.json())
    .then(data => {
      alert(data.message);
    }).catch(err => alert("Connection error"));
}

function sendQuery() {
  const query = document.getElementById("queryInput").value.trim();
  if (!query) return alert("Enter a query");

  fetch("http://localhost:8000/api/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query })
  }).then(res => res.json())
    .then(data => {
      displayQueryResult(query, data.response);
      if (document.getElementById("voiceToggle").checked) {
        const utterance = new SpeechSynthesisUtterance(data.response);
        speechSynthesis.speak(utterance);
      }
    });
}

function displayQueryResult(query, result) {
  const container = document.getElementById("resultsContainer");
  const q = document.createElement("div");
  q.className = "query-text";
  q.textContent = `> ${query}`;
  const r = document.createElement("pre");
  r.className = "query-result";
  r.textContent = result;
  container.appendChild(q);
  container.appendChild(r);
  container.scrollTop = container.scrollHeight;
}

function quickQuery(q) {
  document.getElementById("queryInput").value = q;
  sendQuery();
}

function getER() {
  fetch("http://localhost:8000/api/er-diagram")
    .then(res => res.json())
    .then(data => {
      const img = document.getElementById("erImage");
      img.src = `http://localhost:8000${data.image_path}`;
      img.style.display = "block";
    });
}

// 🔒 Logout logic: redirects to login.html on logout click
document.addEventListener("DOMContentLoaded", () => {
  const logoutBtn = document.querySelector(".logout-btn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      // Optional: clear session/local storage if used
      localStorage.clear();
      sessionStorage.clear();
      // Redirect to login page
      window.location.href = "login.html";
    });
  }
});

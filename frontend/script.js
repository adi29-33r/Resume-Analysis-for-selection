const analyzeBtn = document.getElementById("analyzeBtn");
const resumeFiles = document.getElementById("resumeFiles");
const statusDiv = document.getElementById("status");
const candidatesBody = document.getElementById("candidatesBody");
const modal = document.getElementById("modal");
const closeModal = document.getElementById("closeModal");
const modalBody = document.getElementById("modalBody");

const API_BASE = "http://127.0.0.1:8000";

analyzeBtn.addEventListener("click", async () => {
  const files = resumeFiles.files;
  if (!files || files.length === 0) {
    alert("Please select one or more resume files.");
    return;
  }

  statusDiv.innerText = "Uploading and analyzing...";
  const form = new FormData();
  for (let i = 0; i < files.length; i++) {
    form.append("files", files[i], files[i].name);
  }

  try {
    const resp = await fetch(`${API_BASE}/analyze-all-resumes/`, {
      method: "POST",
      body: form
    });

    if (!resp.ok) {
      const errText = await resp.text();
      throw new Error(`Backend returned error: ${errText}`);
    }

    const data = await resp.json();
    console.log("[DEBUG] Backend response:", data);

    if (data.results && data.results.length > 0) {
      statusDiv.innerText = `Analyzed ${data.count} resume(s).`;
      renderTable(data.results);
    } else {
      statusDiv.innerText = "No valid resumes were analyzed. Please check file format or content.";
    }
  } catch (err) {
    console.error("[ERROR] Analyze resumes failed:", err);
    statusDiv.innerText = `Error contacting backend: ${err.message}`;
  }
});

function renderTable(list) {
  candidatesBody.innerHTML = "";
  list.forEach(item => {
    const tr = document.createElement("tr");

    // Candidate ID
    const tdId = document.createElement("td");
    tdId.innerText = item.candidate_id;
    tr.appendChild(tdId);

    // Score
    const tdScore = document.createElement("td");
    tdScore.innerText = item.score ?? "-";
    tr.appendChild(tdScore);

    // Rank
    const tdRank = document.createElement("td");
    tdRank.innerText = item.rank ?? "-";
    tr.appendChild(tdRank);

    // Pass/Fail
    const tdPass = document.createElement("td");
    const badge = document.createElement("span");
    badge.className = item.pass ? "badge pass" : "badge fail";
    badge.innerText = item.pass ? "Pass" : "Fail";
    tdPass.appendChild(badge);
    tr.appendChild(tdPass);

    // Download PDF
    const tdDownload = document.createElement("td");
    const pdfBtn = document.createElement("button");
    pdfBtn.innerText = "PDF";
    pdfBtn.onclick = () => {
      window.open(`${API_BASE}/download/${item.candidate_id}/pdf`, "_blank");
    };
    tdDownload.appendChild(pdfBtn);
    tr.appendChild(tdDownload);

    // View Details
    const tdDetails = document.createElement("td");
    const viewBtn = document.createElement("button");
    viewBtn.innerText = "View";
    viewBtn.onclick = () => openDetails(item.candidate_id);
    tdDetails.appendChild(viewBtn);
    tr.appendChild(tdDetails);

    candidatesBody.appendChild(tr);
  });
}

async function openDetails(candidateId) {
  try {
    const resp = await fetch(`${API_BASE}/get-candidate-details/${candidateId}`);
    if (!resp.ok) {
      const errText = await resp.text();
      throw new Error(`Failed to load details: ${errText}`);
    }
    const details = await resp.json();
    console.log("[DEBUG] Candidate details:", details);
    showModal(details);
  } catch (err) {
    console.error("[ERROR] Open candidate details failed:", err);
    alert(err.message);
  }
}

function showModal(details) {
  modalBody.innerHTML = "";

  const title = document.createElement("h2");
  title.innerText = "Candidate Details";
  modalBody.appendChild(title);

  const fields = [
    { label: "Summary", value: details.summary || "N/A" },
    { label: "Skills Detected", value: (details.skills_detected || []).join(", ") || "None" },
    { label: "Experience (years)", value: details.experience_years ?? 0 },
    { label: "ATS Score", value: details.ats_score ?? details.keyword_score ?? 0 },
    { label: "Semantic Score", value: details.semantic_score ?? 0 },
    { label: "GenAI Suggestions", value: details.genai_suggestions || "No suggestions available." }
  ];

  fields.forEach(f => {
    if (f.label === "GenAI Suggestions") {
      const pre = document.createElement("pre");
      pre.innerText = f.value;
      modalBody.appendChild(pre);
    } else {
      const p = document.createElement("p");
      p.innerHTML = `<strong>${f.label}:</strong> ${escapeHtml(f.value)}`;
      modalBody.appendChild(p);
    }
  });

  modal.style.display = "block";
}

closeModal.onclick = () => {
  modal.style.display = "none";
};
window.onclick = (e) => {
  if (e.target === modal) modal.style.display = "none";
};

function escapeHtml(text) {
  if (!text) return "";
  return text
    .toString()
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

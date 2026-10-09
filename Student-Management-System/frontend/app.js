// Acadex Frontend Application Script
const API_BASE = ""; // Relative to host

// Global State
let currentUser = null;
let currentToken = localStorage.getItem("sms_token") || null;
let currentRole = localStorage.getItem("sms_role") || "student";
let activeStudentData = null;
let activeTeacherStudents = [];
let allSubjectNotes = [];
let selectedStudentForEdit = null;

// Initialize on DOM Ready
document.addEventListener("DOMContentLoaded", async () => {
  setupEventListeners();

  if (!currentToken) {
    // Automatically log in as default student for instant preview
    await quickLogin("student_aarav", "student123");
  } else {
    try {
      await fetchUserProfile();
      await loadPortalData();
    } catch (e) {
      console.warn("Session expired or invalid, re-authenticating as student_aarav");
      await quickLogin("student_aarav", "student123");
    }
  }

  if (window.lucide) {
    lucide.createIcons();
  }
});

function setupEventListeners() {
  // Quick switcher dropdown toggle
  const quickSwitchBtn = document.getElementById("quickSwitchBtn");
  const quickSwitchDropdown = document.getElementById("quickSwitchDropdown");
  if (quickSwitchBtn && quickSwitchDropdown) {
    quickSwitchBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      quickSwitchDropdown.classList.toggle("hidden");
    });

    document.addEventListener("click", () => {
      quickSwitchDropdown.classList.add("hidden");
    });
  }

  // Login form submit
  const loginForm = document.getElementById("loginForm");
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const u = document.getElementById("loginUsername").value.trim();
      const p = document.getElementById("loginPassword").value.trim();
      await performLogin(u, p);
    });
  }
}

// ----------------------------------------------------
// Authentication Handlers
// ----------------------------------------------------
async function performLogin(username, password) {
  try {
    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });

    if (!res.ok) {
      const err = await res.json();
      showToast(err.detail || "Authentication failed", "error");
      return;
    }

    const data = await res.json();
    currentToken = data.access_token;
    currentRole = data.role;
    localStorage.setItem("sms_token", currentToken);
    localStorage.setItem("sms_role", currentRole);

    document.getElementById("loginModal").classList.add("hidden");
    showToast(`Signed in as ${data.full_name} (${data.role})`);

    await fetchUserProfile();
    await loadPortalData();
  } catch (err) {
    showToast("Network error during login", "error");
  }
}

async function quickLogin(username, password) {
  const quickSwitchDropdown = document.getElementById("quickSwitchDropdown");
  if (quickSwitchDropdown) quickSwitchDropdown.classList.add("hidden");
  await performLogin(username, password);
}

async function fetchUserProfile() {
  const res = await fetch(`${API_BASE}/api/auth/me`, {
    headers: { "Authorization": `Bearer ${currentToken}` }
  });

  if (!res.ok) throw new Error("Invalid token");
  currentUser = await res.json();
  currentRole = currentUser.role;

  // Update Top Navigation
  const userNameElem = document.getElementById("userName");
  const userRoleSubElem = document.getElementById("userRoleSub");
  const userAvatarElem = document.getElementById("userAvatar");
  const roleBadgeElem = document.getElementById("roleBadge");
  const roleBadgeTextElem = document.getElementById("roleBadgeText");

  if (userNameElem) userNameElem.textContent = currentUser.full_name;
  if (userRoleSubElem) userRoleSubElem.textContent = currentUser.username;
  if (userAvatarElem && currentUser.avatar_url) userAvatarElem.src = currentUser.avatar_url;

  if (currentRole === "student") {
    roleBadgeElem.className = "text-xs font-semibold px-2.5 py-1 rounded-md bg-blue-50 text-blue-700 border border-blue-200 flex items-center space-x-1.5";
    roleBadgeTextElem.textContent = "STUDENT PORTAL";
  } else {
    roleBadgeElem.className = "text-xs font-semibold px-2.5 py-1 rounded-md bg-indigo-50 text-indigo-700 border border-indigo-200 flex items-center space-x-1.5";
    roleBadgeTextElem.textContent = "FACULTY PORTAL";
  }
}

// ----------------------------------------------------
// Load Portal View (Student vs Teacher)
// ----------------------------------------------------
async function loadPortalData() {
  const studentView = document.getElementById("studentView");
  const teacherView = document.getElementById("teacherView");

  if (currentRole === "student") {
    studentView.classList.remove("hidden");
    teacherView.classList.add("hidden");
    await loadStudentDashboard();
    await loadSubjectNotes();
  } else {
    studentView.classList.add("hidden");
    teacherView.classList.remove("hidden");
    await loadTeacherDashboard();
    await loadSubjectNotes();
  }

  if (window.lucide) lucide.createIcons();
}

// ----------------------------------------------------
// Student Portal Logic
// ----------------------------------------------------
async function loadStudentDashboard() {
  try {
    const res = await fetch(`${API_BASE}/api/student/dashboard`, {
      headers: { "Authorization": `Bearer ${currentToken}` }
    });
    if (!res.ok) throw new Error("Could not load student dashboard");
    const data = await res.json();
    activeStudentData = data;

    // Header Overview
    document.getElementById("sHeaderName").textContent = `Welcome, ${data.profile.full_name}`;
    document.getElementById("sHeaderSub").textContent = `Roll No: ${data.profile.roll_number} • Semester ${data.profile.semester} • ${data.profile.department}`;
    document.getElementById("sStandingBadge").textContent = data.profile.academic_standing;
    document.getElementById("sGpaScore").innerHTML = `${data.profile.gpa} <span class="text-xs font-normal text-slate-500">/ 10</span>`;
    
    // Overall Attendance
    const attElem = document.getElementById("sOverallAttPct");
    attElem.textContent = `${data.overall_attendance}%`;
    if (data.overall_attendance >= 85) {
      attElem.className = "text-2xl font-extrabold text-emerald-600 font-mono";
      document.getElementById("sAttStatusDesc").textContent = "Safe Attendance (≥85%)";
    } else if (data.overall_attendance >= 75) {
      attElem.className = "text-2xl font-extrabold text-blue-600 font-mono";
      document.getElementById("sAttStatusDesc").textContent = "Eligible (>75%)";
    } else {
      attElem.className = "text-2xl font-extrabold text-amber-600 font-mono";
      document.getElementById("sAttStatusDesc").textContent = "Attendance Shortage (<75%)";
    }

    document.getElementById("sFeedbackCount").textContent = `${data.feedbacks.length} Remarks Posted`;
    document.getElementById("sNotesCountKpi").textContent = `${data.recent_notes_count} Modules Available`;

    // Render Tab 1: Marks Table
    renderStudentMarks(data.marks);

    // Render Tab 2: Attendance Cards
    renderStudentAttendance(data.attendance);

    // Render Tab 3: Feedbacks
    renderStudentFeedback(data.feedbacks);

  } catch (err) {
    console.error(err);
    showToast("Error loading student dashboard", "error");
  }
}

function renderStudentMarks(marks) {
  const tbody = document.getElementById("sMarksTableBody");
  if (!tbody) return;

  tbody.innerHTML = marks.map(m => {
    let gradeBadgeClass = "bg-slate-100 text-slate-700";
    if (m.grade.startsWith("A")) gradeBadgeClass = "bg-emerald-50 text-emerald-700 border border-emerald-200";
    else if (m.grade.startsWith("B")) gradeBadgeClass = "bg-blue-50 text-blue-700 border border-blue-200";
    else if (m.grade.startsWith("C")) gradeBadgeClass = "bg-amber-50 text-amber-700 border border-amber-200";

    return `
      <tr class="hover:bg-slate-50/60 transition">
        <td class="py-3 px-3">
          <p class="font-bold text-slate-900">${m.subject_name}</p>
          <span class="text-2xs text-slate-400 font-mono">${m.subject_code}</span>
        </td>
        <td class="py-3 px-2 text-center font-mono font-medium text-slate-700">${m.midterm_score}</td>
        <td class="py-3 px-2 text-center font-mono font-medium text-slate-700">${m.assignment_score}</td>
        <td class="py-3 px-2 text-center font-mono font-medium text-slate-700">${m.lab_score}</td>
        <td class="py-3 px-2 text-center font-mono font-medium text-slate-700">${m.final_score}</td>
        <td class="py-3 px-2 text-center font-mono font-bold text-slate-900">${m.total_score}</td>
        <td class="py-3 px-3 text-right">
          <span class="px-2 py-0.5 rounded text-xs font-bold font-mono ${gradeBadgeClass}">${m.grade}</span>
        </td>
      </tr>
    `;
  }).join("");
}

function renderStudentAttendance(records) {
  const container = document.getElementById("sAttendanceCardsGrid");
  if (!container) return;

  container.innerHTML = records.map(r => {
    const isSafe = r.percentage >= 75;
    const isHigh = r.percentage >= 85;
    const badgeColor = isHigh 
      ? "bg-emerald-50 text-emerald-700 border-emerald-200" 
      : (isSafe ? "bg-blue-50 text-blue-700 border-blue-200" : "bg-amber-50 text-amber-700 border-amber-200");
    const barColor = isHigh ? "bg-emerald-500" : (isSafe ? "bg-blue-500" : "bg-amber-500");

    return `
      <div class="p-4 rounded-xl border border-slate-200 bg-white shadow-2xs hover:border-slate-300 transition">
        <div class="flex items-start justify-between">
          <div>
            <h4 class="font-bold text-xs text-slate-900">${r.subject_name}</h4>
            <p class="text-2xs text-slate-400 font-mono">${r.subject_code} • Instructor: ${r.instructor_name}</p>
          </div>
          <span class="text-xs font-mono font-bold px-2 py-0.5 rounded border ${badgeColor}">
            ${r.percentage}%
          </span>
        </div>

        <div class="mt-4">
          <div class="flex justify-between text-2xs text-slate-500 mb-1 font-mono">
            <span>Attended: ${r.attended_classes} of ${r.total_classes} sessions</span>
            <span>${isSafe ? 'Eligible' : 'Warning'}</span>
          </div>
          <div class="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
            <div class="${barColor} h-2 rounded-full transition-all duration-500" style="width: ${Math.min(r.percentage, 100)}%"></div>
          </div>
        </div>
      </div>
    `;
  }).join("");
}

function renderStudentFeedback(feedbacks) {
  const container = document.getElementById("sFeedbackTimeline");
  if (!container) return;

  if (feedbacks.length === 0) {
    container.innerHTML = `<p class="text-xs text-slate-400 italic">No feedback remarks posted yet.</p>`;
    return;
  }

  container.innerHTML = feedbacks.map(f => {
    const dateFormatted = new Date(f.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    
    let tagColor = "bg-blue-50 text-blue-700 border-blue-200";
    if (f.behavior_tag.includes("Punctual") || f.behavior_tag.includes("Proactive") || f.behavior_tag.includes("Analytical")) {
      tagColor = "bg-emerald-50 text-emerald-700 border-emerald-200";
    } else if (f.behavior_tag.includes("Attention") || f.behavior_tag.includes("Improvement")) {
      tagColor = "bg-amber-50 text-amber-700 border-amber-200";
    }

    return `
      <div class="p-4 rounded-xl border border-slate-200 bg-white shadow-2xs flex items-start space-x-3.5">
        <div class="w-8 h-8 rounded-lg bg-slate-100 text-slate-700 flex items-center justify-center shrink-0">
          <i data-lucide="message-square" class="w-4 h-4 text-indigo-600"></i>
        </div>
        <div class="flex-1">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-1 mb-1.5">
            <div class="flex items-center space-x-2">
              <span class="font-bold text-xs text-slate-900">${f.teacher_name}</span>
              <span class="text-2xs text-slate-400 font-mono">• ${f.subject}</span>
            </div>
            <span class="text-2xs text-slate-400 font-mono">${dateFormatted}</span>
          </div>

          <div class="flex items-center space-x-2 mb-2">
            <span class="text-2xs px-2 py-0.5 rounded font-mono font-medium bg-slate-100 text-slate-600">${f.category}</span>
            <span class="text-2xs px-2 py-0.5 rounded font-semibold border ${tagColor}">
              ★ ${f.behavior_tag}
            </span>
          </div>

          <p class="text-xs text-slate-700 leading-relaxed bg-slate-50/70 p-3 rounded-lg border border-slate-100">
            "${f.feedback_text}"
          </p>
        </div>
      </div>
    `;
  }).join("");

  if (window.lucide) lucide.createIcons();
}

function switchStudentTab(tabName) {
  const tabs = ['progress', 'attendance', 'feedback', 'notes'];
  tabs.forEach(t => {
    const content = document.getElementById(`studentTab-${t}`);
    const btn = document.getElementById(`tabBtn-${t}`);
    if (content) content.classList.add("hidden");
    if (btn) {
      btn.classList.remove("active", "text-slate-900", "border-b-2", "border-slate-900", "font-semibold");
      btn.classList.add("text-slate-500");
    }
  });

  const activeContent = document.getElementById(`studentTab-${tabName}`);
  const activeBtn = document.getElementById(`tabBtn-${tabName}`);
  if (activeContent) activeContent.classList.remove("hidden");
  if (activeBtn) {
    activeBtn.classList.add("active", "text-slate-900", "border-b-2", "border-slate-900", "font-semibold");
    activeBtn.classList.remove("text-slate-500");
  }

  if (tabName === 'notes') {
    loadSubjectNotes();
  }

  if (window.lucide) lucide.createIcons();
}

// ----------------------------------------------------
// Subject Notes Hub (MLOps & Deep Learning)
// ----------------------------------------------------
let activeNoteFilter = "all";
let noteSearchQuery = "";

async function loadSubjectNotes() {
  try {
    let url = `${API_BASE}/api/notes`;
    const res = await fetch(url, {
      headers: { "Authorization": `Bearer ${currentToken}` }
    });
    if (!res.ok) throw new Error("Could not fetch notes");
    allSubjectNotes = await res.json();
    renderNotesGrid();
    if (currentRole === "teacher") {
      renderTeacherNotesList();
    }
  } catch (err) {
    console.error(err);
  }
}

function filterNotes(subject) {
  activeNoteFilter = subject;
  document.querySelectorAll(".note-filter-btn").forEach(btn => {
    btn.classList.remove("active", "bg-slate-900", "text-white");
    btn.classList.add("bg-slate-100", "text-slate-700");
  });

  const btnId = subject === "all" ? "filterBtn-all" : (subject.includes("MLOps") ? "filterBtn-MLOps" : "filterBtn-DeepLearning");
  const targetBtn = document.getElementById(btnId);
  if (targetBtn) {
    targetBtn.classList.add("active", "bg-slate-900", "text-white");
    targetBtn.classList.remove("bg-slate-100", "text-slate-700");
  }

  renderNotesGrid();
}

function searchNotes(query) {
  noteSearchQuery = query.toLowerCase().trim();
  renderNotesGrid();
}

function renderNotesGrid() {
  const container = document.getElementById("notesGrid");
  if (!container) return;

  let filtered = allSubjectNotes;
  if (activeNoteFilter !== "all") {
    filtered = filtered.filter(n => n.subject_name.toLowerCase().includes(activeNoteFilter.toLowerCase()));
  }

  if (noteSearchQuery) {
    filtered = filtered.filter(n =>
      n.title.toLowerCase().includes(noteSearchQuery) ||
      n.summary.toLowerCase().includes(noteSearchQuery) ||
      n.tags.toLowerCase().includes(noteSearchQuery) ||
      n.unit.toLowerCase().includes(noteSearchQuery)
    );
  }

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="col-span-3 text-center py-12 bg-white rounded-xl border border-slate-200">
        <i data-lucide="book-open" class="w-8 h-8 text-slate-300 mx-auto mb-2"></i>
        <p class="text-xs text-slate-500">No subject notes match your search or filter.</p>
      </div>
    `;
    if (window.lucide) lucide.createIcons();
    return;
  }

  container.innerHTML = filtered.map(n => {
    const isMlops = n.subject_name.toLowerCase().includes("mlops");
    const subjectBadge = isMlops
      ? "bg-indigo-50 text-indigo-700 border-indigo-200"
      : "bg-blue-50 text-blue-700 border-blue-200";

    const tagsList = n.tags ? n.tags.split(",").map(t => `<span class="text-3xs px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 font-mono">${t.trim()}</span>`).join(" ") : "";

    return `
      <div class="bg-white rounded-xl border border-slate-200/80 p-5 shadow-2xs hover:shadow-sm hover:border-slate-300 transition flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-2.5">
            <span class="text-2xs font-mono font-bold px-2 py-0.5 rounded border ${subjectBadge}">${n.subject_name}</span>
            <span class="text-2xs text-slate-400 font-mono">${n.unit}</span>
          </div>

          <h4 class="font-bold text-xs text-slate-900 leading-snug mb-2">${n.title}</h4>
          <p class="text-xs text-slate-600 line-clamp-3 leading-relaxed mb-3">${n.summary}</p>
          
          <div class="flex flex-wrap gap-1 mb-4">
            ${tagsList}
          </div>
        </div>

        <div class="pt-3 border-t border-slate-100 flex items-center justify-between text-2xs">
          <span class="text-slate-400">${n.author_name}</span>
          <button onclick="openNoteModal(${n.id})" class="font-bold text-indigo-600 hover:text-indigo-800 flex items-center space-x-1">
            <span>Read Module</span>
            <i data-lucide="arrow-right" class="w-3 h-3"></i>
          </button>
        </div>
      </div>
    `;
  }).join("");

  if (window.lucide) lucide.createIcons();
}

function openNoteModal(noteId) {
  const note = allSubjectNotes.find(n => n.id === noteId);
  if (!note) return;

  document.getElementById("noteModalSubjectBadge").textContent = note.subject_name;
  document.getElementById("noteModalTitle").textContent = `${note.unit}: ${note.title}`;
  document.getElementById("noteModalAuthor").textContent = `Published by: ${note.author_name}`;
  
  const contentElem = document.getElementById("noteModalContent");
  if (window.marked) {
    contentElem.innerHTML = marked.parse(note.content_markdown);
  } else {
    contentElem.textContent = note.content_markdown;
  }

  const resLink = document.getElementById("noteModalResourceLink");
  if (note.resource_url) {
    resLink.href = note.resource_url;
    resLink.classList.remove("hidden");
  } else {
    resLink.classList.add("hidden");
  }

  document.getElementById("viewNoteModal").classList.remove("hidden");
}

function closeNoteModal() {
  document.getElementById("viewNoteModal").classList.add("hidden");
}

// ----------------------------------------------------
// Teacher Portal Logic
// ----------------------------------------------------
async function loadTeacherDashboard() {
  try {
    const res = await fetch(`${API_BASE}/api/teacher/students`, {
      headers: { "Authorization": `Bearer ${currentToken}` }
    });
    if (!res.ok) throw new Error("Could not load students list");
    activeTeacherStudents = await res.json();

    // KPIs
    document.getElementById("tTotalStudents").textContent = activeTeacherStudents.length;
    const avg = activeTeacherStudents.reduce((acc, s) => acc + s.overall_attendance, 0) / (activeTeacherStudents.length || 1);
    document.getElementById("tAvgAtt").textContent = `${avg.toFixed(1)}%`;
    
    const honors = activeTeacherStudents.filter(s => s.gpa >= 9.0).length;
    document.getElementById("tHonorsCount").textContent = honors;

    const warnings = activeTeacherStudents.filter(s => s.overall_attendance < 75).length;
    document.getElementById("tWarningCount").textContent = warnings;

    renderTeacherRoster(activeTeacherStudents);
  } catch (err) {
    console.error(err);
    showToast("Error loading faculty dashboard", "error");
  }
}

function renderTeacherRoster(students) {
  const tbody = document.getElementById("tRosterTableBody");
  if (!tbody) return;

  tbody.innerHTML = students.map(s => {
    const isWarning = s.overall_attendance < 75;
    const attBadge = isWarning
      ? "bg-amber-50 text-amber-700 border border-amber-200"
      : "bg-emerald-50 text-emerald-700 border border-emerald-200";

    return `
      <tr class="hover:bg-slate-50/70 transition">
        <td class="py-3 px-3">
          <p class="font-bold text-slate-900">${s.full_name}</p>
          <span class="text-2xs text-slate-400 font-mono">${s.roll_number} • ${s.email}</span>
        </td>
        <td class="py-3 px-3 text-slate-600">${s.department}</td>
        <td class="py-3 px-3 text-center font-mono font-medium">${s.semester}</td>
        <td class="py-3 px-3 text-center">
          <span class="px-2 py-0.5 rounded text-xs font-mono font-bold ${attBadge}">
            ${s.overall_attendance}%
          </span>
        </td>
        <td class="py-3 px-3 text-center font-mono font-bold text-slate-900">${s.gpa}</td>
        <td class="py-3 px-3">
          <span class="text-2xs font-semibold ${s.academic_standing.includes('Warning') ? 'text-amber-600' : 'text-slate-700'}">
            ${s.academic_standing}
          </span>
        </td>
        <td class="py-3 px-3 text-right">
          <button onclick="openEditStudentModal(${s.id})" class="px-2.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-medium text-xs shadow-2xs transition">
            Manage Details &rarr;
          </button>
        </td>
      </tr>
    `;
  }).join("");
}

function filterRoster(query) {
  const q = query.toLowerCase().trim();
  const filtered = activeTeacherStudents.filter(s =>
    s.full_name.toLowerCase().includes(q) ||
    s.roll_number.toLowerCase().includes(q)
  );
  renderTeacherRoster(filtered);
}

function filterRosterSelect(val) {
  if (val === "all") {
    renderTeacherRoster(activeTeacherStudents);
  } else if (val === "warning") {
    renderTeacherRoster(activeTeacherStudents.filter(s => s.overall_attendance < 75));
  } else if (val === "honors") {
    renderTeacherRoster(activeTeacherStudents.filter(s => s.gpa >= 9.0));
  }
}

// ----------------------------------------------------
// Teacher: Student Edit Modal Logic
// ----------------------------------------------------
async function openEditStudentModal(studentId) {
  try {
    const res = await fetch(`${API_BASE}/api/teacher/students/${studentId}`, {
      headers: { "Authorization": `Bearer ${currentToken}` }
    });
    if (!res.ok) throw new Error("Could not load student details");
    selectedStudentForEdit = await res.json();

    const p = selectedStudentForEdit.profile;
    document.getElementById("modalStudentName").textContent = p.full_name;
    document.getElementById("modalStudentRoll").textContent = `${p.roll_number} • Semester ${p.semester} • GPA ${p.gpa}`;
    document.getElementById("modalStudentAvatarInitial").textContent = p.full_name.split(" ").map(n => n[0]).join("");

    renderModalAttendance();
    renderModalMarks();
    renderModalFeedbacks();

    switchModalTab('attendance');
    document.getElementById("editStudentModal").classList.remove("hidden");
    if (window.lucide) lucide.createIcons();
  } catch (err) {
    showToast("Error loading student details", "error");
  }
}

function closeEditModal() {
  document.getElementById("editStudentModal").classList.add("hidden");
  // Refresh teacher dashboard to reflect latest marks/attendance/GPA
  loadTeacherDashboard();
}

function switchModalTab(tabName) {
  ['attendance', 'marks', 'feedback'].forEach(t => {
    document.getElementById(`modalSubTab-${t}`).classList.add("hidden");
    const btn = document.getElementById(`modalTabBtn-${t}`);
    btn.classList.remove("active", "border-b-2", "border-slate-900", "text-slate-900");
    btn.classList.add("text-slate-500");
  });

  document.getElementById(`modalSubTab-${tabName}`).classList.remove("hidden");
  const activeBtn = document.getElementById(`modalTabBtn-${tabName}`);
  activeBtn.classList.add("active", "border-b-2", "border-slate-900", "text-slate-900");
  activeBtn.classList.remove("text-slate-500");
}

function renderModalAttendance() {
  const container = document.getElementById("modalAttendanceList");
  if (!container || !selectedStudentForEdit) return;

  container.innerHTML = selectedStudentForEdit.attendance.map(a => `
    <div class="p-3.5 bg-slate-50 border border-slate-200 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div>
        <h5 class="text-xs font-bold text-slate-900">${a.subject_name}</h5>
        <span class="text-2xs text-slate-400 font-mono">${a.subject_code}</span>
      </div>

      <div class="flex items-center space-x-3">
        <div class="flex items-center space-x-1.5 text-xs">
          <label class="text-2xs text-slate-500 font-medium">Attended:</label>
          <input type="number" id="att_attended_${a.subject_id}" value="${a.attended_classes}" min="0" class="w-16 px-2 py-1 text-xs border border-slate-300 rounded font-mono text-center">
        </div>
        <div class="flex items-center space-x-1.5 text-xs">
          <label class="text-2xs text-slate-500 font-medium">Total:</label>
          <input type="number" id="att_total_${a.subject_id}" value="${a.total_classes}" min="1" class="w-16 px-2 py-1 text-xs border border-slate-300 rounded font-mono text-center">
        </div>
        <button onclick="saveAttendance(${a.subject_id})" class="px-3 py-1 bg-slate-900 hover:bg-slate-800 text-white rounded text-xs font-medium transition">
          Update
        </button>
      </div>
    </div>
  `).join("");
}

async function saveAttendance(subjectId) {
  const attended = parseInt(document.getElementById(`att_attended_${subjectId}`).value);
  const total = parseInt(document.getElementById(`att_total_${subjectId}`).value);

  if (isNaN(attended) || isNaN(total) || total <= 0 || attended > total) {
    showToast("Invalid attendance values", "error");
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/api/teacher/students/${selectedStudentForEdit.profile.id}/attendance/${subjectId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${currentToken}`
      },
      body: JSON.stringify({ attended_classes: attended, total_classes: total })
    });

    if (!res.ok) throw new Error("Update failed");
    const updated = await res.json();
    showToast(`Attendance updated: ${updated.percentage}%`);
  } catch (err) {
    showToast("Could not save attendance", "error");
  }
}

function renderModalMarks() {
  const container = document.getElementById("modalMarksList");
  if (!container || !selectedStudentForEdit) return;

  container.innerHTML = selectedStudentForEdit.marks.map(m => `
    <div class="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
      <div class="flex items-center justify-between">
        <div>
          <h5 class="text-xs font-bold text-slate-900">${m.subject_name}</h5>
          <span class="text-2xs text-slate-400 font-mono">${m.subject_code}</span>
        </div>
        <div class="text-right">
          <span class="text-2xs font-mono font-bold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200" id="gradeBadge_${m.subject_id}">
            Total: ${m.total_score} (${m.grade})
          </span>
        </div>
      </div>

      <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
        <div>
          <label class="block text-2xs font-semibold text-slate-600 mb-0.5">Midterm (Max 30)</label>
          <input type="number" step="0.5" id="mark_mid_${m.subject_id}" value="${m.midterm_score}" max="30" class="w-full px-2 py-1 text-xs border border-slate-300 rounded font-mono">
        </div>
        <div>
          <label class="block text-2xs font-semibold text-slate-600 mb-0.5">Assign (Max 20)</label>
          <input type="number" step="0.5" id="mark_assign_${m.subject_id}" value="${m.assignment_score}" max="20" class="w-full px-2 py-1 text-xs border border-slate-300 rounded font-mono">
        </div>
        <div>
          <label class="block text-2xs font-semibold text-slate-600 mb-0.5">Lab (Max 20)</label>
          <input type="number" step="0.5" id="mark_lab_${m.subject_id}" value="${m.lab_score}" max="20" class="w-full px-2 py-1 text-xs border border-slate-300 rounded font-mono">
        </div>
        <div>
          <label class="block text-2xs font-semibold text-slate-600 mb-0.5">Final (Max 30)</label>
          <input type="number" step="0.5" id="mark_final_${m.subject_id}" value="${m.final_score}" max="30" class="w-full px-2 py-1 text-xs border border-slate-300 rounded font-mono">
        </div>
      </div>

      <div class="text-right pt-2 border-t border-slate-200">
        <button onclick="saveMarks(${m.subject_id})" class="px-3.5 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded text-xs font-semibold transition">
          Save Marks
        </button>
      </div>
    </div>
  `).join("");
}

async function saveMarks(subjectId) {
  const midterm = parseFloat(document.getElementById(`mark_mid_${subjectId}`).value) || 0;
  const assign = parseFloat(document.getElementById(`mark_assign_${subjectId}`).value) || 0;
  const lab = parseFloat(document.getElementById(`mark_lab_${subjectId}`).value) || 0;
  const finalScore = parseFloat(document.getElementById(`mark_final_${subjectId}`).value) || 0;

  try {
    const res = await fetch(`${API_BASE}/api/teacher/students/${selectedStudentForEdit.profile.id}/marks/${subjectId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${currentToken}`
      },
      body: JSON.stringify({
        midterm_score: midterm,
        assignment_score: assign,
        lab_score: lab,
        final_score: finalScore
      })
    });

    if (!res.ok) throw new Error("Could not update marks");
    const updated = await res.json();
    document.getElementById(`gradeBadge_${subjectId}`).textContent = `Total: ${updated.total_score} (${updated.grade})`;
    showToast(`Marks updated: Total ${updated.total_score} (${updated.grade})`);
  } catch (err) {
    showToast("Error updating marks", "error");
  }
}

function renderModalFeedbacks() {
  const container = document.getElementById("modalExistingFeedback");
  if (!container || !selectedStudentForEdit) return;

  if (selectedStudentForEdit.feedbacks.length === 0) {
    container.innerHTML = `<p class="text-2xs text-slate-400 italic">No previous remarks posted for this student.</p>`;
    return;
  }

  container.innerHTML = selectedStudentForEdit.feedbacks.map(f => `
    <div class="p-3 bg-white border border-slate-200 rounded-lg flex items-start justify-between">
      <div>
        <div class="flex items-center space-x-2 mb-1">
          <span class="text-2xs font-bold text-slate-800">${f.teacher_name}</span>
          <span class="text-3xs text-slate-400 font-mono">• ${f.subject}</span>
          <span class="text-3xs px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-700 font-mono font-medium">${f.category}</span>
        </div>
        <p class="text-xs text-slate-700 leading-snug">"${f.feedback_text}"</p>
        <span class="inline-block mt-1 text-3xs font-semibold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
          Tag: ${f.behavior_tag}
        </span>
      </div>
      <button onclick="deleteFeedbackItem(${f.id})" class="text-slate-400 hover:text-red-500 p-1">
        <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
      </button>
    </div>
  `).join("");

  if (window.lucide) lucide.createIcons();
}

async function submitFeedback(event) {
  event.preventDefault();
  if (!selectedStudentForEdit) return;

  const subject = document.getElementById("fbSubject").value;
  const category = document.getElementById("fbCategory").value;
  const behavior_tag = document.getElementById("fbTag").value.trim();
  const feedback_text = document.getElementById("fbText").value.trim();

  try {
    const res = await fetch(`${API_BASE}/api/teacher/students/${selectedStudentForEdit.profile.id}/feedback`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${currentToken}`
      },
      body: JSON.stringify({ subject, category, behavior_tag, feedback_text })
    });

    if (!res.ok) throw new Error("Could not submit feedback");
    const created = await res.json();
    selectedStudentForEdit.feedbacks.unshift(created);
    renderModalFeedbacks();
    document.getElementById("fbText").value = "";
    showToast("Feedback & behavioral observation saved!");
  } catch (err) {
    showToast("Error adding feedback", "error");
  }
}

async function deleteFeedbackItem(feedbackId) {
  try {
    const res = await fetch(`${API_BASE}/api/teacher/feedbacks/${feedbackId}`, {
      method: "DELETE",
      headers: { "Authorization": `Bearer ${currentToken}` }
    });
    if (!res.ok) throw new Error("Delete failed");
    selectedStudentForEdit.feedbacks = selectedStudentForEdit.feedbacks.filter(f => f.id !== feedbackId);
    renderModalFeedbacks();
    showToast("Remark removed");
  } catch (err) {
    showToast("Could not remove remark", "error");
  }
}

// ----------------------------------------------------
// Teacher: Subject Notes Management
// ----------------------------------------------------
function renderTeacherNotesList() {
  const container = document.getElementById("tNotesList");
  if (!container) return;

  container.innerHTML = allSubjectNotes.map(n => `
    <div class="py-3 flex items-center justify-between text-xs">
      <div>
        <div class="flex items-center space-x-2">
          <span class="font-bold text-slate-900">${n.title}</span>
          <span class="text-2xs font-mono px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">${n.subject_name}</span>
          <span class="text-2xs text-slate-400 font-mono">${n.unit}</span>
        </div>
        <p class="text-2xs text-slate-500 mt-0.5 line-clamp-1">${n.summary}</p>
      </div>
      <div class="flex items-center space-x-2">
        <button onclick="openNoteModal(${n.id})" class="text-xs text-indigo-600 hover:underline">View</button>
        <button onclick="deleteNote(${n.id})" class="text-xs text-red-500 hover:text-red-700 ml-2">Delete</button>
      </div>
    </div>
  `).join("");
}

function openPublishNoteModal() {
  document.getElementById("publishNoteModal").classList.remove("hidden");
}

function closePublishNoteModal() {
  document.getElementById("publishNoteModal").classList.add("hidden");
}

async function submitNewNote(e) {
  e.preventDefault();
  const subject_name = document.getElementById("newNoteSubject").value;
  const unit = document.getElementById("newNoteUnit").value.trim();
  const title = document.getElementById("newNoteTitle").value.trim();
  const summary = document.getElementById("newNoteSummary").value.trim();
  const content_markdown = document.getElementById("newNoteContent").value.trim();
  const tags = document.getElementById("newNoteTags").value.trim();
  const resource_url = document.getElementById("newNoteResource").value.trim();

  try {
    const res = await fetch(`${API_BASE}/api/notes`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${currentToken}`
      },
      body: JSON.stringify({
        subject_name,
        unit,
        title,
        summary,
        content_markdown,
        tags,
        resource_url: resource_url || null
      })
    });

    if (!res.ok) throw new Error("Could not publish note");
    showToast("Subject note published successfully!");
    closePublishNoteModal();
    document.getElementById("publishNoteForm").reset();
    await loadSubjectNotes();
  } catch (err) {
    showToast("Error publishing note", "error");
  }
}

async function deleteNote(noteId) {
  if (!confirm("Are you sure you want to delete this study note?")) return;
  try {
    const res = await fetch(`${API_BASE}/api/notes/${noteId}`, {
      method: "DELETE",
      headers: { "Authorization": `Bearer ${currentToken}` }
    });
    if (!res.ok) throw new Error("Delete failed");
    showToast("Note deleted");
    await loadSubjectNotes();
  } catch (err) {
    showToast("Error deleting note", "error");
  }
}

// ----------------------------------------------------
// Toast Notification
// ----------------------------------------------------
function showToast(message, type = "success") {
  const toast = document.getElementById("toast");
  const msg = document.getElementById("toastMsg");
  const icon = document.getElementById("toastIcon");

  if (!toast || !msg) return;

  msg.textContent = message;
  toast.classList.remove("hidden");

  setTimeout(() => {
    toast.classList.add("hidden");
  }, 3500);
}


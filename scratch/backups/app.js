// Global App State
let state = {
  employees: [],
  tasks: [],
  assignments: [],
  submissions: [],
  theme: 'dark'
};

// Initial Mock Data (Used if LocalStorage is empty)
const initialEmployees = [
  { id: 'emp-1', name: 'Sarah Connor', role: 'Lead DevOps Architect', score: 9.6, experience: 8, skills: ['Docker', 'AWS', 'Kubernetes', 'Python'] },
  { id: 'emp-2', name: 'Marcus Wright', role: 'Senior Backend Engineer', score: 8.8, experience: 6, skills: ['Python', 'SQL', 'Django', 'API'] },
  { id: 'emp-3', name: 'Kyle Reese', role: 'Frontend Developer', score: 8.2, experience: 4, skills: ['JavaScript', 'CSS', 'React', 'HTML'] },
  { id: 'emp-4', name: 'John Connor', role: 'Machine Learning Specialist', score: 9.4, experience: 5, skills: ['Python', 'PyTorch', 'SQL', 'Math'] },
  { id: 'emp-5', name: 'Kate Brewster', role: 'QA Automation Engineer', score: 7.9, experience: 3, skills: ['Python', 'Selenium', 'CSS', 'JavaScript'] },
  { id: 'emp-6', name: 'Grace Harper', role: 'Database Administrator', score: 8.5, experience: 7, skills: ['SQL', 'Postgres', 'AWS', 'Optimization'] }
];

const initialTasks = [
  { id: 'task-1', title: 'Deploy Kubernetes Cluster', desc: 'Set up multi-region high-availability EKS cluster for staging environment.', priority: 'High', skill: 'Kubernetes', deadline: '2026-06-15', status: 'In-Progress' },
  { id: 'task-2', title: 'Optimize SQL Query Performance', desc: 'Profile and index main reporting tables to reduce load time under 200ms.', priority: 'High', skill: 'SQL', deadline: '2026-06-12', status: 'Pending' },
  { id: 'task-3', title: 'Implement CSS Glassmorphism UI', desc: 'Create a modern, clean visual look with blurred backdrops and custom scrollbars.', priority: 'Medium', skill: 'CSS', deadline: '2026-06-18', status: 'Pending' },
  { id: 'task-4', title: 'Refactor Django Authentication Rest API', desc: 'Migrate old session endpoints to secure JWT and OAuth2 integration.', priority: 'High', skill: 'API', deadline: '2026-06-10', status: 'In-Progress' },
  { id: 'task-5', title: 'Build React Dashboard Widgets', desc: 'Implement interactive SVG charts for the executive operations board.', priority: 'Medium', skill: 'React', deadline: '2026-06-20', status: 'Completed' },
  { id: 'task-6', title: 'Configure Selenium Smoke Tests', desc: 'Automate user checkout flow verification on mobile and desktop viewports.', priority: 'Low', skill: 'Selenium', deadline: '2026-06-25', status: 'Pending' }
];

const initialAssignments = [
  { employeeId: 'emp-1', taskId: 'task-1', assignedDate: '2026-06-05' },
  { employeeId: 'emp-2', taskId: 'task-4', assignedDate: '2026-06-04' }
];

const initialSubmissions = [
  { id: 'sub-1', taskTitle: 'Build React Dashboard Widgets', employeeName: 'Kyle Reese', fileName: 'dashboard-widgets-react.zip', date: '2026-06-06 14:30', status: 'Approved' }
];

// Chart Instances Global Object
const charts = {
  performance: null,
  completion: null,
  efficiency: null,
  priority: null,
  trends: null,
  efficiencyComparison: null
};

// --- CORE SYSTEM INITS ---
document.addEventListener('DOMContentLoaded', () => {
  initAppState();
  setupEventListeners();
  fetchStateAndRefresh().then(() => {
    switchTab('dashboard'); // Default view
  });
});

async function fetchStateAndRefresh() {
  try {
    const response = await fetch('/api/state');
    if (!response.ok) throw new Error('Failed to fetch state');
    const newState = await response.json();
    state.employees = newState.employees;
    state.tasks = newState.tasks;
    state.assignments = newState.assignments;
    state.submissions = newState.submissions;
    updateAllViews();
  } catch (error) {
    console.error('Error fetching state:', error);
    showToast('Failed to sync with database', 'error');
  }
}

// Load theme state from LocalStorage
function initAppState() {
  const storedTheme = localStorage.getItem('optima_assign_theme') || 'dark';
  state.theme = storedTheme;
  
  // Apply initial theme
  document.documentElement.setAttribute('data-theme', state.theme);
  const themeIconSun = document.getElementById('themeIconSun');
  const themeIconMoon = document.getElementById('themeIconMoon');
  if (state.theme === 'light') {
    themeIconSun.style.display = 'block';
    themeIconMoon.style.display = 'none';
  } else {
    themeIconSun.style.display = 'none';
    themeIconMoon.style.display = 'block';
  }
}

function saveThemeState() {
  localStorage.setItem('optima_assign_theme', state.theme);
}

// --- EVENT LISTENERS CONFIG ---
function setupEventListeners() {
  // Sidebar tab routing
  const sidebarLinks = document.querySelectorAll('.menu-item-link');
  sidebarLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const targetSection = link.getAttribute('data-section');
      
      sidebarLinks.forEach(l => l.classList.remove('active'));
      link.classList.add('active');
      
      switchTab(targetSection);
      
      // Close sidebar on mobile
      document.getElementById('sidebar').classList.remove('active');
    });
  });

  // Mobile drawer toggle
  document.getElementById('sidebarToggle').addEventListener('click', () => {
    document.getElementById('sidebar').classList.toggle('active');
  });

  // Global search input keyup
  document.getElementById('globalSearch').addEventListener('input', (e) => {
    filterData(e.target.value.toLowerCase());
  });
  // Dark/Light theme toggler
  document.getElementById('themeToggle').addEventListener('click', () => {
    state.theme = state.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', state.theme);
    
    const themeIconSun = document.getElementById('themeIconSun');
    const themeIconMoon = document.getElementById('themeIconMoon');
    
    if (state.theme === 'light') {
      themeIconSun.style.display = 'block';
      themeIconMoon.style.display = 'none';
      showToast('Switched to Light Theme', 'success');
    } else {
      themeIconSun.style.display = 'none';
      themeIconMoon.style.display = 'block';
      showToast('Switched to Dark Theme', 'success');
    }
    saveThemeState();
    
    // Re-draw charts to apply correct text/grid colors for the theme
    setTimeout(initCharts, 100);
  });

  // Modals management
  setupModal('employeeModalOverlay', 'openEmployeeModal', 'closeEmployeeModal', 'cancelEmployeeBtn');
  setupModal('taskModalOverlay', 'openTaskModal', 'closeTaskModal', 'cancelTaskBtn');

  // Add Employee form submit
  document.getElementById('addEmployeeForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const name = document.getElementById('empName').value;
    const role = document.getElementById('empRole').value;
    const score = parseFloat(document.getElementById('empScore').value);
    const experience = parseInt(document.getElementById('empExperience').value);
    const skillsText = document.getElementById('empSkills').value;
    
    const skills = skillsText.split(',').map(s => s.trim()).filter(s => s.length > 0);
    
    const newEmployee = {
      name,
      role,
      score,
      experience,
      skills
    };
    
    fetch('/api/add_employee', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(newEmployee)
    })
    .then(response => {
      if (!response.ok) throw new Error('Failed to add employee');
      return fetchStateAndRefresh();
    })
    .then(() => {
      closeModal('employeeModalOverlay');
      document.getElementById('addEmployeeForm').reset();
      showToast(`Added new employee: ${name}`, 'success');
    })
    .catch(err => {
      console.error(err);
      showToast('Failed to add employee to database', 'error');
    });
  });

  // Add Task form submit
  document.getElementById('addTaskForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const title = document.getElementById('taskTitle').value;
    const desc = document.getElementById('taskDesc').value;
    const priority = document.getElementById('taskPriority').value;
    const deadline = document.getElementById('taskDeadline').value;
    const skill = document.getElementById('taskSkill').value.trim();
    
    const newTask = {
      title,
      desc,
      priority,
      deadline,
      skill
    };
    
    fetch('/api/add_task', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(newTask)
    })
    .then(response => {
      if (!response.ok) throw new Error('Failed to create task');
      return fetchStateAndRefresh();
    })
    .then(() => {
      closeModal('taskModalOverlay');
      document.getElementById('addTaskForm').reset();
      showToast(`Created new task: ${title}`, 'success');
    })
    .catch(err => {
      console.error(err);
      showToast('Failed to create task in database', 'error');
    });
  });
  // --- SUBMISSION PORTAL TRIGGERS ---
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('fileInput');
  const selectedFilePanel = document.getElementById('selectedFilePanel');
  const selectedFileName = document.getElementById('selectedFileName');
  const selectedFileSize = document.getElementById('selectedFileSize');
  const removeFileBtn = document.getElementById('removeFileBtn');
  const submitWorkBtn = document.getElementById('submitWorkBtn');
  const submitTaskSelect = document.getElementById('submitTaskSelect');
  let chosenFile = null;

  dropzone.addEventListener('click', () => fileInput.click());

  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });

  dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('dragover');
  });

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      handleFileSelection(e.target.files[0]);
    }
  });

  function handleFileSelection(file) {
    chosenFile = file;
    selectedFileName.textContent = file.name;
    selectedFileSize.textContent = formatBytes(file.size);
    dropzone.style.display = 'none';
    selectedFilePanel.style.display = 'flex';
    validateSubmissionButton();
  }

  removeFileBtn.addEventListener('click', () => {
    clearUploadState();
  });

  submitTaskSelect.addEventListener('change', () => {
    validateSubmissionButton();
  });

  function validateSubmissionButton() {
    submitWorkBtn.disabled = !(chosenFile && submitTaskSelect.value);
  }

  function clearUploadState() {
    chosenFile = null;
    fileInput.value = '';
    dropzone.style.display = 'flex';
    selectedFilePanel.style.display = 'none';
    document.getElementById('uploadProgressContainer').style.display = 'none';
    submitWorkBtn.disabled = true;
  }
  submitWorkBtn.addEventListener('click', () => {
    if (!chosenFile || !submitTaskSelect.value) return;

    submitWorkBtn.disabled = true;
    const uploadProgressContainer = document.getElementById('uploadProgressContainer');
    const progressBarFill = document.getElementById('progressBarFill');
    const progressPercent = document.getElementById('progressPercent');
    const progressText = document.getElementById('progressText');

    uploadProgressContainer.style.display = 'block';
    let percent = 0;
    let uploadComplete = false;
    
    const interval = setInterval(() => {
      if (percent < 90) {
        percent += 10;
        progressBarFill.style.width = percent + '%';
        progressPercent.textContent = percent + '%';
      } else if (uploadComplete) {
        percent = 100;
        progressBarFill.style.width = '100%';
        progressPercent.textContent = '100%';
        clearInterval(interval);
      }
    }, 100);

    const formData = new FormData();
    formData.append('task_id', submitTaskSelect.value);
    formData.append('file', chosenFile);

    fetch('/submit_work?format=json', {
      method: 'POST',
      body: formData
    })
    .then(async (response) => {
      if (!response.ok) throw new Error('Submission failed');
      uploadComplete = true;
      
      // Wait a moment for progress bar to hit 100%
      setTimeout(async () => {
        const taskId = submitTaskSelect.value;
        const task = state.tasks.find(t => t.id === taskId);
        const title = task ? task.title : 'Task';
        
        await fetchStateAndRefresh();
        clearUploadState();
        showToast(`Deliverable successfully submitted for "${title}"`, 'success');
      }, 300);
    })
    .catch((err) => {
      clearInterval(interval);
      console.error(err);
      showToast('Failed to submit work', 'error');
      submitWorkBtn.disabled = false;
    });
  });
}

// --- HELPER FUNCTIONS ---
function setupModal(overlayId, triggerId, closeId, cancelId) {
  const overlay = document.getElementById(overlayId);
  const trigger = document.getElementById(triggerId);
  const close = document.getElementById(closeId);
  const cancel = document.getElementById(cancelId);

  trigger.addEventListener('click', () => overlay.classList.add('active'));
  close.addEventListener('click', () => overlay.classList.remove('active'));
  cancel.addEventListener('click', () => overlay.classList.remove('active'));
}

function closeModal(overlayId) {
  document.getElementById(overlayId).classList.remove('active');
}

function switchTab(sectionName) {
  const sections = document.querySelectorAll('.view-section');
  sections.forEach(sec => sec.classList.remove('active'));
  
  const activeSection = document.getElementById(`section-${sectionName}`);
  if (activeSection) {
    activeSection.classList.add('active');
  }

  // Sync menu state if triggered via outside clicks
  const sidebarLinks = document.querySelectorAll('.menu-item-link');
  sidebarLinks.forEach(link => {
    if (link.getAttribute('data-section') === sectionName) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });
}

function formatBytes(bytes, decimals = 2) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// Global search filters
function filterData(query) {
  // Simple filter overlays
  const employeeCards = document.querySelectorAll('.profile-card');
  employeeCards.forEach(card => {
    const name = card.querySelector('h3').textContent.toLowerCase();
    const role = card.querySelector('p').textContent.toLowerCase();
    const skills = Array.from(card.querySelectorAll('.skill-tag')).map(t => t.textContent.toLowerCase());
    
    const matches = name.includes(query) || role.includes(query) || skills.some(s => s.includes(query));
    card.style.display = matches ? 'flex' : 'none';
  });

  const taskCards = document.querySelectorAll('.task-card');
  taskCards.forEach(card => {
    const title = card.querySelector('h3').textContent.toLowerCase();
    const desc = card.querySelector('.task-desc').textContent.toLowerCase();
    const skill = card.querySelector('.task-meta-item span:last-child').textContent.toLowerCase();
    
    const matches = title.includes(query) || desc.includes(query) || skill.includes(query);
    card.style.display = matches ? 'block' : 'none';
  });

  const tableRows = document.querySelectorAll('#assignmentsTableBody tr');
  tableRows.forEach(row => {
    const textContent = row.textContent.toLowerCase();
    row.style.display = textContent.includes(query) ? 'table-row' : 'none';
  });
}

// Toast Notifications System
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  
  let icon = 'fa-circle-info';
  if (type === 'success') icon = 'fa-circle-check';
  if (type === 'error') icon = 'fa-circle-xmark';
  if (type === 'warning') icon = 'fa-triangle-exclamation';

  toast.innerHTML = `
    <i class="fa-solid ${icon} toast-icon"></i>
    <div class="toast-message">${message}</div>
  `;
  
  container.appendChild(toast);
  
  // Trigger transition
  setTimeout(() => toast.classList.add('show'), 50);
  
  // Remove after delay
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 400);
  }, 4000);
}

// --- OPTIMIZATION ALGORITHM (Engine) ---
function triggerOptimization() {
  const uncompletedTasks = state.tasks.filter(t => t.status !== 'Completed');
  if (uncompletedTasks.length === 0) {
    showToast('All tasks are already completed!', 'warning');
    return;
  }

  showToast('Evaluating performance indexes & skill alignment...', 'info');
  
  setTimeout(() => {
    fetch('/run_optimization?format=json')
      .then(response => {
        if (!response.ok) throw new Error('Optimization failed');
        return fetchStateAndRefresh();
      })
      .then(() => {
        showToast(`Optimization completed! Assigned tasks dynamically.`, 'success');
        switchTab('assignments');
      })
      .catch(err => {
        console.error(err);
        showToast('Optimization failed on backend', 'error');
      });
  }, 1200);
}

// --- RENDER ENGINES ---

function updateAllViews() {
  updateDashboardMetrics();
  renderEmployeeCards();
  renderTaskCards();
  renderAssignmentsTable();
  renderLeaderboard();
  renderSubmissionTaskSelect();
  renderRecentSubmissions();
  
  // Re-build graphs
  initCharts();
}

function updateDashboardMetrics() {
  const totalEmployees = state.employees.length;
  const activeTasks = state.tasks.filter(t => t.status === 'In-Progress').length;
  const completedTasks = state.tasks.filter(t => t.status === 'Completed').length;
  
  let avgPerformance = 0;
  if (totalEmployees > 0) {
    const totalScore = state.employees.reduce((acc, curr) => acc + curr.score, 0);
    avgPerformance = (totalScore / totalEmployees).toFixed(1);
  }

  document.getElementById('card-total-employees').textContent = totalEmployees;
  document.getElementById('card-active-tasks').textContent = activeTasks;
  document.getElementById('card-completed-tasks').textContent = completedTasks;
  document.getElementById('card-avg-performance').textContent = avgPerformance;
}
function renderEmployeeCards() {
  const grid = document.getElementById('employeeCardsGrid');
  grid.innerHTML = '';

  state.employees.forEach(emp => {
    const avatarLetter = emp.name.charAt(0);
    
    // Count active assignments
    const activeTasksCount = state.assignments.filter(a => a.employeeId === emp.id).length;
    
    const statusClass = emp.availability === 'Busy' ? 'in-progress' : 'completed';
    const statusText = emp.availability || 'Available';
    
    const card = document.createElement('div');
    card.className = 'profile-card';
    card.innerHTML = `
      <div class="profile-score-badge">Score: ${emp.score}</div>
      <div class="profile-header">
        <div class="profile-avatar">${avatarLetter}</div>
        <div class="profile-details">
          <h3>${emp.name}</h3>
          <p>${emp.role} &nbsp;<span class="status-badge ${statusClass}" style="padding: 1px 6px; font-size: 0.65rem; border-radius: 4px; display: inline-flex;">${statusText}</span></p>
        </div>
      </div>
      <div class="profile-skills">
        ${emp.skills.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
      </div>
      <div class="profile-footer">
        <span><i class="fa-solid fa-briefcase"></i> ${activeTasksCount} Active Tasks</span>
        <span><i class="fa-solid fa-graduation-cap"></i> ${emp.experience} Yrs Exp</span>
      </div>
    `;
    grid.appendChild(card);
  });
}
function renderTaskCards() {
  const grid = document.getElementById('taskCardsGrid');
  grid.innerHTML = '';

  state.tasks.forEach(task => {
    const priorityClass = task.priority.toLowerCase();
    
    // Find who is assigned
    const assignment = state.assignments.find(a => a.taskId === task.id);
    let assignedToName = 'Unassigned';
    if (assignment) {
      const emp = state.employees.find(e => e.id === assignment.employeeId);
      if (emp) assignedToName = emp.name;
    }

    let statusHtml = '';
    if (task.status === 'Completed') {
      statusHtml = `<span class="status-badge completed">Completed</span>`;
    } else if (task.status === 'In-Progress') {
      statusHtml = `<span class="status-badge in-progress">In-Progress (${assignedToName})</span>`;
    } else {
      statusHtml = `<span class="status-badge pending">Pending Allocation</span>`;
    }

    const card = document.createElement('div');
    card.className = 'task-card';
    card.innerHTML = `
      <span class="task-priority-badge ${priorityClass}">${task.priority}</span>
      <h3 style="font-size: 1.1rem; margin-bottom: 4px; padding-right: 70px;">${task.title}</h3>
      <div style="margin-bottom: 12px;">${statusHtml}</div>
      <p class="task-desc">${task.desc}</p>
      <div class="task-meta">
        <div class="task-meta-item">
          <span>Required Skill</span>
          <span><i class="fa-solid fa-circle-nodes"></i> ${task.skill}</span>
        </div>
        <div class="task-meta-item">
          <span>Deadline</span>
          <span style="color: var(--danger); font-weight:700;"><i class="fa-solid fa-calendar-day"></i> ${task.deadline}</span>
        </div>
      </div>
    `;
    grid.appendChild(card);
  });
}

function renderAssignmentsTable() {
  const tbody = document.getElementById('assignmentsTableBody');
  tbody.innerHTML = '';

  if (state.assignments.length === 0) {
    // Show fallback message if no assignments are active
    const uncompletedPending = state.tasks.filter(t => t.status === 'Pending').length;
    let fallbackText = "No active job assignments found.";
    if (uncompletedPending > 0) {
      fallbackText += " Run optimization to allocate pending tasks.";
    }
    
    tbody.innerHTML = `
      <tr>
        <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 32px 0;">
          <i class="fa-solid fa-circle-nodes" style="font-size: 2rem; margin-bottom: 12px; display: block;"></i>
          ${fallbackText}
        </td>
      </tr>
    `;
    return;
  }

  state.assignments.forEach(assign => {
    const emp = state.employees.find(e => e.id === assign.employeeId);
    const task = state.tasks.find(t => t.id === assign.taskId);
    if (!emp || !task) return;

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>
        <div class="table-employee">
          <div class="table-employee-avatar">${emp.name.charAt(0)}</div>
          <div>
            <div style="font-weight: 700;">${emp.name}</div>
            <div style="font-size: 0.75rem; color: var(--text-muted);">${emp.role}</div>
          </div>
        </div>
      </td>
      <td>
        <div style="font-weight: 600;">${task.title}</div>
      </td>
      <td>
        <span class="skill-tag">${task.skill}</span>
      </td>
      <td>
        <span class="task-priority-badge ${task.priority.toLowerCase()}" style="position: static; padding: 2px 8px;">${task.priority}</span>
      </td>
      <td>
        <span style="font-size: 0.85rem;"><i class="fa-solid fa-calendar-day" style="margin-right:4px;"></i> ${task.deadline}</span>
      </td>
      <td>
        <span class="status-badge in-progress">Active</span>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function renderLeaderboard() {
  const list = document.getElementById('leaderboardList');
  list.innerHTML = '';

  // Sort employees by performance rating (descending)
  const sorted = [...state.employees].sort((a, b) => b.score - a.score);

  if (sorted.length > 0) {
    const best = sorted[0];
    document.getElementById('best-emp-name').textContent = best.name;
    document.getElementById('best-emp-skills').textContent = `Skills: ${best.skills.slice(0, 3).join(', ')}`;
    document.getElementById('best-emp-score').textContent = best.score.toFixed(1);
    document.getElementById('best-emp-avatar').textContent = best.name.charAt(0);
  }

  sorted.slice(0, 5).forEach((emp, index) => {
    const item = document.createElement('div');
    item.className = 'leaderboard-item';
    item.innerHTML = `
      <div class="leaderboard-rank rank-${index + 1}">${index + 1}</div>
      <div class="leaderboard-profile">
        <div class="leaderboard-details">
          <span class="leaderboard-name">${emp.name}</span>
          <span style="font-size: 0.75rem; color: var(--text-muted);">${emp.role}</span>
        </div>
      </div>
      <div class="leaderboard-score">${emp.score.toFixed(1)}</div>
    `;
    list.appendChild(item);
  });
}

function renderSubmissionTaskSelect() {
  const select = document.getElementById('submitTaskSelect');
  select.innerHTML = '<option value="" disabled selected>-- Select a task to complete --</option>';

  // Find all tasks that are currently "In-Progress"
  const inProgressTasks = state.tasks.filter(t => t.status === 'In-Progress');
  
  inProgressTasks.forEach(task => {
    // Find assignee name
    const assignment = state.assignments.find(a => a.taskId === task.id);
    let assigneeName = 'Unassigned';
    if (assignment) {
      const emp = state.employees.find(e => e.id === assignment.employeeId);
      if (emp) assigneeName = emp.name;
    }
    
    const option = document.createElement('option');
    option.value = task.id;
    option.textContent = `${task.title} (Assigned to: ${assigneeName})`;
    select.appendChild(option);
  });
}

function renderRecentSubmissions() {
  const list = document.getElementById('recentSubmissionsList');
  list.innerHTML = '';

  if (state.submissions.length === 0) {
    list.innerHTML = `
      <div style="text-align: center; color: var(--text-muted); padding: 20px 0; font-size: 0.85rem;">
        No recent submissions.
      </div>
    `;
    return;
  }

  state.submissions.slice(0, 5).forEach(sub => {
    const item = document.createElement('div');
    item.className = 'submission-item';
    item.innerHTML = `
      <div class="submission-info">
        <span class="submission-name">${sub.taskTitle}</span>
        <span style="font-size:0.75rem; color: var(--text-secondary);">By ${sub.employeeName} • <span style="font-family: monospace;">${sub.fileName}</span></span>
        <span class="submission-date">${sub.date}</span>
      </div>
      <span class="status-badge completed" style="padding: 2px 8px;">Approved</span>
    `;
    list.appendChild(item);
  });
}

// --- CHART GENERATION FUNCTIONS ---

function initCharts() {
  const isDark = state.theme === 'dark';
  
  // Theme-aware styles
  const gridColor = isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)';
  const textColor = isDark ? '#9ca3af' : '#475569';
  const labelColor = isDark ? '#f3f4f6' : '#0f172a';

  Chart.defaults.color = textColor;
  Chart.defaults.font.family = "'Plus Jakarta Sans', sans-serif";
  Chart.defaults.font.size = 11;
  
  // Helper to destroy existing chart if initialized
  const safeDestroy = (chartName) => {
    if (charts[chartName]) {
      charts[chartName].destroy();
    }
  };

  // 1. Employee Performance Over Time (Line Chart)
  safeDestroy('performance');
  
  // Find current performance scores dynamically or fall back to baseline
  const empSarah = state.employees.find(e => e.name === 'Sarah Connor');
  const empMarcus = state.employees.find(e => e.name === 'Marcus Wright');
  const empJohn = state.employees.find(e => e.name === 'John Connor');
  
  const sarahScore = empSarah ? empSarah.score : 9.6;
  const marcusScore = empMarcus ? empMarcus.score : 8.8;
  const johnScore = empJohn ? empJohn.score : 9.4;

  const perfCtx = document.getElementById('chartPerformanceOverTime').getContext('2d');
  charts.performance = new Chart(perfCtx, {
    type: 'line',
    data: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      datasets: [
        {
          label: 'Sarah Connor',
          data: [9.2, 9.3, 9.5, 9.4, 9.6, sarahScore],
          borderColor: '#6366f1',
          backgroundColor: 'transparent',
          tension: 0.35,
          borderWidth: 2,
          pointRadius: 3
        },
        {
          label: 'Marcus Wright',
          data: [8.0, 8.4, 8.5, 8.7, 8.7, marcusScore],
          borderColor: '#10b981',
          backgroundColor: 'transparent',
          tension: 0.35,
          borderWidth: 2,
          pointRadius: 3
        },
        {
          label: 'John Connor',
          data: [8.9, 9.0, 9.1, 9.3, 9.2, johnScore],
          borderColor: '#0ea5e9',
          backgroundColor: 'transparent',
          tension: 0.35,
          borderWidth: 2,
          pointRadius: 3
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top', labels: { color: textColor } }
      },
      scales: {
        x: { grid: { color: gridColor }, ticks: { color: textColor } },
        y: { grid: { color: gridColor }, ticks: { color: textColor }, min: 5, max: 10 }
      }
    }
  });

  // 2. Task Completion Rate (Doughnut Chart)
  safeDestroy('completion');
  const pending = state.tasks.filter(t => t.status === 'Pending').length;
  const inProgress = state.tasks.filter(t => t.status === 'In-Progress').length;
  const completed = state.tasks.filter(t => t.status === 'Completed').length;
  
  const completionCtx = document.getElementById('chartTaskCompletion').getContext('2d');
  charts.completion = new Chart(completionCtx, {
    type: 'doughnut',
    data: {
      labels: ['Pending', 'In Progress', 'Completed'],
      datasets: [{
        data: [pending, inProgress, completed],
        backgroundColor: ['#f59e0b', '#0ea5e9', '#10b981'],
        borderWidth: 0,
        hoverOffset: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'right', labels: { color: textColor } }
      },
      cutout: '65%'
    }
  });

  // 3. Employee Efficiency Index (Horizontal Bar Chart)
  safeDestroy('efficiency');
  const names = state.employees.map(e => e.name);
  const scoreData = state.employees.map(e => e.score);

  const effCtx = document.getElementById('chartEmployeeEfficiency').getContext('2d');
  charts.efficiency = new Chart(effCtx, {
    type: 'bar',
    data: {
      labels: names,
      datasets: [{
        label: 'Capability Rating',
        data: scoreData,
        backgroundColor: 'rgba(99, 102, 241, 0.7)',
        hoverBackgroundColor: '#6366f1',
        borderRadius: 5,
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: { grid: { color: gridColor }, ticks: { color: textColor }, min: 0, max: 10 },
        y: { grid: { display: false }, ticks: { color: textColor } }
      }
    }
  });

  // 4. Task Priority Distribution (Polar Area / Pie)
  safeDestroy('priority');
  const highTasks = state.tasks.filter(t => t.priority === 'High').length;
  const medTasks = state.tasks.filter(t => t.priority === 'Medium').length;
  const lowTasks = state.tasks.filter(t => t.priority === 'Low').length;

  const priorityCtx = document.getElementById('chartTaskPriority').getContext('2d');
  charts.priority = new Chart(priorityCtx, {
    type: 'polarArea',
    data: {
      labels: ['High', 'Medium', 'Low'],
      datasets: [{
        data: [highTasks, medTasks, lowTasks],
        backgroundColor: [
          'rgba(239, 68, 68, 0.6)',
          'rgba(245, 158, 11, 0.6)',
          'rgba(99, 102, 241, 0.6)'
        ],
        borderColor: isDark ? '#1f2937' : '#ffffff',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'right', labels: { color: textColor } }
      },
      scales: {
        r: {
          grid: { color: gridColor },
          angleLines: { color: gridColor },
          ticks: { backdropColor: 'transparent', color: textColor }
        }
      }
    }
  });

  // 5. Efficiency Comparison - Performance vs Experience Scatter/Bubble
  safeDestroy('efficiencyComparison');
  const scatterData = state.employees.map(e => ({
    x: e.experience,
    y: e.score,
    label: e.name
  }));

  const effCompCtx = document.getElementById('chartEfficiencyComparison').getContext('2d');
  charts.efficiencyComparison = new Chart(effCompCtx, {
    type: 'scatter',
    data: {
      datasets: [{
        label: 'Employees',
        data: scatterData,
        backgroundColor: '#0ea5e9',
        borderColor: '#0284c7',
        pointRadius: 7,
        pointHoverRadius: 9
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const item = ctx.dataset.data[ctx.dataIndex];
              return `${item.label} (Exp: ${item.x} Yrs, Rating: ${item.y})`;
            }
          }
        }
      },
      scales: {
        x: { 
          title: { display: true, text: 'Experience (Years)', color: textColor }, 
          grid: { color: gridColor }, 
          ticks: { color: textColor },
          min: 0,
          max: 10
        },
        y: { 
          title: { display: true, text: 'Rating Score', color: textColor }, 
          grid: { color: gridColor }, 
          ticks: { color: textColor },
          min: 5,
          max: 10
        }
      }
    }
  });

  // 6. Completion Trends & Forecast (Line Chart)
  safeDestroy('trends');
  
  // Count completed tasks dynamically from state
  const completedCount = state.tasks.filter(t => t.status === 'Completed').length;

  const trendsCtx = document.getElementById('chartCompletionTrends').getContext('2d');
  charts.trends = new Chart(trendsCtx, {
    type: 'line',
    data: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun (Actual)', 'Jul (Forecast)', 'Aug (Forecast)'],
      datasets: [
        {
          label: 'Completed Tasks',
          data: [12, 14, 18, 23, 27, completedCount, null, null],
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          tension: 0.3,
          borderWidth: 3,
          fill: true,
          pointRadius: 4
        },
        {
          label: 'Completion Forecast',
          data: [null, null, null, null, null, completedCount, completedCount + 6, completedCount + 12],
          borderColor: '#f59e0b',
          borderDash: [5, 5],
          backgroundColor: 'transparent',
          tension: 0.3,
          borderWidth: 2,
          pointRadius: 4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top', labels: { color: textColor } }
      },
      scales: {
        x: { grid: { color: gridColor }, ticks: { color: textColor } },
        y: { grid: { color: gridColor }, ticks: { color: textColor }, min: 0 }
      }
    }
  });
}

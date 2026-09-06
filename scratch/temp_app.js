// Global App State
let state = {
  employees: [],
  tasks: [],
  assignments: [],
  submissions: [],
  performance_history: [],
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

// Animation states and trackers
const prevDashboardMetrics = {};
const prevEmployeeScores = {};
const prevLeaderboardRanks = {};

// Helper to animate count of values inside elements
function animateCountValue(elementId, start, end, isDecimal = false) {
  const el = document.getElementById(elementId);
  if (!el) return;
  
  if (start === end) {
    el.textContent = isDecimal ? end.toFixed(1) : end;
    return;
  }
  
  const duration = 1000;
  const startTime = performance.now();
  
  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const easeProgress = progress * (2 - progress); // easeOutQuad
    const currentValue = start + (end - start) * easeProgress;
    
    if (isDecimal) {
      el.textContent = currentValue.toFixed(1);
    } else {
      el.textContent = Math.floor(currentValue);
    }
    
    if (progress < 1) {
      requestAnimationFrame(update);
    } else {
      el.textContent = isDecimal ? end.toFixed(1) : end;
    }
  }
  requestAnimationFrame(update);
}

// Helper to animate individual employee score elements
function animateScoreElement(element, start, end) {
  if (!element) return;
  if (start === end) {
    element.textContent = `Score: ${end.toFixed(1)}`;
    return;
  }
  
  const duration = 1000;
  const startTime = performance.now();
  
  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const easeProgress = progress * (2 - progress);
    const currentValue = start + (end - start) * easeProgress;
    
    element.textContent = `Score: ${currentValue.toFixed(1)}`;
    
    if (progress < 1) {
      requestAnimationFrame(update);
    } else {
      element.textContent = `Score: ${end.toFixed(1)}`;
    }
  }
  requestAnimationFrame(update);
}

// Chart Instances Global Object
const charts = {
  performanceAnalytics: null,
  taskCompletionAnalytics: null,
  performanceDashboard: null,
  taskCompletionDashboard: null,
  efficiency: null,
  workload: null,
  priority: null,
  trends: null,
  efficiencyComparison: null
};

// --- CORE SYSTEM INITS ---
document.addEventListener('DOMContentLoaded', () => {
  initAppState();
  setupEventListeners();
  setupNotificationListeners();
  fetchStateAndRefresh().then(() => {
    switchTab('dashboard'); // Default view
  });
});

async function fetchStateAndRefresh() {
  try {
    const response = await fetch('/api/state');
    if (!response.ok) throw new Error('Failed to fetch state');
    const newState = await response.json();
    state.employees = newState.employees || [];
    state.tasks = newState.tasks || [];
    state.assignments = newState.assignments || [];
    state.submissions = newState.submissions || [];
    state.performance_history = newState.performance_history || [];
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
  // Sidebar collapse toggle
  const sidebarCollapseBtn = document.getElementById('sidebarCollapseBtn');
  if (sidebarCollapseBtn) {
    sidebarCollapseBtn.addEventListener('click', () => {
      const sidebar = document.getElementById('sidebar');
      sidebar.classList.toggle('collapsed');
      const collapseIcon = document.getElementById('collapseIcon');
      if (sidebar.classList.contains('collapsed')) {
        collapseIcon.className = 'fa-solid fa-angles-right';
      } else {
        collapseIcon.className = 'fa-solid fa-angles-left';
      }
      setTimeout(initCharts, 250);
    });
  }

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

  // Employee filter listeners
  const empSearchInput = document.getElementById('empSearchInput');
  if (empSearchInput) empSearchInput.addEventListener('input', renderEmployeeCards);

  const empAvailabilityFilter = document.getElementById('empAvailabilityFilter');
  if (empAvailabilityFilter) empAvailabilityFilter.addEventListener('change', renderEmployeeCards);

  const empRoleFilter = document.getElementById('empRoleFilter');
  if (empRoleFilter) empRoleFilter.addEventListener('change', renderEmployeeCards);

  const empSkillFilter = document.getElementById('empSkillFilter');
  if (empSkillFilter) empSkillFilter.addEventListener('change', renderEmployeeCards);

  const empPerformanceFilter = document.getElementById('empPerformanceFilter');
  if (empPerformanceFilter) empPerformanceFilter.addEventListener('change', renderEmployeeCards);

  const empExperienceFilter = document.getElementById('empExperienceFilter');
  if (empExperienceFilter) empExperienceFilter.addEventListener('change', renderEmployeeCards);

  const employeeSortSelect = document.getElementById('employeeSort');
  if (employeeSortSelect) employeeSortSelect.addEventListener('change', renderEmployeeCards);

  // Task Registry filter listeners
  const taskSearchInput = document.getElementById('taskSearchInput');
  if (taskSearchInput) taskSearchInput.addEventListener('input', renderTaskCards);

  const taskStatusFilter = document.getElementById('taskStatusFilter');
  if (taskStatusFilter) taskStatusFilter.addEventListener('change', renderTaskCards);

  const taskPriorityFilter = document.getElementById('taskPriorityFilter');
  if (taskPriorityFilter) taskPriorityFilter.addEventListener('change', renderTaskCards);

  const taskSkillFilter = document.getElementById('taskSkillFilter');
  if (taskSkillFilter) taskSkillFilter.addEventListener('change', renderTaskCards);

  const taskDeadlineFilter = document.getElementById('taskDeadlineFilter');
  if (taskDeadlineFilter) taskDeadlineFilter.addEventListener('change', renderTaskCards);

  const taskSortSelect = document.getElementById('taskSort');
  if (taskSortSelect) taskSortSelect.addEventListener('change', renderTaskCards);

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

  // Drawer close events
  const closeDrawerBtn = document.getElementById('closeDrawerBtn');
  if (closeDrawerBtn) {
    closeDrawerBtn.addEventListener('click', closeEmployeeProfile);
  }
  const drawerBackdrop = document.getElementById('drawerBackdrop');
  if (drawerBackdrop) {
    drawerBackdrop.addEventListener('click', closeEmployeeProfile);
  }
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

  // Update top sticky header title & subtitle
  const headerTitle = document.getElementById('headerSectionTitle');
  const headerSub = document.getElementById('headerSectionSub');
  
  const sectionTitles = {
    dashboard: { title: 'Operations Dashboard', sub: 'Real-time workforce deployment and capability indicators' },
    employees: { title: 'Employees Management', sub: 'Configure team members, skills list, and availability status' },
    tasks: { title: 'Task Registry', sub: 'Manage incoming work queues, deadlines, and skill requirements' },
    assignments: { title: 'Optimized Assignments', sub: 'Dynamic job allocations based on performance matching and task requirements' },
    analytics: { title: 'Analytics Hub', sub: 'Advanced metrics, workforce workloads, and performance trend insights' },
    activity: { title: 'Activity Feed', sub: 'Chronological audit trail of task optimization and employee assignments' },
    submission: { title: 'Deliverables Portal', sub: 'Upload files to mark assigned tasks as complete and trigger review' },
    settings: { title: 'System Settings', sub: 'Configure dashboard preferences, manage backups, and reset mock data' }
  };

  if (sectionTitles[sectionName]) {
    if (headerTitle) headerTitle.textContent = sectionTitles[sectionName].title;
    if (headerSub) headerSub.textContent = sectionTitles[sectionName].sub;
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

  // Redraw charts when switching to Analytics or Dashboard tab post-DOM layout update
  if (sectionName === 'analytics' || sectionName === 'dashboard') {
    setTimeout(() => {
      initCharts();
    }, 50);
  }
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
  const cleanQuery = (query || '').toLowerCase().trim();

  // Sync with Employee search input if on Employees page
  const empSearchInput = document.getElementById('empSearchInput');
  if (empSearchInput) {
    empSearchInput.value = cleanQuery;
    renderEmployeeCards();
  }

  // Sync with Task search input if on Tasks page
  const taskSearchInput = document.getElementById('taskSearchInput');
  if (taskSearchInput) {
    taskSearchInput.value = cleanQuery;
    renderTaskCards();
  }

  // Filter Employee cards
  const employeeCards = document.querySelectorAll('.profile-card');
  employeeCards.forEach(card => {
    const textContent = card.textContent.toLowerCase();
    card.style.display = (cleanQuery === '' || textContent.includes(cleanQuery)) ? 'flex' : 'none';
  });

  // Filter Task cards
  const taskCards = document.querySelectorAll('.task-card');
  taskCards.forEach(card => {
    const textContent = card.textContent.toLowerCase();
    card.style.display = (cleanQuery === '' || textContent.includes(cleanQuery)) ? 'block' : 'none';
  });

  // Filter Assignments table rows
  const tableRows = document.querySelectorAll('#assignmentsTableBody tr');
  tableRows.forEach(row => {
    const textContent = row.textContent.toLowerCase();
    row.style.display = (cleanQuery === '' || textContent.includes(cleanQuery)) ? 'table-row' : 'none';
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
  
  // Render Dashboard Overview Widgets
  renderDashboardTodayTasks();
  renderDashboardTopWorkforce();
  renderDashboardRecentAssignments();
  renderDashboardRecentSubmissions();
  renderDashboardActivityFeed();
  renderActivityFeedContainer();
  updateNotificationsPanel();
  
  // Re-build graphs
  initCharts();
}

function updateDashboardMetrics() {
  const totalEmployees = state.employees.length;
  const activeEmployees = state.employees.filter(e => e.availability === 'Busy').length;
  const pendingTasks = state.tasks.filter(t => t.status === 'Pending').length;
  const activeTasks = state.tasks.filter(t => t.status === 'In-Progress').length;
  const completedTasks = state.tasks.filter(t => t.status === 'Completed').length;
  
  let avgPerformance = 0.0;
  if (totalEmployees > 0) {
    const totalScore = state.employees.reduce((acc, curr) => acc + curr.score, 0);
    avgPerformance = parseFloat((totalScore / totalEmployees).toFixed(1));
  }

  // Retrieve previous metrics or default to 0
  const prevTotal = prevDashboardMetrics['total'] || 0;
  const prevActiveEmp = prevDashboardMetrics['activeEmp'] || 0;
  const prevPending = prevDashboardMetrics['pending'] || 0;
  const prevActive = prevDashboardMetrics['active'] || 0;
  const prevCompleted = prevDashboardMetrics['completed'] || 0;
  const prevAvg = prevDashboardMetrics['avg'] || 0.0;

  // Save new values
  prevDashboardMetrics['total'] = totalEmployees;
  prevDashboardMetrics['activeEmp'] = activeEmployees;
  prevDashboardMetrics['pending'] = pendingTasks;
  prevDashboardMetrics['active'] = activeTasks;
  prevDashboardMetrics['completed'] = completedTasks;
  prevDashboardMetrics['avg'] = avgPerformance;

  // Animate counts
  animateCountValue('card-total-employees', prevTotal, totalEmployees);
  animateCountValue('card-active-employees', prevActiveEmp, activeEmployees);
  animateCountValue('card-pending-tasks', prevPending, pendingTasks);
  animateCountValue('card-active-tasks', prevActive, activeTasks);
  animateCountValue('card-completed-tasks', prevCompleted, completedTasks);
  animateCountValue('card-avg-performance', prevAvg, avgPerformance, true);
}

function renderEmployeeCards() {
  const grid = document.getElementById('employeeCardsGrid');
  if (!grid) return;
  grid.innerHTML = '';

  const searchVal = (document.getElementById('empSearchInput')?.value || '').toLowerCase().trim();
  const availFilter = document.getElementById('empAvailabilityFilter')?.value || 'ALL';
  const roleFilter = document.getElementById('empRoleFilter')?.value || 'ALL';
  const skillFilter = document.getElementById('empSkillFilter')?.value || 'ALL';
  const perfFilter = document.getElementById('empPerformanceFilter')?.value || 'ALL';
  const expFilter = document.getElementById('empExperienceFilter')?.value || 'ALL';
  const sortVal = document.getElementById('employeeSort')?.value || 'score_desc';

  let employeesToRender = [...state.employees];

  // 1. Text Search Filter
  if (searchVal) {
    employeesToRender = employeesToRender.filter(e => 
      e.name.toLowerCase().includes(searchVal) ||
      e.role.toLowerCase().includes(searchVal) ||
      (e.department && e.department.toLowerCase().includes(searchVal)) ||
      e.skills.some(s => s.toLowerCase().includes(searchVal))
    );
  }

  // 2. Availability Filter
  if (availFilter !== 'ALL') {
    employeesToRender = employeesToRender.filter(e => (e.availability || 'Available') === availFilter);
  }

  // 3. Role Filter
  if (roleFilter !== 'ALL') {
    employeesToRender = employeesToRender.filter(e => e.role.toLowerCase().includes(roleFilter.toLowerCase()));
  }

  // 4. Skill Filter
  if (skillFilter !== 'ALL') {
    employeesToRender = employeesToRender.filter(e => 
      e.skills.some(s => s.toLowerCase().includes(skillFilter.toLowerCase()))
    );
  }

  // 5. Performance Filter
  if (perfFilter === 'HIGH') {
    employeesToRender = employeesToRender.filter(e => e.score >= 9.0);
  } else if (perfFilter === 'MED') {
    employeesToRender = employeesToRender.filter(e => e.score >= 8.0 && e.score < 9.0);
  } else if (perfFilter === 'LOW') {
    employeesToRender = employeesToRender.filter(e => e.score < 8.0);
  }

  // 6. Experience Filter
  if (expFilter === 'SENIOR') {
    employeesToRender = employeesToRender.filter(e => e.experience >= 7);
  } else if (expFilter === 'MID') {
    employeesToRender = employeesToRender.filter(e => e.experience >= 4 && e.experience <= 6);
  } else if (expFilter === 'JUNIOR') {
    employeesToRender = employeesToRender.filter(e => e.experience <= 3);
  }

  // 7. Sorting
  if (sortVal === 'score_desc' || sortVal === 'performance') {
    employeesToRender.sort((a, b) => b.score - a.score);
  } else if (sortVal === 'score_asc') {
    employeesToRender.sort((a, b) => a.score - b.score);
  } else if (sortVal === 'experience_desc' || sortVal === 'experience') {
    employeesToRender.sort((a, b) => b.experience - a.experience);
  } else if (sortVal === 'experience_asc') {
    employeesToRender.sort((a, b) => a.experience - b.experience);
  } else if (sortVal === 'success_rate_desc') {
    employeesToRender.sort((a, b) => (b.success_rate || 0) - (a.success_rate || 0));
  } else if (sortVal === 'completed_tasks_desc' || sortVal === 'completed_tasks') {
    employeesToRender.sort((a, b) => (b.completed_tasks || 0) - (a.completed_tasks || 0));
  } else if (sortVal === 'active_tasks_desc' || sortVal === 'active_tasks') {
    employeesToRender.sort((a, b) => (b.active_tasks || 0) - (a.active_tasks || 0));
  }

  if (employeesToRender.length === 0) {
    grid.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 48px 0; font-size: 0.9rem;">
        <i class="fa-solid fa-user-slash" style="font-size: 2.2rem; display: block; margin-bottom: 12px; color: var(--text-muted);"></i>
        No matching employees found. Try adjusting your filter parameters.
      </div>
    `;
    return;
  }

  employeesToRender.forEach(emp => {
    const avatarLetter = emp.name.charAt(0);
    const statusClass = emp.availability === 'Busy' ? 'busy' : 'available';
    const statusText = emp.availability || 'Available';
    const currentTaskText = emp.current_task && emp.current_task !== 'None' ? emp.current_task : 'No Active Task';
    
    const percent = Math.min(100, Math.max(0, (emp.score / 10.0) * 100));
    let scoreColor = 'var(--success)';
    if (emp.score < 7.0) scoreColor = 'var(--danger)';
    else if (emp.score < 8.5) scoreColor = 'var(--warning)';

    const card = document.createElement('div');
    card.className = 'profile-card';
    card.setAttribute('data-emp-id', emp.id);
    card.style.cursor = 'pointer';
    card.addEventListener('click', () => openEmployeeProfile(emp));
    
    const prevScore = prevEmployeeScores[emp.id];
    prevEmployeeScores[emp.id] = emp.score;
    
    card.innerHTML = `
      <div class="card-header-flex">
        <div class="profile-avatar-container">
          <div class="profile-avatar">${avatarLetter}</div>
          <span class="online-indicator ${emp.online_status === 'Online' ? 'online' : 'offline'}"></span>
        </div>
        <div class="profile-details">
          <h3>${emp.name}</h3>
          <p class="role-text">${emp.role} • <span class="dept-name">${emp.department || 'Engineering'}</span></p>
          <div class="badge-row">
            <span class="status-badge ${statusClass}">● ${statusText}</span>
          </div>
        </div>
      </div>

      <div class="perf-bar-section">
        <div class="perf-bar-header">
          <span class="perf-label">Performance Rating</span>
          <span class="perf-value score-badge-val" style="color: ${scoreColor}">${emp.score.toFixed(1)} / 10.0</span>
        </div>
        <div class="perf-bar-track">
          <div class="perf-bar-fill" style="width: ${percent}%; background-color: ${scoreColor};"></div>
        </div>
      </div>

      <div class="profile-skills-row">
        ${emp.skills.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
      </div>

      <div class="profile-metrics-grid">
        <div class="mini-metric">
          <span class="metric-lbl">Active</span>
          <span class="metric-val"><i class="fa-solid fa-briefcase"></i> ${emp.active_tasks}</span>
        </div>
        <div class="mini-metric">
          <span class="metric-lbl">Done</span>
          <span class="metric-val"><i class="fa-solid fa-circle-check"></i> ${emp.completed_tasks}</span>
        </div>
        <div class="mini-metric">
          <span class="metric-lbl">Success</span>
          <span class="metric-val" style="color: var(--success);"><i class="fa-solid fa-chart-line"></i> ${emp.success_rate}%</span>
        </div>
        <div class="mini-metric">
          <span class="metric-lbl">Exp</span>
          <span class="metric-val"><i class="fa-solid fa-award"></i> ${emp.experience}y</span>
        </div>
      </div>

      <div class="current-task-box">
        <span class="task-box-label"><i class="fa-solid fa-thumbtack"></i> Current Task:</span>
        <span class="task-box-title" title="${currentTaskText}">${currentTaskText}</span>
      </div>
    `;
    grid.appendChild(card);
    
    if (prevScore !== undefined && prevScore !== emp.score) {
      const scoreBadge = card.querySelector('.score-badge-val');
      animateScoreElement(scoreBadge, prevScore, emp.score);
    }
  });
}

function renderDashboardTodayTasks() {
  const container = document.getElementById('dashboardTodayTasks');
  if (!container) return;
  container.innerHTML = '';

  const upcomingTasks = [...state.tasks]
    .filter(t => t.status !== 'Completed')
    .sort((a, b) => new Date(a.deadline) - new Date(b.deadline))
    .slice(0, 5);

  if (upcomingTasks.length === 0) {
    container.innerHTML = `<div class="empty-widget-state"><i class="fa-solid fa-circle-check" style="font-size: 1.5rem; color: var(--success); display: block; margin-bottom: 8px;"></i>All tasks completed! No upcoming deadlines.</div>`;
    return;
  }

  upcomingTasks.forEach(task => {
    const item = document.createElement('div');
    item.className = 'dashboard-list-item';
    
    const assignment = state.assignments.find(a => a.taskId === task.id);
    let assigneeName = 'Unassigned';
    if (assignment) {
      const emp = state.employees.find(e => e.id === assignment.employeeId);
      if (emp) assigneeName = emp.name;
    }

    item.innerHTML = `
      <div class="list-item-info">
        <span class="list-item-title">${task.title}</span>
        <span class="list-item-sub">Assignee: <strong>${assigneeName}</strong> • Skill: <span class="skill-tag-sm">${task.skill}</span></span>
      </div>
      <div class="list-item-right">
        <span class="task-priority-badge ${task.priority.toLowerCase()}" style="position: static; padding: 2px 8px;">${task.priority}</span>
        <span class="deadline-tag"><i class="fa-solid fa-calendar-day"></i> ${task.deadline}</span>
      </div>
    `;
    container.appendChild(item);
  });
}

function renderDashboardTopWorkforce() {
  const container = document.getElementById('dashboardTopWorkforce');
  if (!container) return;
  container.innerHTML = '';

  const topWorkforce = [...state.employees]
    .sort((a, b) => b.score - a.score)
    .slice(0, 5);

  topWorkforce.forEach((emp, index) => {
    const item = document.createElement('div');
    item.className = 'dashboard-list-item';
    item.innerHTML = `
      <div class="list-item-rank">#${index + 1}</div>
      <div class="profile-avatar-sm">${emp.name.charAt(0)}</div>
      <div class="list-item-info">
        <span class="list-item-title">${emp.name}</span>
        <span class="list-item-sub">${emp.role} • ${emp.experience} Yrs Exp</span>
      </div>
      <div class="list-item-right">
        <span class="top-score-badge"><i class="fa-solid fa-star"></i> ${emp.score.toFixed(1)}</span>
        <span class="success-rate-tag">${emp.success_rate}% Success</span>
      </div>
    `;
    container.appendChild(item);
  });
}

function renderDashboardRecentAssignments() {
  const container = document.getElementById('dashboardRecentAssignments');
  if (!container) return;
  container.innerHTML = '';

  if (state.assignments.length === 0) {
    container.innerHTML = `<div class="empty-widget-state">No active task assignments found.</div>`;
    return;
  }

  state.assignments.slice(0, 5).forEach(assign => {
    const emp = state.employees.find(e => e.id === assign.employeeId);
    const task = state.tasks.find(t => t.id === assign.taskId);
    if (!emp || !task) return;

    const item = document.createElement('div');
    item.className = 'dashboard-list-item';
    item.innerHTML = `
      <div class="profile-avatar-sm">${emp.name.charAt(0)}</div>
      <div class="list-item-info">
        <span class="list-item-title">${task.title}</span>
        <span class="list-item-sub">Assigned to: <strong>${emp.name}</strong></span>
      </div>
      <div class="list-item-right">
        <span class="status-badge in-progress">Active</span>
      </div>
    `;
    container.appendChild(item);
  });
}

function renderDashboardRecentSubmissions() {
  const container = document.getElementById('dashboardRecentSubmissions');
  if (!container) return;
  container.innerHTML = '';

  if (state.submissions.length === 0) {
    container.innerHTML = `<div class="empty-widget-state">No deliverables submitted yet.</div>`;
    return;
  }

  state.submissions.slice(0, 5).forEach(sub => {
    const item = document.createElement('div');
    item.className = 'dashboard-list-item';
    item.innerHTML = `
      <div class="submission-icon"><i class="fa-solid fa-file-circle-check"></i></div>
      <div class="list-item-info">
        <span class="list-item-title">${sub.taskTitle}</span>
        <span class="list-item-sub">By <strong>${sub.employeeName}</strong> • ${sub.date}</span>
      </div>
      <div class="list-item-right">
        <span class="status-badge completed">Approved</span>
      </div>
    `;
    container.appendChild(item);
  });
}

function getActivityMeta(type) {
  switch (type) {
    case 'employee_added':
      return { icon: 'fa-user-plus', color: 'var(--success)', badge: 'Employee Added' };
    case 'task_created':
      return { icon: 'fa-plus-circle', color: 'var(--primary)', badge: 'Task Created' };
    case 'assignment':
      return { icon: 'fa-circle-nodes', color: 'var(--info)', badge: 'Task Assigned' };
    case 'reassignment':
      return { icon: 'fa-arrows-rotate', color: 'var(--warning)', badge: 'Task Reassigned' };
    case 'completion':
      return { icon: 'fa-circle-check', color: 'var(--success)', badge: 'Task Completed' };
    case 'submission':
      return { icon: 'fa-cloud-arrow-up', color: 'var(--accent)', badge: 'Submission Received' };
    case 'performance_update':
      return { icon: 'fa-chart-line', color: '#ec4899', badge: 'Performance Updated' };
    case 'availability':
    case 'availability_update':
      return { icon: 'fa-user-check', color: '#10b981', badge: 'Employee Available' };
    default:
      return { icon: 'fa-circle-info', color: 'var(--primary)', badge: 'System' };
  }
}

function renderDashboardActivityFeed() {
  const container = document.getElementById('dashboardActivityFeed');
  if (!container) return;
  container.innerHTML = '';

  if (!state.activities || state.activities.length === 0) {
    container.innerHTML = `<div class="empty-widget-state"><i class="fa-solid fa-clock-rotate-left" style="font-size: 1.5rem; margin-bottom: 8px; display: block; color: var(--text-muted);"></i>No activity logged yet.</div>`;
    return;
  }

  state.activities.slice(0, 8).forEach(act => {
    const meta = getActivityMeta(act.type);
    const item = document.createElement('div');
    item.className = 'activity-item';

    item.innerHTML = `
      <div class="activity-icon" style="color: ${meta.color};">
        <i class="fa-solid ${meta.icon}"></i>
      </div>
      <div class="activity-content">
        <div class="activity-text">${act.message}</div>
        <div class="activity-time">${act.timestamp}</div>
      </div>
    `;
    container.appendChild(item);
  });
}

function renderActivityFeedContainer() {
  const container = document.getElementById('activityTimelineContainer');
  if (!container) return;
  container.innerHTML = '';

  if (!state.activities || state.activities.length === 0) {
    container.innerHTML = `
      <div class="empty-feed-state" style="text-align: center; padding: 48px 20px; color: var(--text-muted);">
        <i class="fa-solid fa-clock-rotate-left" style="font-size: 2.5rem; margin-bottom: 12px; display: block; color: var(--text-muted);"></i>
        <p style="font-weight: 700; font-size: 1.1rem; color: var(--text-primary); margin-bottom: 6px;">No Activity Events Logged</p>
        <p style="font-size: 0.85rem; max-width: 400px; margin: 0 auto;">Events will automatically populate as team members are added, tasks created, assigned, submitted, and completed.</p>
      </div>
    `;
    return;
  }

  state.activities.forEach(act => {
    const meta = getActivityMeta(act.type);
    const item = document.createElement('div');
    item.className = 'timeline-item';

    item.innerHTML = `
      <div class="timeline-marker" style="background-color: ${meta.color}20; color: ${meta.color}; border-color: ${meta.color};">
        <i class="fa-solid ${meta.icon}"></i>
      </div>
      <div class="timeline-content">
        <div class="timeline-header">
          <span class="timeline-badge" style="background-color: ${meta.color}15; color: ${meta.color}; font-weight: 600; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem;">${meta.badge}</span>
          <span class="timeline-timestamp"><i class="fa-solid fa-clock" style="margin-right: 4px;"></i>${act.timestamp}</span>
        </div>
        <p class="timeline-description">${act.message}</p>
      </div>
    `;
    container.appendChild(item);
  });
}
function renderTaskCards() {
  const grid = document.getElementById('taskCardsGrid');
  if (!grid) return;
  grid.innerHTML = '';

  const searchVal = (document.getElementById('taskSearchInput')?.value || '').toLowerCase().trim();
  const statusFilter = document.getElementById('taskStatusFilter')?.value || 'ALL';
  const priorityFilter = document.getElementById('taskPriorityFilter')?.value || 'ALL';
  const skillFilter = document.getElementById('taskSkillFilter')?.value || 'ALL';
  const deadlineFilter = document.getElementById('taskDeadlineFilter')?.value || 'ALL';
  const sortVal = document.getElementById('taskSort')?.value || 'priority';

  let tasksToRender = [...state.tasks];

  // 1. Text Search Filter
  if (searchVal) {
    tasksToRender = tasksToRender.filter(t => 
      t.title.toLowerCase().includes(searchVal) || 
      t.desc.toLowerCase().includes(searchVal) || 
      t.skill.toLowerCase().includes(searchVal) ||
      t.priority.toLowerCase().includes(searchVal) ||
      t.status.toLowerCase().includes(searchVal)
    );
  }

  // 2. Status Filter
  if (statusFilter !== 'ALL') {
    tasksToRender = tasksToRender.filter(t => t.status === statusFilter);
  }

  // 3. Priority Filter
  if (priorityFilter !== 'ALL') {
    tasksToRender = tasksToRender.filter(t => t.priority === priorityFilter);
  }

  // 4. Required Skill Filter
  if (skillFilter !== 'ALL') {
    tasksToRender = tasksToRender.filter(t => t.skill.toLowerCase().includes(skillFilter.toLowerCase()));
  }

  // 5. Deadline Filter
  if (deadlineFilter !== 'ALL') {
    const today = new Date().toISOString().split('T')[0];
    if (deadlineFilter === 'UPCOMING') {
      tasksToRender = tasksToRender.filter(t => t.status !== 'Completed' && t.deadline >= today);
    } else if (deadlineFilter === 'OVERDUE') {
      tasksToRender = tasksToRender.filter(t => t.status !== 'Completed' && t.deadline < today);
    }
  }

  // 6. Sorting
  if (sortVal === 'priority') {
    const pMap = { High: 3, Medium: 2, Low: 1 };
    tasksToRender.sort((a, b) => pMap[b.priority] - pMap[a.priority]);
  } else if (sortVal === 'deadline_asc' || sortVal === 'deadline') {
    tasksToRender.sort((a, b) => new Date(a.deadline) - new Date(b.deadline));
  } else if (sortVal === 'deadline_desc') {
    tasksToRender.sort((a, b) => new Date(b.deadline) - new Date(a.deadline));
  } else if (sortVal === 'status') {
    tasksToRender.sort((a, b) => a.status.localeCompare(b.status));
  } else if (sortVal === 'title') {
    tasksToRender.sort((a, b) => a.title.localeCompare(b.title));
  }

  if (tasksToRender.length === 0) {
    grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 48px 0; font-size: 0.9rem;"><i class="fa-solid fa-folder-open" style="font-size: 2.2rem; display: block; margin-bottom: 12px; color: var(--text-muted);"></i>No matching tasks found. Try adjusting your filter parameters.</div>`;
    return;
  }

  tasksToRender.forEach(task => {
    const priorityClass = task.priority.toLowerCase();
    
    const assignment = state.assignments.find(a => a.taskId === task.id);
    let assignedToName = 'Unassigned';
    if (assignment) {
      const emp = state.employees.find(e => e.id === assignment.employeeId);
      if (emp) assignedToName = emp.name;
    }

    let statusBadge = '';
    if (task.status === 'Completed') {
      statusBadge = `<span class="status-badge completed">Completed</span>`;
    } else if (task.status === 'In-Progress') {
      statusBadge = `<span class="status-badge in-progress">In Progress (${assignedToName})</span>`;
    } else {
      statusBadge = `<span class="status-badge pending">Pending</span>`;
    }

    const card = document.createElement('div');
    card.className = 'task-card';
    card.innerHTML = `
      <div class="task-card-header">
        <span class="priority-badge ${priorityClass}">${task.priority}</span>
        ${statusBadge}
      </div>
      <h3 class="task-card-title">${task.title}</h3>
      <p class="task-desc">${task.desc}</p>
      <div class="task-meta-grid">
        <div class="task-assignee-tag">
          <i class="fa-solid fa-circle-nodes" style="color: var(--primary);"></i>
          <span>Required: <strong>${task.skill}</strong></span>
        </div>
        <div class="task-deadline-tag">
          <i class="fa-solid fa-calendar-day"></i>
          <span>${task.deadline}</span>
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
  const list = document.getElementById('leaderboardList') || document.getElementById('dashboardTopWorkforce');

  const sorted = [...state.employees].sort((a, b) => {
    if (b.score !== a.score) return b.score - a.score;
    if (b.success_rate !== a.success_rate) return b.success_rate - a.success_rate;
    if (a.active_tasks !== b.active_tasks) return a.active_tasks - b.active_tasks;
    return b.experience - a.experience;
  });

  if (sorted.length > 0) {
    const best = sorted[0];
    const nameEl = document.getElementById('best-emp-name');
    const skillsEl = document.getElementById('best-emp-skills');
    const scoreEl = document.getElementById('best-emp-score');
    const avatarEl = document.getElementById('best-emp-avatar');
    
    if (nameEl) nameEl.textContent = best.name;
    if (skillsEl) skillsEl.textContent = `Skills: ${best.skills.slice(0, 3).join(', ')}`;
    if (scoreEl) scoreEl.textContent = best.score.toFixed(1);
    if (avatarEl) {
      if (avatarEl.tagName === 'IMG') {
        avatarEl.src = best.avatar_url || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=150&h=150&q=80';
      } else {
        avatarEl.textContent = best.name.charAt(0);
      }
    }
  }

  if (!list) return;
  list.innerHTML = '';

  sorted.slice(0, 5).forEach((emp, index) => {
    const newRank = index + 1;
    const prevRank = prevLeaderboardRanks[emp.id];
    prevLeaderboardRanks[emp.id] = newRank;

    const item = document.createElement('div');
    item.className = 'leaderboard-item';
    item.innerHTML = `
      <div class="leaderboard-rank rank-${newRank}">${newRank}</div>
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
  if (!select) return;
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
  if (!list) return;
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

function safeDestroyCanvas(canvasId, chartKey) {
  const canvas = document.getElementById(canvasId);
  if (canvas) {
    const existing = Chart.getChart(canvas);
    if (existing) {
      existing.destroy();
    }
  }
  if (charts[chartKey]) {
    try {
      charts[chartKey].destroy();
    } catch (e) {}
    charts[chartKey] = null;
  }
}

function toggleChartEmptyState(canvasId, emptyId, isEmpty) {
  const canvas = document.getElementById(canvasId);
  const emptyEl = document.getElementById(emptyId);
  
  if (isEmpty) {
    if (canvas) canvas.style.display = 'none';
    if (emptyEl) emptyEl.style.display = 'flex';
    return true;
  } else {
    if (canvas) canvas.style.display = 'block';
    if (emptyEl) emptyEl.style.display = 'none';
    return false;
  }
}

function initCharts() {
  const isDark = state.theme === 'dark';
  
  const gridColor = isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)';
  const textColor = isDark ? '#9ca3af' : '#475569';

  Chart.defaults.color = textColor;
  Chart.defaults.font.family = "'Plus Jakarta Sans', sans-serif";
  Chart.defaults.font.size = 11;
  
  const colors = ['#6366f1', '#10b981', '#0ea5e9', '#f59e0b', '#ec4899', '#8b5cf6', '#14b8a6', '#f97316'];

  // Helper to build line datasets for performance history
  const buildPerformanceDatasets = () => {
    if (!state.employees || state.employees.length === 0) return { labels: [], datasets: [] };

    let eventLabels = ['Initial'];
    if (state.performance_history && state.performance_history.length > 0) {
      const dates = state.performance_history.map((ph, idx) => ph.date ? `Log #${idx+1} (${ph.date})` : `Log #${idx+1}`);
      eventLabels = ['Initial', ...dates];
    } else {
      eventLabels = ['Initial', 'Current'];
    }

    const datasets = state.employees.map((emp, index) => {
      const empLogs = (state.performance_history || []).filter(ph => ph.employeeId === emp.id);
      
      let scores = [];
      if (empLogs.length > 0) {
        scores.push(empLogs[0].oldScore);
        empLogs.forEach(ph => scores.push(ph.newScore));
        while (scores.length < eventLabels.length) {
          scores.push(emp.score);
        }
      } else {
        scores = [emp.score, emp.score];
      }

      return {
        label: emp.name,
        data: scores,
        borderColor: colors[index % colors.length],
        backgroundColor: 'transparent',
        tension: 0.35,
        borderWidth: 2,
        pointRadius: 4
      };
    });

    return { labels: eventLabels, datasets };
  };

  // 1. Employee Performance History (Analytics Hub)
  safeDestroyCanvas('chartPerformanceOverTime', 'performanceAnalytics');
  const perfData = buildPerformanceDatasets();
  const isPerfEmpty = perfData.datasets.length === 0;
  if (!toggleChartEmptyState('chartPerformanceOverTime', 'empty-chartPerformanceOverTime', isPerfEmpty)) {
    const perfCtx = document.getElementById('chartPerformanceOverTime').getContext('2d');
    charts.performanceAnalytics = new Chart(perfCtx, {
      type: 'line',
      data: perfData,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top', labels: { color: textColor } }
        },
        scales: {
          x: { grid: { color: gridColor }, ticks: { color: textColor } },
          y: { grid: { color: gridColor }, ticks: { color: textColor }, min: 0, max: 10 }
        }
      }
    });
  }

  // 1b. Employee Performance History (Dashboard)
  safeDestroyCanvas('chartPerformanceDashboard', 'performanceDashboard');
  if (!toggleChartEmptyState('chartPerformanceDashboard', 'empty-chartPerformanceDashboard', isPerfEmpty)) {
    const perfDashCtx = document.getElementById('chartPerformanceDashboard').getContext('2d');
    charts.performanceDashboard = new Chart(perfDashCtx, {
      type: 'line',
      data: perfData,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top', labels: { color: textColor } }
        },
        scales: {
          x: { grid: { color: gridColor }, ticks: { color: textColor } },
          y: { grid: { color: gridColor }, ticks: { color: textColor }, min: 0, max: 10 }
        }
      }
    });
  }

  // 2. Task Status Distribution (Analytics Hub)
  safeDestroyCanvas('chartTaskCompletion', 'taskCompletionAnalytics');
  const pendingCount = (state.tasks || []).filter(t => t.status === 'Pending').length;
  const inProgressCount = (state.tasks || []).filter(t => t.status === 'In-Progress').length;
  const completedCount = (state.tasks || []).filter(t => t.status === 'Completed').length;
  const totalTasks = (state.tasks || []).length;
  const isTaskCompEmpty = totalTasks === 0;

  if (!toggleChartEmptyState('chartTaskCompletion', 'empty-chartTaskCompletion', isTaskCompEmpty)) {
    const completionCtx = document.getElementById('chartTaskCompletion').getContext('2d');
    charts.taskCompletionAnalytics = new Chart(completionCtx, {
      type: 'doughnut',
      data: {
        labels: ['Pending', 'In Progress', 'Completed'],
        datasets: [{
          data: [pendingCount, inProgressCount, completedCount],
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
  }

  // 2b. Task Status Distribution (Dashboard)
  safeDestroyCanvas('chartTaskCompletionDashboard', 'taskCompletionDashboard');
  if (!toggleChartEmptyState('chartTaskCompletionDashboard', 'empty-chartTaskCompletionDashboard', isTaskCompEmpty)) {
    const compDashCtx = document.getElementById('chartTaskCompletionDashboard').getContext('2d');
    charts.taskCompletionDashboard = new Chart(compDashCtx, {
      type: 'doughnut',
      data: {
        labels: ['Pending', 'In Progress', 'Completed'],
        datasets: [{
          data: [pendingCount, inProgressCount, completedCount],
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
  }

  // 3. Employee Efficiency (Horizontal Bar Chart)
  safeDestroyCanvas('chartEmployeeEfficiency', 'efficiency');
  const empNames = (state.employees || []).map(e => e.name);
  const empScores = (state.employees || []).map(e => e.score);
  const isEmpEffEmpty = empNames.length === 0;

  if (!toggleChartEmptyState('chartEmployeeEfficiency', 'empty-chartEmployeeEfficiency', isEmpEffEmpty)) {
    const effCtx = document.getElementById('chartEmployeeEfficiency').getContext('2d');
    charts.efficiency = new Chart(effCtx, {
      type: 'bar',
      data: {
        labels: empNames,
        datasets: [{
          label: 'Capability Rating',
          data: empScores,
          backgroundColor: 'rgba(99, 102, 241, 0.75)',
          hoverBackgroundColor: '#6366f1',
          borderRadius: 6,
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
  }

  // 4. Workload Distribution (Bar Chart)
  safeDestroyCanvas('chartWorkloadDistribution', 'workload');
  const empWorkloads = (state.employees || []).map(e => e.active_tasks || 0);
  const isWorkloadEmpty = empNames.length === 0;

  if (!toggleChartEmptyState('chartWorkloadDistribution', 'empty-chartWorkloadDistribution', isWorkloadEmpty)) {
    const wlCtx = document.getElementById('chartWorkloadDistribution').getContext('2d');
    charts.workload = new Chart(wlCtx, {
      type: 'bar',
      data: {
        labels: empNames,
        datasets: [{
          label: 'Active Tasks Assigned',
          data: empWorkloads,
          backgroundColor: 'rgba(14, 165, 233, 0.75)',
          hoverBackgroundColor: '#0ea5e9',
          borderRadius: 6,
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: { grid: { display: false }, ticks: { color: textColor } },
          y: { grid: { color: gridColor }, ticks: { color: textColor, precision: 0 }, min: 0 }
        }
      }
    });
  }

  // 5. Task Priority Distribution (Polar Area Chart)
  safeDestroyCanvas('chartTaskPriority', 'priority');
  const highTasks = (state.tasks || []).filter(t => t.priority === 'High').length;
  const medTasks = (state.tasks || []).filter(t => t.priority === 'Medium').length;
  const lowTasks = (state.tasks || []).filter(t => t.priority === 'Low').length;
  const isPriorityEmpty = totalTasks === 0;

  if (!toggleChartEmptyState('chartTaskPriority', 'empty-chartTaskPriority', isPriorityEmpty)) {
    const priorityCtx = document.getElementById('chartTaskPriority').getContext('2d');
    charts.priority = new Chart(priorityCtx, {
      type: 'polarArea',
      data: {
        labels: ['High', 'Medium', 'Low'],
        datasets: [{
          data: [highTasks, medTasks, lowTasks],
          backgroundColor: [
            'rgba(239, 68, 68, 0.7)',
            'rgba(245, 158, 11, 0.7)',
            'rgba(99, 102, 241, 0.7)'
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
            ticks: { backdropColor: 'transparent', color: textColor, precision: 0 }
          }
        }
      }
    });
  }

  // 6. Performance vs Experience Scatter Matrix
  safeDestroyCanvas('chartEfficiencyComparison', 'efficiencyComparison');
  const scatterData = (state.employees || []).map(e => ({
    x: e.experience,
    y: e.score,
    label: e.name
  }));
  const isScatterEmpty = scatterData.length === 0;

  if (!toggleChartEmptyState('chartEfficiencyComparison', 'empty-chartEfficiencyComparison', isScatterEmpty)) {
    const effCompCtx = document.getElementById('chartEfficiencyComparison').getContext('2d');
    charts.efficiencyComparison = new Chart(effCompCtx, {
      type: 'scatter',
      data: {
        datasets: [{
          label: 'Employees',
          data: scatterData,
          backgroundColor: '#10b981',
          borderColor: '#059669',
          pointRadius: 8,
          pointHoverRadius: 10
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
            min: 0
          },
          y: { 
            title: { display: true, text: 'Performance Rating', color: textColor }, 
            grid: { color: gridColor }, 
            ticks: { color: textColor },
            min: 0,
            max: 10
          }
        }
      }
    });
  }

  // 7. Completion Trend (Line Chart)
  safeDestroyCanvas('chartCompletionTrends', 'trends');
  const isTrendEmpty = completedCount === 0 && (!state.submissions || state.submissions.length === 0);

  if (!toggleChartEmptyState('chartCompletionTrends', 'empty-chartCompletionTrends', isTrendEmpty)) {
    let trendLabels = [];
    let trendData = [];
    
    if (state.submissions && state.submissions.length > 0) {
      const dateMap = {};
      state.submissions.forEach(sub => {
        const d = sub.date ? sub.date.split(' ')[0] : 'Today';
        dateMap[d] = (dateMap[d] || 0) + 1;
      });

      const sortedDates = Object.keys(dateMap).sort();
      let cumSum = 0;
      sortedDates.forEach(d => {
        cumSum += dateMap[d];
        trendLabels.push(d);
        trendData.push(cumSum);
      });
    } else {
      trendLabels = ['Start', 'Current'];
      trendData = [0, completedCount];
    }

    const trendsCtx = document.getElementById('chartCompletionTrends').getContext('2d');
    charts.trends = new Chart(trendsCtx, {
      type: 'line',
      data: {
        labels: trendLabels,
        datasets: [{
          label: 'Cumulative Completed Tasks',
          data: trendData,
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.15)',
          tension: 0.3,
          borderWidth: 3,
          fill: true,
          pointRadius: 5
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top', labels: { color: textColor } }
        },
        scales: {
          x: { grid: { color: gridColor }, ticks: { color: textColor } },
          y: { grid: { color: gridColor }, ticks: { color: textColor, precision: 0 }, min: 0 }
        }
      }
    });
  }
}

// --- NOTIFICATIONS SYSTEM ---
let unreadNotifications = 0;

function setupNotificationListeners() {
  const notifBtn = document.getElementById('notificationBtn');
  const dropdown = document.getElementById('notificationDropdown');
  const markReadBtn = document.getElementById('markReadBtn');

  if (notifBtn && dropdown) {
    notifBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const isVisible = dropdown.style.display === 'block';
      dropdown.style.display = isVisible ? 'none' : 'block';
      if (!isVisible) {
        unreadNotifications = 0;
        updateNotificationBadge();
      }
    });

    document.addEventListener('click', (e) => {
      if (dropdown && !dropdown.contains(e.target) && !notifBtn.contains(e.target)) {
        dropdown.style.display = 'none';
      }
    });
  }

  if (markReadBtn) {
    markReadBtn.addEventListener('click', () => {
      unreadNotifications = 0;
      updateNotificationBadge();
      if (dropdown) dropdown.style.display = 'none';
      showToast('All notifications marked as read', 'info');
    });
  }
}

function updateNotificationBadge() {
  const badge = document.getElementById('notificationBadge');
  if (!badge) return;
  if (unreadNotifications > 0) {
    badge.textContent = unreadNotifications;
    badge.style.display = 'inline-flex';
  } else {
    badge.style.display = 'none';
  }
}

function updateNotificationsPanel() {
  const list = document.getElementById('notificationList');
  if (!list) return;
  list.innerHTML = '';

  const notifications = [];

  // 1. Deadline alerts from real task state
  const today = new Date().toISOString().split('T')[0];
  (state.tasks || []).forEach(t => {
    if (t.status !== 'Completed') {
      if (t.deadline < today) {
        notifications.push({
          title: `Overdue Task Alert`,
          message: `'${t.title}' passed deadline (${t.deadline}).`,
          time: 'Action Required',
          type: 'warning',
          icon: 'fa-triangle-exclamation',
          color: 'var(--danger)'
        });
      } else if (t.deadline === today) {
        notifications.push({
          title: `Deadline Due Today`,
          message: `'${t.title}' is due today!`,
          time: 'Today',
          type: 'info',
          icon: 'fa-clock',
          color: 'var(--warning)'
        });
      }
    }
  });

  // 2. Real activity logs
  (state.activities || []).slice(0, 10).forEach(act => {
    const meta = getActivityMeta(act.type);
    notifications.push({
      title: meta.badge,
      message: act.message,
      time: act.timestamp,
      type: 'activity',
      icon: meta.icon,
      color: meta.color
    });
  });

  if (notifications.length === 0) {
    list.innerHTML = `
      <div style="text-align: center; color: var(--text-muted); padding: 24px 12px; font-size: 0.85rem;">
        <i class="fa-solid fa-bell-slash" style="font-size: 1.8rem; display: block; margin-bottom: 8px;"></i>
        No unread system notifications.
      </div>
    `;
    return;
  }

  notifications.slice(0, 8).forEach(n => {
    const item = document.createElement('div');
    item.className = 'notification-item';
    item.style.cssText = `display: flex; gap: 10px; padding: 10px; border-radius: 8px; background: rgba(255,255,255,0.03); border: 1px solid var(--border-color); font-size: 0.8rem; align-items: flex-start;`;
    
    const iconColor = n.color || 'var(--primary)';
    item.innerHTML = `
      <div style="color: ${iconColor}; font-size: 1.1rem; margin-top: 2px;">
        <i class="fa-solid ${n.icon}"></i>
      </div>
      <div style="flex: 1;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
          <span style="font-weight: 700; color: var(--text-primary);">${n.title}</span>
          <span style="font-size: 0.7rem; color: var(--text-muted);">${n.time}</span>
        </div>
        <div style="color: var(--text-secondary); line-height: 1.3;">${n.message}</div>
      </div>
    `;
    list.appendChild(item);
  });

  unreadNotifications = Math.min(9, notifications.length);
  updateNotificationBadge();
}

function openEmployeeProfile(emp) {
  const backdrop = document.getElementById('drawerBackdrop');
  const drawer = document.getElementById('employeeDrawer');
  const drawerBody = document.getElementById('drawerBody');
  
  if (!backdrop || !drawer || !drawerBody) return;
  
  const avatarLetter = emp.name.charAt(0);
  const percent = Math.min(100, Math.max(0, (emp.score / 10.0) * 100));
  let scoreColor = 'var(--success)';
  if (emp.score < 7.0) scoreColor = 'var(--danger)';
  else if (emp.score < 8.5) scoreColor = 'var(--warning)';

  // Filter performance history for this employee
  const empIdClean = emp.id.replace('emp-', '');
  const empPerfLogs = (state.performance_history || []).filter(ph => 
    String(ph.employeeId) === String(emp.id) || String(ph.employee_id) === String(empIdClean) || ph.employeeName === emp.name
  );

  // Filter activity logs for this employee
  const empActivities = (state.activities || []).filter(act => 
    act.message.toLowerCase().includes(emp.name.toLowerCase())
  );

  let perfHistoryHTML = `<div style="font-size: 0.8rem; color: var(--text-muted); padding: 8px 0;">No score adjustments recorded yet.</div>`;
  if (empPerfLogs.length > 0) {
    perfHistoryHTML = empPerfLogs.map(ph => `
      <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.02); border: 1px solid var(--border-color); padding: 8px 12px; border-radius: 6px; font-size: 0.78rem;">
        <div>
          <span style="font-weight: 700; color: var(--text-primary);">${ph.reason || 'Rating update'}</span>
          <span style="display: block; font-size: 0.7rem; color: var(--text-muted);">${ph.date}</span>
        </div>
        <span style="font-weight: 800; font-family: monospace; color: ${ph.newScore >= ph.oldScore ? 'var(--success)' : 'var(--danger)'}; font-size: 0.85rem;">
          ${ph.oldScore} → ${ph.newScore}
        </span>
      </div>
    `).join('');
  }

  let activityTimelineHTML = `<div style="font-size: 0.8rem; color: var(--text-muted); padding: 8px 0;">No recent event activity for ${emp.name}.</div>`;
  if (empActivities.length > 0) {
    activityTimelineHTML = empActivities.slice(0, 5).map(act => {
      const meta = getActivityMeta(act.type);
      return `
        <div style="display: flex; gap: 8px; font-size: 0.78rem; align-items: flex-start; padding: 6px 0; border-bottom: 1px dashed var(--border-color);">
          <i class="fa-solid ${meta.icon}" style="color: ${meta.color}; font-size: 0.9rem; margin-top: 2px;"></i>
          <div style="flex: 1;">
            <div style="color: var(--text-primary); line-height: 1.3;">${act.message}</div>
            <div style="font-size: 0.68rem; color: var(--text-muted);">${act.timestamp}</div>
          </div>
        </div>
      `;
    }).join('');
  }

  drawerBody.innerHTML = `
    <div style="display: flex; flex-direction: column; align-items: center; text-align: center; margin-bottom: 20px; border-bottom: 1px solid var(--border-color); padding-bottom: 16px;">
      <div class="profile-avatar" style="width: 72px; height: 72px; border-radius: 50%; font-size: 2rem; display: flex; align-items: center; justify-content: center; background: var(--primary-glow); color: var(--primary); margin-bottom: 10px; font-weight: 800;">
        ${avatarLetter}
      </div>
      <h2 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 2px; color: var(--text-primary);">${emp.name}</h2>
      <p style="color: var(--text-muted); font-size: 0.82rem; margin-bottom: 8px;">${emp.role} • ${emp.department}</p>
      <span class="status-badge ${emp.availability === 'Busy' ? 'in-progress' : 'completed'}" style="padding: 3px 10px; border-radius: 6px; font-size: 0.75rem;">
        ● ${emp.availability || 'Available'}
      </span>
    </div>

    <div style="display: flex; flex-direction: column; gap: 16px;">
      
      <!-- Performance Score Bar -->
      <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-color); border-radius: 10px; padding: 14px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
          <span style="font-size: 0.8rem; font-weight: 600; color: var(--text-secondary);"><i class="fa-solid fa-star" style="color: var(--warning); margin-right: 4px;"></i> Capability Rating</span>
          <span style="font-size: 1.1rem; font-weight: 800; color: ${scoreColor};">${emp.score.toFixed(1)} / 10.0</span>
        </div>
        <div style="height: 8px; width: 100%; background: var(--border-color); border-radius: 4px; overflow: hidden;">
          <div style="height: 100%; width: ${percent}%; background-color: ${scoreColor}; transition: width 0.4s ease;"></div>
        </div>
      </div>

      <!-- Skill Chips -->
      <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-color); border-radius: 10px; padding: 14px;">
        <span style="font-size: 0.75rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; display: block; margin-bottom: 8px;">Technical Skills</span>
        <div style="display: flex; flex-wrap: wrap; gap: 6px;">
          ${emp.skills.map(s => `<span class="skill-tag" style="position: static;">${s}</span>`).join('')}
        </div>
      </div>

      <!-- Mini Metrics Grid -->
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
        <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-color); border-radius: 8px; padding: 10px; text-align: center;">
          <span style="font-size: 0.72rem; color: var(--text-muted); display: block;">Active Tasks</span>
          <span style="font-size: 1.2rem; font-weight: 800; color: var(--text-primary);">${emp.active_tasks}</span>
        </div>
        <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-color); border-radius: 8px; padding: 10px; text-align: center;">
          <span style="font-size: 0.72rem; color: var(--text-muted); display: block;">Completed Tasks</span>
          <span style="font-size: 1.2rem; font-weight: 800; color: var(--success);">${emp.completed_tasks}</span>
        </div>
        <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-color); border-radius: 8px; padding: 10px; text-align: center;">
          <span style="font-size: 0.72rem; color: var(--text-muted); display: block;">Success Rate</span>
          <span style="font-size: 1.2rem; font-weight: 800; color: var(--info);">${emp.success_rate}%</span>
        </div>
        <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-color); border-radius: 8px; padding: 10px; text-align: center;">
          <span style="font-size: 0.72rem; color: var(--text-muted); display: block;">Experience</span>
          <span style="font-size: 1.2rem; font-weight: 800; color: var(--primary);">${emp.experience} Yrs</span>
        </div>
      </div>

      <!-- Current & Last Task -->
      <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-color); border-radius: 10px; padding: 14px; display: flex; flex-direction: column; gap: 10px;">
        <div>
          <span style="font-size: 0.72rem; color: var(--text-muted); display: block; margin-bottom: 2px;">Current Assigned Task</span>
          <span style="font-weight: 700; font-size: 0.85rem; color: var(--text-primary);"><i class="fa-solid fa-thumbtack" style="color: var(--primary); margin-right: 4px;"></i>${emp.current_task || 'None'}</span>
        </div>
        <div>
          <span style="font-size: 0.72rem; color: var(--text-muted); display: block; margin-bottom: 2px;">Last Completed Task</span>
          <span style="font-weight: 600; font-size: 0.85rem; color: var(--text-secondary);"><i class="fa-solid fa-circle-check" style="color: var(--success); margin-right: 4px;"></i>${emp.last_completed_task || 'None'}</span>
        </div>
      </div>

      <!-- Performance History Log -->
      <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-color); border-radius: 10px; padding: 14px;">
        <span style="font-size: 0.75rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; display: block; margin-bottom: 10px;">
          <i class="fa-solid fa-chart-line" style="color: var(--primary); margin-right: 4px;"></i> Performance Score History
        </span>
        <div style="display: flex; flex-direction: column; gap: 6px;">
          ${perfHistoryHTML}
        </div>
      </div>

      <!-- Employee Activity Timeline -->
      <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-color); border-radius: 10px; padding: 14px;">
        <span style="font-size: 0.75rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; display: block; margin-bottom: 10px;">
          <i class="fa-solid fa-timeline" style="color: var(--info); margin-right: 4px;"></i> Recent Activity
        </span>
        <div style="display: flex; flex-direction: column; gap: 4px;">
          ${activityTimelineHTML}
        </div>
      </div>

    </div>
  `;
  
  backdrop.classList.add('show');
  drawer.classList.add('show');
}

function closeEmployeeProfile() {
  const backdrop = document.getElementById('drawerBackdrop');
  const drawer = document.getElementById('employeeDrawer');
  
  if (backdrop && drawer) {
    backdrop.classList.remove('show');
    drawer.classList.remove('show');
  }
}

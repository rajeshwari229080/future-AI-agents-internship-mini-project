/**
 * EWB EduTech Student Record Management System
 * Single-Page Administrative Frontend Logic
 */

(function () {
  'use strict';

  // State Management
  const state = {
    skip: 0,
    limit: 10,
    search: '',
    course: 'all',
    total: 0,
    students: [],
    courses: [],
    selectedStudent: null,
    isEditing: false,
    aiAvailable: false,
  };

  // DOM Elements Cache
  const elements = {
    // Stats
    statTotalStudents: document.getElementById('stat-total-students'),
    statTotalCourses: document.getElementById('stat-total-courses'),
    statRecentCount: document.getElementById('stat-recent-count'),
    courseBreakdownList: document.getElementById('course-breakdown-list'),

    // Table & Filters
    tableBody: document.getElementById('students-table-body'),
    tableLoading: document.getElementById('table-loading-state'),
    emptyState: document.getElementById('empty-state'),
    backendErrorState: document.getElementById('backend-error-state'),
    recordCountIndicator: document.getElementById('record-count-indicator'),
    searchInput: document.getElementById('search-input'),
    searchClearBtn: document.getElementById('search-clear-btn'),
    courseFilter: document.getElementById('course-filter'),
    limitSelect: document.getElementById('limit-select'),
    btnRefresh: document.getElementById('btn-refresh'),
    btnRetryFetch: document.getElementById('btn-retry-fetch'),
    btnPrevPage: document.getElementById('btn-prev-page'),
    btnNextPage: document.getElementById('btn-next-page'),
    pageIndicator: document.getElementById('page-indicator'),
    paginationText: document.getElementById('pagination-text'),

    // Action Buttons
    btnAddStudent: document.getElementById('btn-add-student'),
    btnEmptyAdd: document.getElementById('btn-empty-add'),

    // Add / Edit Modal
    studentModal: document.getElementById('student-modal'),
    modalTitle: document.getElementById('modal-title'),
    studentForm: document.getElementById('student-form'),
    studentIdInput: document.getElementById('student-id'),
    nameInput: document.getElementById('student-name'),
    dobInput: document.getElementById('student-dob'),
    emailInput: document.getElementById('student-email'),
    phoneInput: document.getElementById('student-phone'),
    courseInput: document.getElementById('student-course'),
    addressInput: document.getElementById('student-address'),
    enrollmentDateInput: document.getElementById('student-enrollment-date'),
    btnSaveStudent: document.getElementById('btn-save-student'),
    generalFormError: document.getElementById('general-form-error'),

    // Profile Modal
    profileModal: document.getElementById('profile-modal'),
    profileAvatar: document.getElementById('profile-avatar'),
    profileName: document.getElementById('profile-name'),
    profileIdBadge: document.getElementById('profile-id-badge'),
    profileCourseBadge: document.getElementById('profile-course-badge'),
    profileDob: document.getElementById('profile-dob'),
    profileEnrollment: document.getElementById('profile-enrollment'),
    profileEmail: document.getElementById('profile-email'),
    profilePhone: document.getElementById('profile-phone'),
    profileAddress: document.getElementById('profile-address'),
    profileCreated: document.getElementById('profile-created'),
    profileUpdated: document.getElementById('profile-updated'),
    profileBtnEdit: document.getElementById('profile-btn-edit'),

    // Delete Modal
    deleteModal: document.getElementById('delete-modal'),
    deleteStudentName: document.getElementById('delete-student-name'),
    deleteStudentId: document.getElementById('delete-student-id'),
    btnConfirmDelete: document.getElementById('btn-confirm-delete'),

    // AI Assistant
    btnOpenAi: document.getElementById('btn-open-ai'),
    btnCloseAi: document.getElementById('btn-close-ai'),
    aiDrawer: document.getElementById('ai-drawer'),
    aiStatusIndicator: document.getElementById('ai-status-indicator'),
    aiStatusBadge: document.getElementById('ai-status-badge'),
    aiAskForm: document.getElementById('ai-ask-form'),
    aiQuestionInput: document.getElementById('ai-question-input'),
    aiConversation: document.getElementById('ai-conversation'),
    btnSendAi: document.getElementById('btn-send-ai'),

    // Toast Container
    toastContainer: document.getElementById('toast-container'),
  };

  // Utility: Sanitize text for HTML injection safety
  function escapeHtml(str) {
    if (!str && str !== 0) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  // Utility: Date formatter
  function formatDate(isoStr) {
    if (!isoStr) return '--';
    try {
      const parts = isoStr.split('-');
      if (parts.length === 3) {
        const d = new Date(parts[0], parts[1] - 1, parts[2]);
        return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
      }
      return isoStr;
    } catch {
      return isoStr;
    }
  }

  // Toast Notification System
  function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <span>${escapeHtml(message)}</span>
      <button class="toast-close" aria-label="Close notification">&times;</button>
    `;
    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', () => toast.remove());

    elements.toastContainer.appendChild(toast);
    setTimeout(() => {
      if (toast.parentElement) toast.remove();
    }, 4500);
  }

  // Fetch Dashboard Statistics
  async function fetchStats() {
    try {
      const response = await fetch('/students/stats/summary');
      if (!response.ok) throw new Error('Failed to fetch statistics');
      const data = await response.json();

      elements.statTotalStudents.textContent = data.total_students;
      elements.statTotalCourses.textContent = data.total_courses;
      elements.statRecentCount.textContent = (data.recent_students || []).length;

      // Render Course Distribution Pills
      if (data.courses_breakdown && data.courses_breakdown.length > 0) {
        elements.courseBreakdownList.innerHTML = data.courses_breakdown
          .map(
            (c) =>
              `<span class="course-tag-pill" title="${c.count} student(s)">${escapeHtml(c.course)}: ${c.count}</span>`
          )
          .join('');
      } else {
        elements.courseBreakdownList.innerHTML = '<span class="text-muted">No courses enrolled</span>';
      }
    } catch (err) {
      console.warn('Stats fetch warning:', err);
    }
  }

  // Fetch Distinct Courses for Filter Dropdown
  async function fetchCourses() {
    try {
      const response = await fetch('/students/courses');
      if (!response.ok) return;
      const courses = await response.json();
      state.courses = courses;

      const currentSelected = elements.courseFilter.value;
      elements.courseFilter.innerHTML = '<option value="all">All Courses</option>';
      courses.forEach((c) => {
        const opt = document.createElement('option');
        opt.value = c;
        opt.textContent = c;
        if (c === currentSelected) opt.selected = true;
        elements.courseFilter.appendChild(opt);
      });
    } catch (err) {
      console.warn('Courses fetch error:', err);
    }
  }

  // Fetch Paginated Students Table
  async function fetchStudents() {
    elements.tableLoading.classList.remove('hidden');
    elements.backendErrorState.classList.add('hidden');
    elements.emptyState.classList.add('hidden');

    const params = new URLSearchParams({
      skip: state.skip.toString(),
      limit: state.limit.toString(),
    });

    if (state.search.trim()) {
      params.append('search', state.search.trim());
    }
    if (state.course && state.course !== 'all') {
      params.append('course', state.course);
    }

    try {
      const response = await fetch(`/students?${params.toString()}`);
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      const data = await response.json();
      state.students = data.items;
      state.total = data.total;

      renderTable();
      renderPagination();
    } catch (error) {
      console.error('Fetch students error:', error);
      elements.tableBody.innerHTML = '';
      elements.backendErrorState.classList.remove('hidden');
      elements.recordCountIndicator.textContent = 'Error';
    } finally {
      elements.tableLoading.classList.add('hidden');
    }
  }

  // Render Students Table Rows
  function renderTable() {
    elements.recordCountIndicator.textContent = `${state.total} record${state.total === 1 ? '' : 's'}`;

    if (state.students.length === 0) {
      elements.tableBody.innerHTML = '';
      elements.emptyState.classList.remove('hidden');
      return;
    }

    elements.emptyState.classList.add('hidden');
    elements.tableBody.innerHTML = state.students
      .map((student) => {
        const initials = student.name
          .split(' ')
          .map((n) => n[0])
          .slice(0, 2)
          .join('')
          .toUpperCase() || 'ST';

        return `
          <tr data-student-id="${student.id}">
            <td><strong style="color: var(--slate-500);">#${student.id}</strong></td>
            <td>
              <div class="student-name-cell">
                <div class="table-avatar">${escapeHtml(initials)}</div>
                <div class="name-primary">${escapeHtml(student.name)}</div>
              </div>
            </td>
            <td>${formatDate(student.date_of_birth)}</td>
            <td>
              <div class="contact-cell">
                ${
                  student.email
                    ? `<span class="contact-email">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
                        ${escapeHtml(student.email)}
                       </span>`
                    : ''
                }
                ${
                  student.phone
                    ? `<span class="contact-phone">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
                        ${escapeHtml(student.phone)}
                       </span>`
                    : ''
                }
              </div>
            </td>
            <td>
              <span class="badge ${student.course ? 'badge-course' : 'badge-unassigned'}">
                ${escapeHtml(student.course || 'Unassigned')}
              </span>
            </td>
            <td>${formatDate(student.enrollment_date)}</td>
            <td>
              <div class="actions-cell">
                <button class="btn-icon" data-action="view" data-id="${student.id}" title="View Student Profile">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                </button>
                <button class="btn-icon" data-action="edit" data-id="${student.id}" title="Edit Student Record">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                </button>
                <button class="btn-icon btn-icon-danger" data-action="delete" data-id="${student.id}" title="Delete Student Record">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>
                </button>
              </div>
            </td>
          </tr>
        `;
      })
      .join('');
  }

  // Update Pagination Controls
  function renderPagination() {
    const start = state.total === 0 ? 0 : state.skip + 1;
    const end = Math.min(state.skip + state.limit, state.total);
    elements.paginationText.textContent = `Showing ${start}-${end} of ${state.total} students`;

    const currentPage = Math.floor(state.skip / state.limit) + 1;
    const totalPages = Math.max(1, Math.ceil(state.total / state.limit));

    elements.pageIndicator.textContent = `Page ${currentPage} of ${totalPages}`;
    elements.btnPrevPage.disabled = state.skip === 0;
    elements.btnNextPage.disabled = state.skip + state.limit >= state.total;
  }

  // Reset Form Errors
  function clearFormErrors() {
    ['name', 'dob', 'email', 'phone', 'course', 'address', 'enrollment_date'].forEach((field) => {
      const errEl = document.getElementById(`error-${field}`);
      if (errEl) errEl.textContent = '';
      const inputEl = document.getElementById(`student-${field}`);
      if (inputEl) inputEl.classList.remove('is-invalid');
    });
    elements.generalFormError.classList.add('hidden');
    elements.generalFormError.textContent = '';
  }

  // Open Modal in Add Mode
  function openAddModal() {
    state.isEditing = false;
    state.selectedStudent = null;
    elements.modalTitle.textContent = 'Add Student Record';
    elements.studentForm.reset();
    elements.studentIdInput.value = '';
    clearFormErrors();
    elements.studentModal.classList.remove('hidden');
    elements.nameInput.focus();
  }

  // Open Modal in Edit Mode
  function openEditModal(student) {
    state.isEditing = true;
    state.selectedStudent = student;
    elements.modalTitle.textContent = `Edit Student (ID: #${student.id})`;
    clearFormErrors();

    elements.studentIdInput.value = student.id;
    elements.nameInput.value = student.name || '';
    elements.dobInput.value = student.date_of_birth || '';
    elements.emailInput.value = student.email || '';
    elements.phoneInput.value = student.phone || '';
    elements.courseInput.value = student.course || '';
    elements.addressInput.value = student.address || '';
    elements.enrollmentDateInput.value = student.enrollment_date || '';

    elements.studentModal.classList.remove('hidden');
    elements.nameInput.focus();
  }

  // Handle Form Submission (Create / Update)
  async function handleStudentFormSubmit(e) {
    e.preventDefault();
    clearFormErrors();

    const name = elements.nameInput.value.trim();
    const dob = elements.dobInput.value;
    const email = elements.emailInput.value.trim();
    const phone = elements.phoneInput.value.trim();
    const course = elements.courseInput.value.trim();
    const address = elements.addressInput.value.trim();
    const enrollmentDate = elements.enrollmentDateInput.value;

    // Client-side quick checks
    let hasError = false;
    if (!name) {
      document.getElementById('error-name').textContent = 'Full name is required.';
      elements.nameInput.classList.add('is-invalid');
      hasError = true;
    }
    if (!dob) {
      document.getElementById('error-dob').textContent = 'Date of birth is required.';
      elements.dobInput.classList.add('is-invalid');
      hasError = true;
    }
    if (!email && !phone) {
      document.getElementById('error-email').textContent = 'Provide email or phone.';
      document.getElementById('error-phone').textContent = 'Provide email or phone.';
      hasError = true;
    }

    if (hasError) return;

    const payload = {
      name,
      date_of_birth: dob,
      email: email || null,
      phone: phone || null,
      course: course || null,
      address: address || null,
      enrollment_date: enrollmentDate || null,
    };

    // Save loading state
    elements.btnSaveStudent.disabled = true;
    elements.btnSaveStudent.querySelector('.btn-text').textContent = 'Saving...';

    const url = state.isEditing ? `/students/${elements.studentIdInput.value}` : '/students';
    const method = state.isEditing ? 'PUT' : 'POST';

    try {
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 422 && data.errors) {
          data.errors.forEach((err) => {
            if (err.field.includes('name')) document.getElementById('error-name').textContent = err.message;
            else if (err.field.includes('date_of_birth')) document.getElementById('error-dob').textContent = err.message;
            else if (err.field.includes('email')) document.getElementById('error-email').textContent = err.message;
            else if (err.field.includes('phone')) document.getElementById('error-phone').textContent = err.message;
            else if (err.field.includes('course')) document.getElementById('error-course').textContent = err.message;
            else if (err.field.includes('enrollment_date')) document.getElementById('error-enrollment_date').textContent = err.message;
            else elements.generalFormError.textContent = err.message;
          });
          if (elements.generalFormError.textContent) elements.generalFormError.classList.remove('hidden');
        } else {
          elements.generalFormError.textContent = data.detail || 'Could not save student record.';
          elements.generalFormError.classList.remove('hidden');
        }
        return;
      }

      // Success
      elements.studentModal.classList.add('hidden');
      showToast(state.isEditing ? 'Student record updated successfully.' : 'New student registered successfully.', 'success');
      await Promise.all([fetchStudents(), fetchStats(), fetchCourses()]);
    } catch (err) {
      console.error('Save error:', err);
      elements.generalFormError.textContent = 'Network error: could not connect to server.';
      elements.generalFormError.classList.remove('hidden');
    } finally {
      elements.btnSaveStudent.disabled = false;
      elements.btnSaveStudent.querySelector('.btn-text').textContent = 'Save Student';
    }
  }

  // View Student Profile
  async function openProfileModal(studentId) {
    try {
      const response = await fetch(`/students/${studentId}`);
      if (!response.ok) throw new Error('Student not found');
      const student = await response.json();
      state.selectedStudent = student;

      const initials = student.name
        .split(' ')
        .map((n) => n[0])
        .slice(0, 2)
        .join('')
        .toUpperCase() || 'ST';

      elements.profileAvatar.textContent = initials;
      elements.profileName.textContent = student.name;
      elements.profileIdBadge.textContent = `ID: #${student.id}`;
      elements.profileCourseBadge.textContent = student.course || 'Unassigned';
      elements.profileDob.textContent = formatDate(student.date_of_birth);
      elements.profileEnrollment.textContent = formatDate(student.enrollment_date);
      elements.profileEmail.textContent = student.email || '--';
      elements.profilePhone.textContent = student.phone || '--';
      elements.profileAddress.textContent = student.address || 'No address registered';
      elements.profileCreated.textContent = student.created_at ? new Date(student.created_at).toLocaleString() : '--';
      elements.profileUpdated.textContent = student.updated_at ? new Date(student.updated_at).toLocaleString() : '--';

      elements.profileModal.classList.remove('hidden');
    } catch (err) {
      showToast('Could not load student profile.', 'error');
    }
  }

  // Open Delete Confirmation
  function openDeleteModal(student) {
    state.selectedStudent = student;
    elements.deleteStudentName.textContent = student.name;
    elements.deleteStudentId.textContent = student.id;
    elements.deleteModal.classList.remove('hidden');
  }

  // Confirm Delete Action
  async function confirmDelete() {
    if (!state.selectedStudent) return;
    elements.btnConfirmDelete.disabled = true;
    elements.btnConfirmDelete.querySelector('.btn-text').textContent = 'Deleting...';

    try {
      const response = await fetch(`/students/${state.selectedStudent.id}`, { method: 'DELETE' });
      if (response.status === 204) {
        elements.deleteModal.classList.add('hidden');
        showToast(`Student #${state.selectedStudent.id} deleted successfully.`, 'success');
        await Promise.all([fetchStudents(), fetchStats(), fetchCourses()]);
      } else {
        throw new Error('Failed to delete student.');
      }
    } catch (err) {
      showToast(err.message || 'Error deleting student.', 'error');
    } finally {
      elements.btnConfirmDelete.disabled = false;
      elements.btnConfirmDelete.querySelector('.btn-text').textContent = 'Permanently Delete';
    }
  }

  // AI Assistant: Check Status
  async function checkAIStatus() {
    try {
      const response = await fetch('/ai/status');
      if (response.ok) {
        const data = await response.json();
        state.aiAvailable = data.available;
        if (data.available) {
          elements.aiStatusIndicator.className = 'status-indicator-dot online';
          elements.aiStatusIndicator.title = `Ollama ${data.version} (${data.model}) Ready`;
          elements.aiStatusBadge.className = 'ai-status-tag online';
          elements.aiStatusBadge.textContent = `● Model: ${data.model}`;
        } else {
          elements.aiStatusIndicator.className = 'status-indicator-dot offline';
          elements.aiStatusIndicator.title = 'Ollama offline (Direct factual stats mode)';
          elements.aiStatusBadge.className = 'ai-status-tag';
          elements.aiStatusBadge.textContent = '○ Offline (Direct metrics mode)';
        }
      }
    } catch {
      elements.aiStatusIndicator.className = 'status-indicator-dot offline';
      elements.aiStatusBadge.textContent = '○ Server disconnected';
    }
  }

  // AI Assistant: Send Question
  async function handleAIQuestion(e) {
    if (e) e.preventDefault();
    const question = elements.aiQuestionInput.value.trim();
    if (!question) return;

    // Append User Message
    const userMsg = document.createElement('div');
    userMsg.className = 'ai-msg ai-msg-user';
    userMsg.textContent = question;
    elements.aiConversation.appendChild(userMsg);

    elements.aiQuestionInput.value = '';
    elements.btnSendAi.disabled = true;

    // Thinking Indicator
    const thinkingMsg = document.createElement('div');
    thinkingMsg.className = 'ai-msg ai-msg-assistant';
    thinkingMsg.innerHTML = '<span class="text-muted">Analyzing records...</span>';
    elements.aiConversation.appendChild(thinkingMsg);
    elements.aiConversation.scrollTop = elements.aiConversation.scrollHeight;

    try {
      const response = await fetch('/ai/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });

      const data = await response.json();
      thinkingMsg.innerHTML = `
        <div>
          ${
            data.service_available
              ? '<span class="ai-msg-grounded-pill">● Grounded in Records</span>'
              : '<span class="ai-msg-fallback-pill">Calculated from Database</span>'
          }
          <div style="margin-top: 0.35rem;">${escapeHtml(data.answer)}</div>
        </div>
      `;
    } catch (err) {
      thinkingMsg.innerHTML = '<span style="color: var(--danger-main);">Failed to contact AI service.</span>';
    } finally {
      elements.btnSendAi.disabled = false;
      elements.aiConversation.scrollTop = elements.aiConversation.scrollHeight;
    }
  }

  // Event Listeners Setup
  function setupEventListeners() {
    // Search with debounce
    let searchDebounceTimer = null;
    elements.searchInput.addEventListener('input', (e) => {
      clearTimeout(searchDebounceTimer);
      const val = e.target.value;
      if (val) elements.searchClearBtn.classList.remove('hidden');
      else elements.searchClearBtn.classList.add('hidden');

      searchDebounceTimer = setTimeout(() => {
        state.search = val;
        state.skip = 0;
        fetchStudents();
      }, 300);
    });

    elements.searchClearBtn.addEventListener('click', () => {
      elements.searchInput.value = '';
      elements.searchClearBtn.classList.add('hidden');
      state.search = '';
      state.skip = 0;
      fetchStudents();
    });

    // Course Filter
    elements.courseFilter.addEventListener('change', (e) => {
      state.course = e.target.value;
      state.skip = 0;
      fetchStudents();
    });

    // Per-page Limit Select
    elements.limitSelect.addEventListener('change', (e) => {
      state.limit = parseInt(e.target.value, 10) || 10;
      state.skip = 0;
      fetchStudents();
    });

    // Refresh & Retry
    elements.btnRefresh.addEventListener('click', () => {
      fetchStudents();
      fetchStats();
      fetchCourses();
      showToast('Records refreshed.', 'info');
    });
    elements.btnRetryFetch.addEventListener('click', () => {
      fetchStudents();
      fetchStats();
      fetchCourses();
    });

    // Pagination
    elements.btnPrevPage.addEventListener('click', () => {
      if (state.skip > 0) {
        state.skip = Math.max(0, state.skip - state.limit);
        fetchStudents();
      }
    });

    elements.btnNextPage.addEventListener('click', () => {
      if (state.skip + state.limit < state.total) {
        state.skip += state.limit;
        fetchStudents();
      }
    });

    // Add Student Button
    elements.btnAddStudent.addEventListener('click', openAddModal);
    elements.btnEmptyAdd.addEventListener('click', openAddModal);

    // Form Submit
    elements.studentForm.addEventListener('submit', handleStudentFormSubmit);

    // Table Actions Delegation (View, Edit, Delete)
    elements.tableBody.addEventListener('click', (e) => {
      const button = e.target.closest('button[data-action]');
      if (!button) return;

      const action = button.getAttribute('data-action');
      const studentId = parseInt(button.getAttribute('data-id'), 10);
      const student = state.students.find((s) => s.id === studentId);

      if (action === 'view') {
        openProfileModal(studentId);
      } else if (action === 'edit' && student) {
        openEditModal(student);
      } else if (action === 'delete' && student) {
        openDeleteModal(student);
      }
    });

    // Profile Modal Edit Shortcut
    elements.profileBtnEdit.addEventListener('click', () => {
      elements.profileModal.classList.add('hidden');
      if (state.selectedStudent) openEditModal(state.selectedStudent);
    });

    // Delete Modal Confirm
    elements.btnConfirmDelete.addEventListener('click', confirmDelete);

    // Modal Close via backdrop or buttons with data-close-modal
    document.addEventListener('click', (e) => {
      const closeTarget = e.target.getAttribute('data-close-modal');
      if (closeTarget) {
        const modal = document.getElementById(closeTarget);
        if (modal) modal.classList.add('hidden');
      }
      if (e.target.classList.contains('modal-overlay')) {
        e.target.classList.add('hidden');
      }
    });

    // AI Drawer Toggle
    elements.btnOpenAi.addEventListener('click', () => {
      elements.aiDrawer.classList.remove('hidden');
      checkAIStatus();
      elements.aiQuestionInput.focus();
    });

    elements.btnCloseAi.addEventListener('click', () => {
      elements.aiDrawer.classList.add('hidden');
    });

    // AI Quick chips
    document.querySelectorAll('.chip-btn').forEach((chip) => {
      chip.addEventListener('click', () => {
        elements.aiQuestionInput.value = chip.getAttribute('data-question');
        handleAIQuestion();
      });
    });

    elements.aiAskForm.addEventListener('submit', handleAIQuestion);

    // Keyboard accessibility: Escape to close modals
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        elements.studentModal.classList.add('hidden');
        elements.profileModal.classList.add('hidden');
        elements.deleteModal.classList.add('hidden');
        elements.aiDrawer.classList.add('hidden');
      }
    });
  }

  // Application Entry Initialization
  async function init() {
    setupEventListeners();
    await Promise.all([fetchStudents(), fetchStats(), fetchCourses(), checkAIStatus()]);
  }

  // Bootstrapping
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

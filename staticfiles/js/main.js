/* ============================================
   main.js — location based garbage management system
   Advanced Features: AJAX, Real-time Updates,
   Notifications, Toast System
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {

    // ====================================================
    // 1. AUTO-DISMISS ALERTS after 5 seconds
    // ====================================================
    const alerts = document.querySelectorAll('.alert-custom');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 400);
        }, 5000);
    });

    // ====================================================
    // 2. ANIMATED COUNTERS (Intersection Observer)
    // ====================================================
    const counters = document.querySelectorAll('[data-counter]');
    if (counters.length) {
        const animateCounter = (el) => {
            const target = parseInt(el.dataset.counter);
            const duration = 1500;
            const startTime = performance.now();

            const tick = (now) => {
                const elapsed = now - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const eased = 1 - (1 - progress) * (1 - progress); // ease-out quad
                el.textContent = Math.floor(target * eased);
                if (progress < 1) requestAnimationFrame(tick);
                else el.textContent = target;
            };
            requestAnimationFrame(tick);
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });

        counters.forEach(c => observer.observe(c));
    }

    // ====================================================
    // 3. CONFIRM STATUS UPDATE (form-based fallback)
    // ====================================================
    const statusForms = document.querySelectorAll('.status-update-form');
    statusForms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const status = form.querySelector('[name="status"]')?.value;
            if (status === 'resolved') {
                if (!confirm('Mark this task as resolved? This action confirms the work is done.')) {
                    e.preventDefault();
                }
            }
        });
    });

    // ====================================================
    // 4. FADE-IN ON SCROLL (Intersection Observer)
    // ====================================================
    const fadeEls = document.querySelectorAll('.fade-in-scroll');
    if (fadeEls.length) {
        const fadeObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                    fadeObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.15 });

        fadeEls.forEach(el => {
            el.style.opacity = '0';
            fadeObserver.observe(el);
        });
    }

    // ====================================================
    // 5. NAVBAR ACTIVE LINK HIGHLIGHT
    // ====================================================
    const currentPath = window.location.pathname;
    document.querySelectorAll('.navbar-custom .nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // ====================================================
    // 6. IMAGE PREVIEW on file input
    // ====================================================
    const imageInput = document.querySelector('input[type="file"][accept="image/*"]');
    if (imageInput) {
        imageInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;

            let preview = document.getElementById('image-preview');
            if (!preview) {
                preview = document.createElement('img');
                preview.id = 'image-preview';
                preview.style.cssText = 'max-width:100%; border-radius:12px; margin-top:1rem; border:1px solid rgba(255,255,255,0.08);';
                imageInput.parentElement.appendChild(preview);
            }

            const reader = new FileReader();
            reader.onload = (ev) => { preview.src = ev.target.result; };
            reader.readAsDataURL(file);
        });
    }

    // ====================================================
    // 7. TOAST NOTIFICATION SYSTEM
    // ====================================================
    window.showToast = function(message, type = 'success') {
        const container = document.getElementById('toast-container') || createToastContainer();
        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        
        const icon = type === 'success' ? 'bi-check-circle-fill' :
                     type === 'error' ? 'bi-exclamation-triangle-fill' :
                     'bi-info-circle-fill';

        toast.innerHTML = `
            <i class="bi ${icon} me-2"></i>
            <span>${message}</span>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="bi bi-x"></i>
            </button>
        `;
        container.appendChild(toast);

        // Auto-remove after 4 seconds
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 400);
        }, 4000);
    };

    function createToastContainer() {
        const c = document.createElement('div');
        c.id = 'toast-container';
        document.body.appendChild(c);
        return c;
    }

    // ====================================================
    // 8. AJAX: WORKER STATUS UPDATE (No Page Reload)
    // ====================================================
    const ajaxStatusForm = document.getElementById('ajax-status-form');
    if (ajaxStatusForm) {
        ajaxStatusForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const taskId = ajaxStatusForm.dataset.taskId;
            const statusSelect = ajaxStatusForm.querySelector('[name="status"]');
            const notesField = ajaxStatusForm.querySelector('[name="worker_notes"]');
            const submitBtn = ajaxStatusForm.querySelector('button[type="submit"]');
            const newStatus = statusSelect.value;

            // Confirm if resolving
            if (newStatus === 'resolved') {
                if (!confirm('Mark this task as resolved?')) return;
            }

            // Disable button during request
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="bi bi-arrow-repeat me-2 spin-icon"></i>Updating...';

            try {
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                const response = await fetch(`/worker/api/task/${taskId}/update/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                    body: JSON.stringify({
                        status: newStatus,
                        worker_notes: notesField?.value || '',
                    }),
                });

                const data = await response.json();

                if (data.success) {
                    // Update the status badge on the page
                    const statusBadge = document.getElementById('current-status-badge');
                    if (statusBadge) {
                        statusBadge.className = `badge bg-${data.status_color} badge-status`;
                        statusBadge.textContent = data.status_display;
                    }

                    // Update the current status display in the form
                    const statusDisplay = document.getElementById('current-status-display');
                    if (statusDisplay) {
                        statusDisplay.className = `badge bg-${data.status_color} badge-status`;
                        statusDisplay.textContent = data.status_display;
                    }

                    showToast(data.message, 'success');

                    // If resolved, disable the form
                    if (data.status === 'resolved') {
                        statusSelect.disabled = true;
                        if (notesField) notesField.disabled = true;
                        submitBtn.style.display = 'none';
                    }
                } else {
                    showToast(data.error || 'Update failed', 'error');
                }
            } catch (err) {
                showToast('Network error. Please try again.', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="bi bi-check-lg me-2"></i>Update Status';
            }
        });
    }

    // ====================================================
    // 9. AJAX: LIVE NOTIFICATION BADGE UPDATE (Poll every 30s)
    // ====================================================
    const notifBadge = document.getElementById('notif-badge');
    const notifDropdown = document.getElementById('notif-dropdown-body');

    if (notifBadge) {
        async function pollNotifications() {
            try {
                const res = await fetch('/accounts/api/notifications/');
                const data = await res.json();

                // Update badge count
                if (data.count > 0) {
                    notifBadge.textContent = data.count;
                    notifBadge.style.display = 'inline-block';
                } else {
                    notifBadge.style.display = 'none';
                }

                // Update dropdown content
                if (notifDropdown) {
                    if (data.notifications.length === 0) {
                        notifDropdown.innerHTML = '<li><span class="dropdown-item text-muted">No new notifications.</span></li>';
                    } else {
                        notifDropdown.innerHTML = data.notifications.map(n => `
                            <li>
                                <div class="dropdown-item text-light" style="white-space: normal; font-size: 0.9rem;">
                                    <small class="text-muted d-block">${n.time_ago}</small>
                                    ${n.message}
                                </div>
                            </li>
                        `).join('<li><hr class="dropdown-divider" style="border-color: rgba(255,255,255,0.08);"></li>');
                    }
                }
            } catch (e) { /* Silently fail on network issues */ }
        }

        // Poll every 30 seconds
        setInterval(pollNotifications, 30000);
    }

    // ====================================================
    // 10. AJAX: MARK ALL NOTIFICATIONS AS READ
    // ====================================================
    const markAllReadBtn = document.getElementById('mark-all-read-btn');
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            try {
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value
                    || getCookie('csrftoken');
                const res = await fetch('/accounts/api/notifications/mark-all-read/', {
                    method: 'POST',
                    headers: { 'X-CSRFToken': csrfToken },
                });
                const data = await res.json();
                if (data.success) {
                    if (notifBadge) notifBadge.style.display = 'none';
                    if (notifDropdown) {
                        notifDropdown.innerHTML = '<li><span class="dropdown-item text-muted">No new notifications.</span></li>';
                    }
                    showToast('All notifications marked as read.', 'success');
                }
            } catch (e) {
                showToast('Failed to mark notifications.', 'error');
            }
        });
    }

    // ====================================================
    // 11. AJAX: CITIZEN DASHBOARD AUTO-REFRESH (Poll every 15s)
    // ====================================================
    const dashboardStatsContainer = document.getElementById('citizen-dashboard-stats');
    if (dashboardStatsContainer) {
        async function refreshDashboard() {
            try {
                const res = await fetch('/citizen/api/dashboard-stats/');
                const data = await res.json();

                // Update stat cards
                const updateStat = (id, val) => {
                    const el = document.getElementById(id);
                    if (el) el.textContent = val;
                };
                updateStat('stat-total', data.total);
                updateStat('stat-pending', data.pending);
                updateStat('stat-in-progress', data.in_progress);
                updateStat('stat-resolved', data.resolved);

            } catch (e) { /* Silently fail */ }
        }

        // Poll every 15 seconds for live updates
        setInterval(refreshDashboard, 15000);
    }

    // ====================================================
    // 12. AJAX: REPORT TRACKING AUTO-REFRESH (Poll every 10s)
    // ====================================================
    const trackingContainer = document.getElementById('report-tracking');
    if (trackingContainer) {
        const reportId = trackingContainer.dataset.reportId;
        
        async function refreshTracking() {
            try {
                const res = await fetch(`/citizen/api/report/${reportId}/status/`);
                const data = await res.json();

                // Update status badge
                const statusEl = document.getElementById('track-status');
                if (statusEl) {
                    statusEl.className = `badge bg-${data.status_color} badge-status`;
                    statusEl.textContent = data.status_display;
                }

                // Update worker info
                const workerEl = document.getElementById('track-worker');
                if (workerEl && data.worker) {
                    workerEl.textContent = data.worker;
                }

                // Update notes
                const notesEl = document.getElementById('track-notes');
                if (notesEl && data.worker_notes) {
                    notesEl.textContent = data.worker_notes;
                    notesEl.closest('.track-notes-section')?.classList.remove('d-none');
                }

                // Update time
                const timeEl = document.getElementById('track-updated');
                if (timeEl) timeEl.textContent = data.updated_at;

            } catch (e) { /* Silently fail */ }
        }

        // Poll every 10 seconds for real-time status
        setInterval(refreshTracking, 10000);
    }

    // ====================================================
    // HELPER: Get CSRF cookie
    // ====================================================
    function getCookie(name) {
        const val = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
        return val ? val.pop() : '';
    }

});

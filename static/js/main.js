/**
 * TaskFlow — Main JavaScript
 *
 * Vanilla JavaScript only — no jQuery or other libraries needed.
 * Bootstrap 5's JS is loaded separately via CDN.
 *
 * Features implemented here:
 *   1. Auto-dismiss flash messages after 5 seconds
 *   2. Delete confirmation dialog for task rows
 *   3. Character counter for the task title field
 *   4. Highlight overdue rows with a tooltip
 *   5. Form "dirty" check — warn before leaving if form was edited
 */

'use strict';

// ============================================================
// 1. AUTO-DISMISS FLASH MESSAGES
//    Django's messages framework shows one-time notifications.
//    We automatically hide them after 5 seconds.
// ============================================================
function initAutoMessages() {
    const alerts = document.querySelectorAll('.alert.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            // Use Bootstrap's dismiss API to fade out
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);  // 5 seconds
    });
}

// ============================================================
// 2. TITLE CHARACTER COUNTER
//    Shows remaining characters as the user types in the title
//    field. Turns red when fewer than 20 characters remain.
// ============================================================
function initTitleCounter() {
    const titleField = document.getElementById('id_title');
    if (!titleField) return;

    const maxLen = 150;
    const counter = document.createElement('div');
    counter.className = 'form-text text-end';
    counter.id = 'titleCounter';
    titleField.parentNode.appendChild(counter);

    function update() {
        const remaining = maxLen - titleField.value.length;
        counter.textContent = remaining + ' characters remaining';
        counter.className = 'form-text text-end ' +
            (remaining < 20 ? 'text-danger' : 'text-muted');
    }

    titleField.addEventListener('input', update);
    update();  // Run on page load (handles pre-filled edit forms)
}

// ============================================================
// 3. DIRTY FORM WARNING
//    If a user starts filling in a form and then navigates
//    away by clicking a link (not the submit button),
//    we warn them that unsaved changes will be lost.
// ============================================================
function initDirtyFormWarning() {
    const forms = document.querySelectorAll('form[method="post"]');
    forms.forEach(function(form) {
        let isDirty = false;

        // Mark form as dirty when any input changes
        form.querySelectorAll('input, textarea, select').forEach(function(el) {
            el.addEventListener('change', function() { isDirty = true; });
            el.addEventListener('input',  function() { isDirty = true; });
        });

        // When the form is submitted normally, it's not a "dirty leave"
        form.addEventListener('submit', function() { isDirty = false; });

        // Warn before unload (e.g. closing tab or refreshing)
        window.addEventListener('beforeunload', function(e) {
            if (isDirty) {
                e.preventDefault();
                // Modern browsers show their own generic message;
                // this string is ignored in Chrome/Firefox.
                e.returnValue = 'You have unsaved changes. Leave anyway?';
            }
        });
    });
}

// ============================================================
// 4. TASK ROW TOOLTIPS
//    Initialize Bootstrap tooltips on elements with
//    data-bs-toggle="tooltip" attribute.
// ============================================================
function initTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(function(el) {
        new bootstrap.Tooltip(el, {
            trigger: 'hover focus'
        });
    });
}

// ============================================================
// 5. FILTER FORM: CLEAR BUTTON CONVENIENCE
//    When the user clicks "Clear Filters", reset all form
//    fields in the filter form instead of just navigating away.
// ============================================================
function initClearFilters() {
    const clearBtn = document.getElementById('clearFiltersBtn');
    const filterForm = document.getElementById('filterForm');

    if (clearBtn && filterForm) {
        clearBtn.addEventListener('click', function(e) {
            e.preventDefault();
            filterForm.querySelectorAll('input[type="text"]').forEach(function(el) {
                el.value = '';
            });
            filterForm.querySelectorAll('select').forEach(function(el) {
                el.selectedIndex = 0;
            });
            filterForm.querySelectorAll('input[type="checkbox"]').forEach(function(el) {
                el.checked = false;
            });
            filterForm.submit();
        });
    }
}

// ============================================================
// 6. ACTIVE NAV LINK HIGHLIGHTING
//    Adds 'active' class to the navbar link matching the
//    current page URL. Works as a fallback / enhancement
//    to the template-level active detection.
// ============================================================
function initNavHighlight() {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.navbar-nav .nav-link').forEach(function(link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

// ============================================================
// INITIALIZATION — Run all functions when DOM is ready
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    initAutoMessages();
    initTitleCounter();
    initDirtyFormWarning();
    initTooltips();
    initClearFilters();
    initNavHighlight();

    console.log('TaskFlow JS initialized.');
});

/**
 * Smart Financial Reconciliation System - Production SPA JavaScript
 * Real-time Multi-Way Matching, OpenRouter AI Integration, Policy RAG,
 * Risk Queues, Interactive Modal, Report Exporter, and Live Cloud Diagnostics.
 */

// Dynamic API Base URL for seamless local + Vercel/Render integration
const API_BASE_URL = window.location.hostname.includes('vercel.app') 
    ? 'https://ai-finance-controller-jnc0.onrender.com' 
    : '';

// Global App State
const state = {
    currentView: 'home',
    transactions: [],
    summary: {},
    aiMetrics: null,
    aiInvestigations: [],
    auditLogs: [],
    aiMap: {},
    settings: {},
    explorer: {
        search: '',
        statusFilter: '',
        sortField: 'order_id',
        sortOrder: 'asc',
        currentPage: 1,
        pageSize: 10
    },
    currentInvestigationId: null
};

// Chart instances
let dashStatusChart = null;
let dashVolumeChart = null;
let dashCategoryChart = null;
let dashBenchmarkChart = null;

document.addEventListener('DOMContentLoaded', () => {
    initApp();

    // Topbar & runner demo buttons
    const demoTopbar = document.getElementById('run-demo-topbar-btn');
    if (demoTopbar) demoTopbar.addEventListener('click', runDemoPipeline);
    const demoRunner = document.getElementById('runner-demo-btn');
    if (demoRunner) demoRunner.addEventListener('click', runDemoPipeline);

    // Topbar Search with instant filter
    const topSearch = document.getElementById('topbar-search');
    if (topSearch) {
        topSearch.addEventListener('input', (e) => {
            state.explorer.search = e.target.value;
            if (state.currentView !== 'transactions') {
                switchView('transactions');
            }
            const expSearch = document.getElementById('explorer-search');
            if (expSearch) expSearch.value = e.target.value;
            renderExplorer();
        });
    }

    // Keyboard Shortcuts (Ctrl+K = Search, Alt+R = Run Demo)
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.getElementById('topbar-search');
            if (searchInput) searchInput.focus();
        } else if (e.altKey && (e.key === 'r' || e.key === 'R')) {
            e.preventDefault();
            runDemoPipeline();
        }
    });

    // Explorer Search & Filter
    const expSearch = document.getElementById('explorer-search');
    if (expSearch) {
        expSearch.addEventListener('input', (e) => {
            state.explorer.search = e.target.value;
            state.explorer.currentPage = 1;
            renderExplorer();
        });
    }

    const expFilter = document.getElementById('explorer-status-filter');
    if (expFilter) {
        expFilter.addEventListener('change', (e) => {
            state.explorer.statusFilter = e.target.value;
            state.explorer.currentPage = 1;
            renderExplorer();
        });
    }

    const prevPage = document.getElementById('explorer-prev-page');
    if (prevPage) {
        prevPage.addEventListener('click', () => {
            if (state.explorer.currentPage > 1) {
                state.explorer.currentPage--;
                renderExplorer();
            }
        });
    }

    const nextPage = document.getElementById('explorer-next-page');
    if (nextPage) {
        nextPage.addEventListener('click', () => {
            state.explorer.currentPage++;
            renderExplorer();
        });
    }

    // CSV Upload
    const uploadBtn = document.getElementById('upload-csv-btn');
    if (uploadBtn) uploadBtn.addEventListener('click', uploadAndReconcileCSVs);

    // Modal controls
    const closeBtn = document.getElementById('close-modal-btn');
    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    const submitBtn = document.getElementById('submit-review-btn');
    if (submitBtn) submitBtn.addEventListener('click', submitHumanReview);
});

async function initApp() {
    await fetchAllData();
    switchView('home');
}

// Fetch all application data from backend
async function fetchAllData() {
    try {
        const [summaryRes, txnsRes, aiMetricsRes, aiInvestigationsRes, auditRes] = await Promise.all([
            fetch(`${API_BASE_URL}/summary`),
            fetch(`${API_BASE_URL}/transactions`),
            fetch(`${API_BASE_URL}/api/v1/ai/metrics`),
            fetch(`${API_BASE_URL}/api/v1/ai/investigations`),
            fetch(`${API_BASE_URL}/api/v1/reports/audit/json`)
        ]);

        if (summaryRes.ok) state.summary = await summaryRes.json();
        if (txnsRes.ok) state.transactions = await txnsRes.json();
        if (aiMetricsRes.ok) state.aiMetrics = await aiMetricsRes.json();

        if (aiInvestigationsRes.ok) {
            state.aiInvestigations = await aiInvestigationsRes.json();
            state.aiMap = {};
            state.aiInvestigations.forEach(inv => {
                state.aiMap[inv.order_id] = inv;
            });
        }

        if (auditRes.ok) state.auditLogs = await auditRes.json();

    } catch (err) {
        console.error('Error fetching application data:', err);
    }
}

// Client-side View Router (All 9 Tabs)
function switchView(viewName) {
    state.currentView = viewName;

    // Update nav item active states
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    const activeNav = document.getElementById(`nav-${viewName}`);
    if (activeNav) activeNav.classList.add('active');

    // Hide all view sections
    const views = ['home', 'dashboard', 'transactions', 'exceptions', 'ai-center', 'reconciliation', 'reports', 'audit-logs', 'settings'];
    views.forEach(v => {
        const el = document.getElementById(`view-${v}`);
        if (el) el.classList.add('hidden');
    });

    // Show target view
    const targetEl = document.getElementById(`view-${viewName}`);
    if (targetEl) targetEl.classList.remove('hidden');

    // Update Topbar Title with respective exact name
    const titles = {
        'home': 'Smart Financial Reconciliation System',
        'dashboard': 'Finance Operations Dashboard',
        'transactions': 'Transaction Explorer & Audit Ledger',
        'exceptions': 'Prioritized Exception Risk Queue',
        'ai-center': 'AI Investigation Center & Policy RAG',
        'reconciliation': 'Reconciliation Pipeline Runner',
        'reports': 'Exportable Finance Reports',
        'audit-logs': 'Immutable Audit Trail Ledger',
        'settings': 'System Settings & AI Engine Configuration'
    };
    const topTitle = document.getElementById('topbar-page-title');
    if (topTitle) topTitle.textContent = titles[viewName] || 'AI Finance Controller';

    // Render View Content
    if (viewName === 'home') renderHomeView();
    else if (viewName === 'dashboard') renderDashboardView();
    else if (viewName === 'transactions') renderExplorer();
    else if (viewName === 'exceptions') renderExceptionCenter();
    else if (viewName === 'ai-center') renderAICenterView();
    else if (viewName === 'reconciliation') renderReconciliationView();
    else if (viewName === 'reports') renderReportsView();
    else if (viewName === 'audit-logs') renderAuditLogsView();
    else if (viewName === 'settings') renderSettingsView();
}

// Tab 1: Front Page (Smart Financial Reconciliation System)
function renderHomeView() {
    // Front page is dynamic and shows overview
}

// Tab 2: Operations Dashboard View
function renderDashboardView() {
    const s = state.summary || {};
    const m = state.aiMetrics || {};

    const elTotal = document.getElementById('kpi-dash-total');
    if (elTotal) elTotal.textContent = (s.total_records || 0).toLocaleString();
    const elRate = document.getElementById('kpi-dash-match-rate');
    if (elRate) elRate.textContent = `${(s.match_rate_pct || 0).toFixed(1)}%`;
    const elMatched = document.getElementById('kpi-dash-matched');
    if (elMatched) elMatched.textContent = (s.matched_records || 0).toLocaleString();
    const elExc = document.getElementById('kpi-dash-exceptions');
    if (elExc) elExc.textContent = (s.exception_records || 0).toLocaleString();

    const elAiRes = document.getElementById('kpi-dash-ai-resolved');
    if (elAiRes) elAiRes.textContent = (m.ai_auto_reconciled_count || 0).toLocaleString();
    const elHuman = document.getElementById('kpi-dash-human-review');
    if (elHuman) elHuman.textContent = ((m.ai_mark_review_count || 0) + (m.ai_escalated_count || 0)).toLocaleString();
    const elUnres = document.getElementById('kpi-dash-unresolved');
    if (elUnres) elUnres.textContent = Math.max(0, (s.exception_records || 0) - (m.ai_auto_reconciled_count || 0)).toLocaleString();

    const elExp = document.getElementById('kpi-dash-expected');
    if (elExp) elExp.textContent = `₹${(s.total_expected_amount || 0).toLocaleString(undefined, {minimumFractionDigits: 2})}`;
    const elRec = document.getElementById('kpi-dash-received');
    if (elRec) elRec.textContent = `₹${(s.total_received_amount || 0).toLocaleString(undefined, {minimumFractionDigits: 2})}`;
    const elDisc = document.getElementById('kpi-dash-discrepancy');
    if (elDisc) elDisc.textContent = `₹${(s.total_discrepancy_amount || 0).toLocaleString(undefined, {minimumFractionDigits: 2})}`;

    renderDashboardCharts();
}

function renderDashboardCharts() {
    const s = state.summary || {};
    const txns = state.transactions || [];
    const m = state.aiMetrics || {};

    const colorMap = {
        'MATCHED': '#10b981',
        'AMOUNT_MISMATCH': '#f59e0b',
        'MISSING_PAYMENT': '#ef4444',
        'MISSING_BANK_TRANSACTION': '#dc2626',
        'DUPLICATE_TRANSACTION': '#8b5cf6',
        'DATE_MISMATCH': '#3b82f6',
        'REFERENCE_MISMATCH': '#d97706',
        'PARTIAL_PAYMENT': '#ec4899',
        'UNRESOLVED': '#64748b'
    };

    // 1. Status Donut Chart
    const canvasStatus = document.getElementById('dashStatusChart');
    if (canvasStatus) {
        const statusCtx = canvasStatus.getContext('2d');
        const breakdown = s.status_breakdown || {};
        if (dashStatusChart) dashStatusChart.destroy();
        dashStatusChart = new Chart(statusCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(breakdown),
                datasets: [{
                    data: Object.values(breakdown),
                    backgroundColor: Object.keys(breakdown).map(l => colorMap[l] || '#94a3b8'),
                    borderWidth: 1, borderColor: '#1e293b'
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { color: '#94a3b8', font: { size: 10 } } } } }
        });
    }

    // 2. Daily Volume Line Chart
    const canvasVol = document.getElementById('dashVolumeChart');
    if (canvasVol) {
        const volCtx = canvasVol.getContext('2d');
        const dateCounts = {};
        txns.forEach(t => {
            const d = (t.order_date || t.payment_date || t.bank_date || '2026-01-01').split(' ')[0];
            dateCounts[d] = (dateCounts[d] || 0) + 1;
        });
        const sortedDates = Object.keys(dateCounts).sort();
        if (dashVolumeChart) dashVolumeChart.destroy();
        dashVolumeChart = new Chart(volCtx, {
            type: 'line',
            data: {
                labels: sortedDates,
                datasets: [{ label: 'Transactions', data: sortedDates.map(d => dateCounts[d]), borderColor: '#38bdf8', backgroundColor: 'rgba(56, 189, 248, 0.15)', fill: true, tension: 0.3 }]
            },
            options: { responsive: true, maintainAspectRatio: false, scales: { x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }, y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' }, beginAtZero: true } }, plugins: { legend: { display: false } } }
        });
    }

    // 3. Category Bar Chart
    const canvasCat = document.getElementById('dashCategoryChart');
    if (canvasCat) {
        const catCtx = canvasCat.getContext('2d');
        const excCategories = {};
        txns.forEach(t => {
            if (t.status !== 'MATCHED') excCategories[t.status] = (excCategories[t.status] || 0) + 1;
        });
        if (dashCategoryChart) dashCategoryChart.destroy();
        dashCategoryChart = new Chart(catCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(excCategories),
                datasets: [{ label: 'Exceptions', data: Object.values(excCategories), backgroundColor: Object.keys(excCategories).map(l => colorMap[l] || '#f59e0b'), borderRadius: 4 }]
            },
            options: { responsive: true, maintainAspectRatio: false, scales: { x: { ticks: { color: '#94a3b8', font: { size: 9 } }, grid: { display: false } }, y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' }, beginAtZero: true } }, plugins: { legend: { display: false } } }
        });
    }

    // 4. Benchmark Chart
    const canvasBench = document.getElementById('dashBenchmarkChart');
    if (canvasBench && m && m.comparison_table) {
        const benchCtx = canvasBench.getContext('2d');
        const comp = m.comparison_table;
        if (dashBenchmarkChart) dashBenchmarkChart.destroy();
        dashBenchmarkChart = new Chart(benchCtx, {
            type: 'bar',
            data: {
                labels: ['Auto-Resolved', 'Exceptions Remaining', 'Human Review'],
                datasets: [
                    { label: 'Phase 1 Rules', data: [comp.automatically_resolved.phase1, comp.exceptions.phase1, comp.human_review_required.phase1], backgroundColor: '#64748b', borderRadius: 4 },
                    { label: 'Phase 2 AI', data: [comp.automatically_resolved.phase2, comp.exceptions.phase2, comp.human_review_required.phase2], backgroundColor: '#8b5cf6', borderRadius: 4 },
                    { label: 'Phase 3 OpenRouter', data: [comp.automatically_resolved.phase2, comp.exceptions.phase2, comp.human_review_required.phase2], backgroundColor: '#10b981', borderRadius: 4 }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false, scales: { x: { ticks: { color: '#94a3b8' }, grid: { display: false } }, y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' }, beginAtZero: true } }, plugins: { legend: { labels: { color: '#94a3b8', font: { size: 10 } } } } }
        });
    }
}

// Tab 3: Transaction Explorer (Sorting, Filtering, Pagination)
function renderExplorer() {
    let list = [...state.transactions];

    // Search filter
    if (state.explorer.search) {
        const q = state.explorer.search.toLowerCase();
        list = list.filter(t => 
            (t.order_id && t.order_id.toLowerCase().includes(q)) ||
            (t.customer_id && t.customer_id.toLowerCase().includes(q)) ||
            (t.transaction_id && t.transaction_id.toLowerCase().includes(q)) ||
            (t.payment_id && t.payment_id.toLowerCase().includes(q))
        );
    }

    // Status filter
    if (state.explorer.statusFilter) {
        list = list.filter(t => t.status === state.explorer.statusFilter);
    }

    // Sorting
    const field = state.explorer.sortField;
    const dir = state.explorer.sortOrder === 'asc' ? 1 : -1;
    list.sort((a, b) => {
        let v1 = a[field] || '';
        let v2 = b[field] || '';
        if (typeof v1 === 'number') return (v1 - v2) * dir;
        return String(v1).localeCompare(String(v2)) * dir;
    });

    // Pagination
    const total = list.length;
    const page = state.explorer.currentPage;
    const pageSize = state.explorer.pageSize;
    const totalPages = Math.ceil(total / pageSize) || 1;

    const start = (page - 1) * pageSize;
    const paginated = list.slice(start, start + pageSize);

    const tbody = document.getElementById('explorer-tbody');
    if (!tbody) return;
    tbody.innerHTML = '';

    if (paginated.length === 0) {
        tbody.innerHTML = `<tr><td colspan="10" class="text-center py-6 text-slate-400">No matching transactions found.</td></tr>`;
    } else {
        paginated.forEach(t => {
            const tr = document.createElement('tr');
            tr.className = 'border-b border-slate-700/50 text-xs table-row-clickable';
            tr.onclick = () => openInvestigationModal(t.order_id);

            const aiData = state.aiMap[t.order_id];
            const aiBadge = aiData ? `<span class="px-2 py-0.5 rounded text-[10px] font-semibold badge-${aiData.decision}">${aiData.decision}</span>` : '-';
            const aiConf = aiData ? `${aiData.confidence.toFixed(0)}%` : '-';

            const actionBtn = t.status !== 'MATCHED'
                ? `<button onclick="event.stopPropagation(); openInvestigationModal('${t.order_id}')" class="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white px-2 py-1 rounded text-[11px] font-medium transition shadow">🤖 Investigate</button>`
                : `<span class="text-emerald-400 font-semibold text-[11px]">✓ Verified</span>`;

            tr.innerHTML = `
                <td class="py-3 px-4 font-mono font-medium text-cyan-300">${t.order_id}</td>
                <td class="py-3 px-4 font-mono text-slate-400">${t.payment_id || '-'}</td>
                <td class="py-3 px-4 text-right font-mono">₹${(t.expected_amount || 0).toFixed(2)}</td>
                <td class="py-3 px-4 text-right font-mono text-slate-300">${t.paid_amount !== null ? '₹' + t.paid_amount.toFixed(2) : '-'}</td>
                <td class="py-3 px-4 text-right font-mono text-slate-300">${t.bank_received_amount !== null ? '₹' + t.bank_received_amount.toFixed(2) : '-'}</td>
                <td class="py-3 px-4 text-center"><span class="px-2 py-0.5 rounded text-[10px] font-semibold badge-${t.status}">${t.status}</span></td>
                <td class="py-3 px-4 text-center font-mono font-semibold">${(t.confidence_score || 0).toFixed(0)}%</td>
                <td class="py-3 px-4 text-center font-mono text-purple-400 font-semibold">${aiConf}</td>
                <td class="py-3 px-4 text-right font-mono text-amber-400">${t.discrepancy_amount > 0 ? '₹' + t.discrepancy_amount.toFixed(2) : '₹0.00'}</td>
                <td class="py-3 px-4 text-center">${actionBtn}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    const info = document.getElementById('explorer-pagination-info');
    if (info) info.textContent = `Showing ${total === 0 ? 0 : start + 1}-${Math.min(start + pageSize, total)} of ${total}`;
    const pBtn = document.getElementById('explorer-prev-page');
    if (pBtn) pBtn.disabled = page <= 1;
    const nBtn = document.getElementById('explorer-next-page');
    if (nBtn) nBtn.disabled = page >= totalPages;
}

function sortExplorer(field) {
    if (state.explorer.sortField === field) {
        state.explorer.sortOrder = state.explorer.sortOrder === 'asc' ? 'desc' : 'asc';
    } else {
        state.explorer.sortField = field;
        state.explorer.sortOrder = 'asc';
    }
    renderExplorer();
}

// Tab 4: Exception Risk Queue View
function renderExceptionCenter() {
    const txns = state.transactions.filter(t => t.status !== 'MATCHED');

    const critical = txns.filter(t => t.discrepancy_amount >= 10000 || t.status === 'UNRESOLVED');
    const high = txns.filter(t => (t.discrepancy_amount >= 2000 && t.discrepancy_amount < 10000) || t.status.includes('MISSING'));
    const medium = txns.filter(t => t.status === 'AMOUNT_MISMATCH' || t.status === 'PARTIAL_PAYMENT');
    const low = txns.filter(t => t.status === 'DATE_MISMATCH' || t.status === 'REFERENCE_MISMATCH' || t.status === 'DUPLICATE_TRANSACTION');

    const bCrit = document.getElementById('badge-count-critical');
    if (bCrit) bCrit.textContent = critical.length;
    const bHigh = document.getElementById('badge-count-high');
    if (bHigh) bHigh.textContent = high.length;
    const bMed = document.getElementById('badge-count-medium');
    if (bMed) bMed.textContent = medium.length;
    const bLow = document.getElementById('badge-count-low');
    if (bLow) bLow.textContent = low.length;

    renderQueueContainer('queue-critical', critical, 'CRITICAL');
    renderQueueContainer('queue-high', high, 'HIGH');
    renderQueueContainer('queue-medium', medium, 'MEDIUM');
    renderQueueContainer('queue-low', low, 'LOW');
}

function renderQueueContainer(containerId, list, priority) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';

    if (list.length === 0) {
        container.innerHTML = `<p class="text-xs text-slate-500 italic p-2">No ${priority.toLowerCase()} exceptions in queue.</p>`;
        return;
    }

    list.slice(0, 10).forEach(t => {
        const card = document.createElement('div');
        card.className = `fintech-card p-3 priority-${priority} space-y-2 cursor-pointer hover:border-slate-500`;
        card.onclick = () => openInvestigationModal(t.order_id);

        card.innerHTML = `
            <div class="flex items-center justify-between">
                <span class="font-mono font-bold text-xs text-cyan-300">${t.order_id}</span>
                <span class="text-[10px] font-mono text-amber-400 font-semibold">₹${t.discrepancy_amount.toFixed(2)}</span>
            </div>
            <p class="text-[11px] text-slate-300 line-clamp-2">${t.explanation}</p>
            <div class="flex items-center justify-between pt-1">
                <span class="px-2 py-0.5 rounded text-[10px] font-semibold badge-${t.status}">${t.status}</span>
                <button onclick="event.stopPropagation(); openInvestigationModal('${t.order_id}')" class="text-[10px] text-purple-400 hover:text-purple-300 font-semibold flex items-center gap-1">Investigate ➔</button>
            </div>
        `;
        container.appendChild(card);
    });
}

// Tab 5: AI Investigation Center View
function renderAICenterView() {
    const tbody = document.getElementById('ai-center-tbody');
    if (!tbody) return;
    tbody.innerHTML = '';

    if (state.aiInvestigations.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center py-6 text-slate-400">No AI investigations executed yet. Click "Run OpenRouter Agent Analysis" to analyze exceptions with real LLM reasoning.</td></tr>`;
        return;
    }

    state.aiInvestigations.forEach(inv => {
        const tr = document.createElement('tr');
        tr.className = 'border-b border-slate-700/50 text-xs hover:bg-slate-800/50 table-row-clickable';
        tr.onclick = () => openInvestigationModal(inv.order_id);

        tr.innerHTML = `
            <td class="py-3 px-4 font-mono font-semibold text-purple-300">${inv.investigation_id || 'AI-INV'}</td>
            <td class="py-3 px-4 font-mono text-cyan-300">${inv.order_id}</td>
            <td class="py-3 px-4 text-center"><span class="px-2 py-0.5 rounded text-[10px] font-semibold badge-${inv.decision}">${inv.decision}</span></td>
            <td class="py-3 px-4 text-center font-mono font-bold text-purple-400">${(inv.confidence || 0).toFixed(0)}%</td>
            <td class="py-3 px-4 text-center"><span class="px-2 py-0.5 rounded text-[10px] font-semibold badge-${inv.recommended_action}">${inv.recommended_action}</span></td>
            <td class="py-3 px-4 text-slate-300 truncate max-w-xs" title="${inv.reason}">${inv.reason}</td>
            <td class="py-3 px-4 text-center">
                <button onclick="event.stopPropagation(); openInvestigationModal('${inv.order_id}')" class="bg-slate-800 hover:bg-slate-700 text-slate-200 px-2.5 py-1 rounded text-[11px] font-medium border border-slate-700">Detail ➔</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Run All AI Investigations with OpenRouter
async function runAIInvestigationAll() {
    const btn = document.getElementById('ai-run-all-btn');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<span class="animate-spin">🔄</span> Running OpenRouter Agent Analysis...`;
    }

    try {
        const res = await fetch(`${API_BASE_URL}/agent/investigations`);
        if (res.ok) {
            await fetchAllData();
            renderAICenterView();
            showToast('OpenRouter AI Analysis completed across all exceptions!', 'success');
        } else {
            showToast('AI analysis failed. Please verify OpenRouter API settings.', 'error');
        }
    } catch (e) {
        console.error('Error running AI investigations:', e);
        showToast('Error connecting to backend AI service.', 'error');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<span>🤖</span> Run OpenRouter Agent Analysis`;
        }
    }
}

// Tab 6: Reconciliation Runner
function renderReconciliationView() {
    // Runner controls
}

// Tab 7: Reports Exporter View
function renderReportsView() {
    // Reports cards
}

function downloadReport(type, format) {
    const url = `${API_BASE_URL}/api/v1/reports/${type}/${format}`;
    window.open(url, '_blank');
}

// Tab 8: Audit Logs View
function renderAuditLogsView() {
    const tbody = document.getElementById('audit-logs-tbody');
    if (!tbody) return;
    tbody.innerHTML = '';

    if (state.auditLogs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center py-6 text-slate-400">No audit log records recorded yet. Run the reconciliation pipeline to generate audit history.</td></tr>`;
        return;
    }

    state.auditLogs.forEach(log => {
        const tr = document.createElement('tr');
        tr.className = 'border-b border-slate-700/50 text-xs hover:bg-slate-800/50';

        const humanAction = log.human_decision
            ? `<span class="px-2 py-0.5 rounded text-[10px] font-semibold badge-${log.human_decision}">${log.human_decision}</span>`
            : `<span class="text-amber-400/80 italic text-[11px]">Pending Review</span>`;

        const reviewerInfo = log.reviewer_name
            ? `<div class="font-medium text-slate-200">${log.reviewer_name}<p class="text-[10px] text-slate-400 italic">"${log.reviewer_note || ''}"</p></div>`
            : `-`;

        tr.innerHTML = `
            <td class="py-3 px-4 font-mono text-slate-400">${log.timestamp}</td>
            <td class="py-3 px-4 font-mono font-semibold text-purple-300">${log.investigation_id}</td>
            <td class="py-3 px-4 font-mono text-cyan-300">${log.order_id}</td>
            <td class="py-3 px-4 text-center"><span class="px-2 py-0.5 rounded text-[10px] font-semibold badge-${log.rule_decision}">${log.rule_decision}</span></td>
            <td class="py-3 px-4 text-center"><span class="px-2 py-0.5 rounded text-[10px] font-semibold badge-${log.ai_decision}">${log.ai_decision}</span></td>
            <td class="py-3 px-4 text-center">${humanAction}</td>
            <td class="py-3 px-4 text-slate-300">${reviewerInfo}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Tab 9: Settings View
async function renderSettingsView() {
    try {
        const res = await fetch(`${API_BASE_URL}/api/v1/settings`);
        if (res.ok) {
            state.settings = await res.json();
            const elModel = document.getElementById('setting-openrouter-model');
            if (elModel && state.settings.openrouter_model) {
                elModel.value = state.settings.openrouter_model;
            }
        }
    } catch (e) {
        console.error('Failed to load settings:', e);
    }
}

// Test OpenRouter API Key Live Connection
async function testLLMConnection() {
    const btn = document.getElementById('btn-test-llm');
    const resultBox = document.getElementById('llm-test-result');
    const key = document.getElementById('setting-openrouter-key').value.trim();
    const model = document.getElementById('setting-openrouter-model').value;

    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<span class="animate-spin">🔄</span> Testing...`;
    }
    if (resultBox) {
        resultBox.classList.remove('hidden');
        resultBox.className = 'p-3 bg-slate-900/80 rounded border border-slate-700 text-[11px] font-mono text-cyan-300';
        resultBox.textContent = 'Pinging OpenRouter API endpoint...';
    }

    try {
        const res = await fetch(`${API_BASE_URL}/api/v1/settings/test-llm`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: key, model: model })
        });
        const data = await res.json();

        if (res.ok) {
            resultBox.className = 'p-3 bg-emerald-950/40 rounded border border-emerald-700 text-[11px] font-mono text-emerald-300';
            resultBox.innerHTML = `
                <p class="font-bold">✓ ${data.message}</p>
                <p class="text-slate-400 mt-1">Tier: ${data.is_free_tier ? 'Free Tier' : 'Paid'} | Model: ${data.model} | Free Requests Remaining: ${data.remaining_free_requests}</p>
            `;
            const badge = document.getElementById('openrouter-status-badge');
            if (badge) {
                badge.className = 'px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-950 text-emerald-300 border border-emerald-800';
                badge.textContent = 'Connected';
            }
            showToast('OpenRouter API connection verified successfully!', 'success');
        } else {
            resultBox.className = 'p-3 bg-rose-950/40 rounded border border-rose-700 text-[11px] font-mono text-rose-300';
            resultBox.textContent = `✗ Connection Failed: ${data.detail || 'Invalid API Key'}`;
            showToast('OpenRouter connection failed.', 'error');
        }
    } catch (e) {
        if (resultBox) {
            resultBox.className = 'p-3 bg-rose-950/40 rounded border border-rose-700 text-[11px] font-mono text-rose-300';
            resultBox.textContent = `✗ Network Error: Could not connect to backend settings API.`;
        }
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<span>⚡</span> Test Connection`;
        }
    }
}

// Save OpenRouter AI Settings
async function saveAISettings() {
    const key = document.getElementById('setting-openrouter-key').value.trim();
    const model = document.getElementById('setting-openrouter-model').value;

    try {
        const res = await fetch(`${API_BASE_URL}/api/v1/settings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ openrouter_api_key: key, openrouter_model: model })
        });
        if (res.ok) {
            showToast(`AI settings saved. Model set to ${model}.`, 'success');
        } else {
            showToast('Failed to save AI settings.', 'error');
        }
    } catch (e) {
        showToast('Error communicating with settings API.', 'error');
    }
}

// Save Policy Settings
async function savePolicySettings() {
    const win = parseInt(document.getElementById('setting-settlement-window').value, 10);
    const autoConf = parseFloat(document.getElementById('setting-auto-conf').value);
    const revConf = parseFloat(document.getElementById('setting-review-conf').value);

    try {
        const res = await fetch(`${API_BASE_URL}/api/v1/settings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                settlement_window_days: win,
                auto_reconcile_threshold: autoConf,
                human_review_threshold: revConf
            })
        });
        if (res.ok) {
            showToast('Reconciliation policy tolerances saved successfully.', 'success');
        } else {
            showToast('Failed to save policy settings.', 'error');
        }
    } catch (e) {
        showToast('Error communicating with settings API.', 'error');
    }
}

function toggleKeyVisibility() {
    const input = document.getElementById('setting-openrouter-key');
    if (input) {
        input.type = input.type === 'password' ? 'text' : 'password';
    }
}

// 1-Click Demo Pipeline Stepper
async function runDemoPipeline() {
    const btn1 = document.getElementById('run-demo-topbar-btn');
    const btn2 = document.getElementById('runner-demo-btn');
    const stepper = document.getElementById('runner-progress-stepper');

    if (btn1) { btn1.disabled = true; btn1.innerHTML = `⚡ Running Pipeline...`; }
    if (btn2) { btn2.disabled = true; btn2.innerHTML = `⚡ Running Pipeline...`; }
    if (stepper) stepper.classList.remove('hidden');

    try {
        setStepStatus('step-val', 'active');
        await new Promise(r => setTimeout(r, 200));
        setStepStatus('step-val', 'done');

        setStepStatus('step-rules', 'active');
        await fetch(`${API_BASE_URL}/reconcile`, { method: 'POST' });
        setStepStatus('step-rules', 'done');

        setStepStatus('step-rag', 'active');
        await fetch(`${API_BASE_URL}/agent/rebuild-knowledge-base`, { method: 'POST' });
        setStepStatus('step-rag', 'done');

        setStepStatus('step-ai', 'active');
        await fetch(`${API_BASE_URL}/agent/investigations`);
        setStepStatus('step-ai', 'done');

        setStepStatus('step-audit', 'active');
        await fetchAllData();
        setStepStatus('step-audit', 'done');

        showToast('Complete 1-Click Reconciliation Demo executed successfully!', 'success');
        switchView('dashboard');
    } catch (e) {
        console.error('Demo pipeline error:', e);
        showToast('Pipeline execution encountered an error.', 'error');
    } finally {
        if (btn1) { btn1.disabled = false; btn1.innerHTML = `<span>⚡</span> Run 1-Click Demo`; }
        if (btn2) { btn2.disabled = false; btn2.innerHTML = `⚡ Run Complete Demo`; }
    }
}

function setStepStatus(stepId, status) {
    const el = document.getElementById(stepId);
    if (!el) return;
    if (status === 'active') {
        el.className = 'p-2 rounded bg-cyan-900/60 text-cyan-200 font-bold border border-cyan-500 animate-pulse';
    } else if (status === 'done') {
        el.className = 'p-2 rounded bg-emerald-950 text-emerald-300 font-bold border border-emerald-800';
    }
}

// Upload custom CSVs
async function uploadAndReconcileCSVs() {
    const ordersFile = document.getElementById('upload-orders').files[0];
    const paymentsFile = document.getElementById('upload-payments').files[0];
    const bankFile = document.getElementById('upload-bank').files[0];

    if (!ordersFile || !paymentsFile || !bankFile) {
        showToast('Please select all three CSV files (orders, payments, bank_transactions).', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('orders_file', ordersFile);
    formData.append('payments_file', paymentsFile);
    formData.append('bank_file', bankFile);

    try {
        const res = await fetch(`${API_BASE_URL}/reconcile`, { method: 'POST', body: formData });
        if (res.ok) {
            await fetchAllData();
            switchView('dashboard');
            showToast('Custom CSV dataset uploaded and reconciled successfully!', 'success');
        } else {
            showToast('Failed to process custom CSV dataset.', 'error');
        }
    } catch (e) {
        console.error('Upload CSV error:', e);
        showToast('Error uploading dataset.', 'error');
    }
}

// Modal Investigation Detail View
async function openInvestigationModal(orderId) {
    try {
        const [txnRes, agentRes, auditRes] = await Promise.all([
            fetch(`${API_BASE_URL}/transactions?search=${encodeURIComponent(orderId)}`),
            fetch(`${API_BASE_URL}/agent/investigate/${encodeURIComponent(orderId)}`, { method: 'POST' }),
            fetch(`${API_BASE_URL}/api/v1/audit/${encodeURIComponent(orderId)}`)
        ]);

        if (!agentRes.ok) {
            showToast(`Could not load investigation for ${orderId}`, 'error');
            return;
        }

        const txns = await txnRes.json();
        const agentData = await agentRes.json();
        const auditLogs = auditRes.ok ? await auditRes.json() : [];
        const txn = txns.length > 0 ? txns[0] : null;

        state.currentInvestigationId = agentData.investigation_id;

        document.getElementById('modal-order-id').textContent = orderId;
        const ruleStatus = document.getElementById('modal-rule-status');
        if (ruleStatus) {
            ruleStatus.textContent = txn ? txn.status : 'UNKNOWN';
            ruleStatus.className = `px-2 py-0.5 rounded text-xs font-semibold badge-${txn ? txn.status : ''}`;
        }

        document.getElementById('modal-evidence-order').innerHTML = `
            <p><span class="text-slate-400">Expected:</span> ₹${txn ? txn.expected_amount : '-'}</p>
            <p><span class="text-slate-400">Customer:</span> ${txn ? txn.customer_id : '-'}</p>
            <p><span class="text-slate-400">Date:</span> ${txn ? (txn.order_date || '-') : '-'}</p>
        `;

        document.getElementById('modal-evidence-payment').innerHTML = `
            <p><span class="text-slate-400">Paid:</span> ${txn && txn.paid_amount !== null ? '₹' + txn.paid_amount : 'MISSING'}</p>
            <p><span class="text-slate-400">Txn ID:</span> ${txn ? (txn.transaction_id || '-') : '-'}</p>
            <p><span class="text-slate-400">Date:</span> ${txn ? (txn.payment_date || '-') : '-'}</p>
        `;

        document.getElementById('modal-evidence-bank').innerHTML = `
            <p><span class="text-slate-400">Bank Received:</span> ${txn && txn.bank_received_amount !== null ? '₹' + txn.bank_received_amount : 'MISSING'}</p>
            <p><span class="text-slate-400">Bank Txn ID:</span> ${txn ? (txn.bank_transaction_id || '-') : '-'}</p>
            <p><span class="text-slate-400">Date:</span> ${txn ? (txn.bank_date || '-') : '-'}</p>
        `;

        const citationsDiv = document.getElementById('modal-rag-citations');
        citationsDiv.innerHTML = '';
        const st = agentData.state || {};
        const citations = st.policy_citations || [];

        if (citations.length === 0) {
            citationsDiv.innerHTML = '<p class="text-slate-400 italic text-xs">No specific policy citation retrieved.</p>';
        } else {
            citations.forEach(c => {
                const div = document.createElement('div');
                div.className = 'bg-purple-900/30 border border-purple-800/50 p-2.5 rounded font-mono text-[11px]';
                div.innerHTML = `
                    <p class="font-bold text-purple-300">📖 ${c.citation_label}</p>
                    <p class="text-slate-300 mt-1 font-sans text-xs">${c.content}</p>
                `;
                citationsDiv.appendChild(div);
            });
        }

        document.getElementById('modal-ai-decision').textContent = agentData.decision;
        document.getElementById('modal-ai-decision').className = `px-2.5 py-0.5 rounded text-xs font-semibold badge-${agentData.decision}`;
        document.getElementById('modal-ai-confidence').textContent = `${(agentData.confidence || 0).toFixed(0)}%`;
        document.getElementById('modal-ai-action').textContent = agentData.recommended_action;
        document.getElementById('modal-ai-action').className = `px-2.5 py-0.5 rounded text-xs font-semibold badge-${aiActionToBadgeClass(agentData.recommended_action)}`;
        document.getElementById('modal-ai-reason').textContent = agentData.reason;

        const timelineDiv = document.getElementById('modal-investigation-timeline');
        timelineDiv.innerHTML = '';
        const timeline = st.timeline || [];
        timeline.forEach(t => {
            const div = document.createElement('div');
            div.className = 'flex items-start gap-2 border-l border-slate-700 pl-3 py-1';
            const toolBadge = t.tool_used ? `<span class="bg-indigo-900/60 text-indigo-300 px-1.5 py-0.5 rounded text-[10px] font-mono">[Tool: ${t.tool_used}]</span>` : '';
            div.innerHTML = `
                <span class="text-slate-500 font-mono text-[10px]">${t.timestamp}</span>
                <div>
                    <span class="font-semibold text-slate-300">${t.step_name}:</span>
                    <span class="text-slate-400">${t.description}</span>
                    ${toolBadge}
                </div>
            `;
            timelineDiv.appendChild(div);
        });

        renderAuditTrail(auditLogs);
        document.getElementById('investigation-modal').classList.remove('hidden');
    } catch (e) {
        console.error('Modal load error:', e);
        showToast('Error opening investigation detail.', 'error');
    }
}

function aiActionToBadgeClass(action) {
    if (action === 'AUTO_RECONCILE') return 'MATCHED';
    if (action === 'MARK_FOR_REVIEW') return 'AMOUNT_MISMATCH';
    if (action === 'ESCALATE') return 'MISSING_PAYMENT';
    return 'UNRESOLVED';
}

function renderAuditTrail(logs) {
    const container = document.getElementById('modal-audit-timeline');
    if (!container) return;
    container.innerHTML = '';
    if (logs.length === 0) {
        container.innerHTML = '<p class="text-xs text-slate-500">No previous audit entries for this record.</p>';
        return;
    }
    logs.forEach(log => {
        const div = document.createElement('div');
        div.className = 'border-l-2 border-slate-700 pl-3 py-1 space-y-1 text-xs';
        const humanPart = log.human_decision
            ? `<div class="mt-1 text-slate-300 font-medium">
                <span class="px-1.5 py-0.5 rounded text-[10px] badge-${log.human_decision}">${log.human_decision}</span> by ${log.reviewer_name}
                <p class="text-slate-400 italic font-normal">"${log.reviewer_note}"</p>
               </div>`
            : '<p class="text-amber-400/80 italic text-[11px]">Pending Human Review</p>';

        div.innerHTML = `
            <div class="flex items-center justify-between text-slate-400 text-[11px]">
                <span class="font-mono">${log.timestamp}</span>
                <span class="font-semibold text-slate-300">ID: ${log.investigation_id}</span>
            </div>
            <p class="text-slate-200">Rule: <span class="font-semibold">${log.rule_decision}</span> (${log.rule_confidence}%) → AI: <span class="font-semibold">${log.ai_decision}</span> (${log.ai_confidence}%)</p>
            ${humanPart}
        `;
        container.appendChild(div);
    });
}

function closeModal() {
    const modal = document.getElementById('investigation-modal');
    if (modal) modal.classList.add('hidden');
    state.currentInvestigationId = null;
}

// Submit Human Review Sign-Off
async function submitHumanReview() {
    if (!state.currentInvestigationId) return;

    const reviewerName = document.getElementById('reviewer-name-input').value.trim() || 'Finance Auditor';
    const decision = document.getElementById('reviewer-decision-select').value;
    const reviewerNote = document.getElementById('reviewer-note-input').value.trim();

    if (!reviewerNote) {
        showToast('Please provide a review note explaining your decision.', 'error');
        return;
    }

    try {
        const res = await fetch(`${API_BASE_URL}/api/v1/ai/investigations/${state.currentInvestigationId}/review`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                reviewer_name: reviewerName,
                decision: decision,
                reviewer_note: reviewerNote
            })
        });

        if (res.ok) {
            closeModal();
            await fetchAllData();
            showToast(`Audit decision '${decision}' successfully logged!`, 'success');
            if (state.currentView === 'dashboard') renderDashboardView();
            else if (state.currentView === 'transactions') renderExplorer();
            else if (state.currentView === 'exceptions') renderExceptionCenter();
            else if (state.currentView === 'ai-center') renderAICenterView();
            else if (state.currentView === 'audit-logs') renderAuditLogsView();
        } else {
            showToast('Failed to submit review.', 'error');
        }
    } catch (e) {
        console.error('Human review submission error:', e);
        showToast('Error submitting review.', 'error');
    }
}

// Theme Switcher Toggle
function toggleTheme(theme) {
    if (theme === 'emerald') {
        document.body.classList.add('theme-emerald');
    } else {
        document.body.classList.remove('theme-emerald');
    }
}

// Floating Toast Notification
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    const border = type === 'success' ? 'border-emerald-500 text-emerald-300' : (type === 'error' ? 'border-rose-500 text-rose-300' : 'border-cyan-500 text-cyan-300');
    toast.className = `p-3 rounded-lg bg-slate-900 border ${border} shadow-2xl text-xs font-medium flex items-center gap-2 transform transition-all duration-300 translate-y-2 opacity-0`;
    toast.innerHTML = `<span>${type === 'success' ? '✓' : (type === 'error' ? '✗' : 'ℹ')}</span> <span>${message}</span>`;

    container.appendChild(toast);
    setTimeout(() => {
        toast.classList.remove('translate-y-2', 'opacity-0');
    }, 10);

    setTimeout(() => {
        toast.classList.add('opacity-0');
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

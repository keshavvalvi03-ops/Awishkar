/**
 * ClauseGuard AI — Client Application Controller
 * Handles SPA navigation, API requests, Chart.js visualizations,
 * modal clause inspection, checklist filters, and PDF export.
 */

// Global State
const state = {
  currentView: 'home',
  currentReport: null,
  currentContractText: '',
  selectedContractType: '',
  sampleData: {},
  checklistFilter: 'ALL',
  clauseLevelFilter: 'ALL',
  clauseSearchQuery: '',
  charts: {
    riskDist: null,
    categoryBar: null,
  },
};

// View Metadata
const VIEW_TITLES = {
  home: { title: 'Overview & Home', subtitle: 'Explainable AI-Based Clause Risk Analyser in Contract' },
  analyze: { title: 'Analyse Contract', subtitle: 'Paste text or upload legal documents for full 6-layer audit' },
  dashboard: { title: 'Risk Dashboard', subtitle: 'Calibrated risk score, summary statistics, and clause matrix' },
  xai: { title: 'Explainable AI (XAI)', subtitle: 'Exact mathematical attribution and keyword modifiers' },
  missing: { title: 'Missing Clauses Checklist', subtitle: 'Contract-specific protection verification across 10 agreement types' },
  interactions: { title: 'Cross-Clause Interaction Traps', subtitle: 'Compounding multi-clause risk combinations and mitigating terms' },
  report: { title: 'Executive Report', subtitle: 'Formal legal memo ready for download or audit print' },
  methodology: { title: 'Architecture & Methodology', subtitle: 'Six-layer research framework and academic foundations' },
};

// Initialization on DOM Load
document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initFormControls();
  initFileUpload();
  initModal();
  fetchInitialData();
});

// ==========================================================================
// 1. Navigation Controller
// ==========================================================================

function initNavigation() {
  const navLinks = document.querySelectorAll('.nav-link');
  navLinks.forEach((link) => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const targetView = link.getAttribute('data-view');
      switchView(targetView);
    });
  });

  // Hero Quick Action Buttons
  document.getElementById('hero-btn-start')?.addEventListener('click', () => switchView('analyze'));
  document.getElementById('hero-btn-sample')?.addEventListener('click', () => loadBaselineSample());
  document.getElementById('hero-btn-methodology')?.addEventListener('click', () => switchView('methodology'));
  document.getElementById('btn-quick-analyze')?.addEventListener('click', () => switchView('analyze'));
  document.getElementById('dash-btn-view-report')?.addEventListener('click', () => switchView('report'));

  // Mobile Menu Toggle
  const mobileToggle = document.getElementById('mobile-toggle');
  const sidebar = document.getElementById('sidebar');
  mobileToggle?.addEventListener('click', () => {
    sidebar.classList.toggle('open');
  });
}

function switchView(viewName) {
  state.currentView = viewName;

  // Update Sidebar active state
  document.querySelectorAll('.nav-link').forEach((link) => {
    if (link.getAttribute('data-view') === viewName) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });

  // Show/Hide View Sections
  document.querySelectorAll('.view-section').forEach((section) => {
    if (section.id === `view-${viewName}`) {
      section.classList.add('active');
    } else {
      section.classList.remove('active');
    }
  });

  // Update Top Header
  const meta = VIEW_TITLES[viewName] || { title: 'ClauseGuard AI', subtitle: '' };
  document.getElementById('header-page-title').textContent = meta.title;
  document.getElementById('header-page-subtitle').textContent = meta.subtitle;

  // Window Scroll to Top
  window.scrollTo({ top: 0, behavior: 'smooth' });

  // Re-render charts if navigating to dashboard and report exists
  if (viewName === 'dashboard' && state.currentReport) {
    setTimeout(renderDashboardCharts, 150);
  }
}

// ==========================================================================
// 2. Data Fetching & Samples Loading
// ==========================================================================

async function fetchInitialData() {
  try {
    const res = await fetch('/api/samples');
    if (res.ok) {
      const data = await res.json();
      state.sampleData = data.samples || {};
    }
  } catch (err) {
    console.warn('Failed loading samples:', err);
  }
}

// ==========================================================================
// 3. Form Controls & Typing Suggestion
// ==========================================================================

function initFormControls() {
  const textInput = document.getElementById('contract-text-input');
  const typeSelect = document.getElementById('contract-type-select');
  const charCounter = document.getElementById('char-counter');
  const clearBtn = document.getElementById('btn-clear-input');
  const runBtn = document.getElementById('btn-run-analysis');
  const acceptSugBtn = document.getElementById('btn-accept-suggestion');

  let suggestDebounce = null;

  textInput?.addEventListener('input', () => {
    const text = textInput.value;
    state.currentContractText = text;
    updateCounter(text);

    // Debounced type suggestion
    clearTimeout(suggestDebounce);
    if (text.trim().length > 40) {
      suggestDebounce = setTimeout(() => requestTypeSuggestion(text), 600);
    } else {
      document.getElementById('live-suggestion-box').style.display = 'none';
    }
  });

  clearBtn?.addEventListener('click', () => {
    textInput.value = '';
    state.currentContractText = '';
    updateCounter('');
    document.getElementById('live-suggestion-box').style.display = 'none';
    document.getElementById('file-status-container').style.display = 'none';
  });

  typeSelect?.addEventListener('change', () => {
    state.selectedContractType = typeSelect.value;
  });

  acceptSugBtn?.addEventListener('click', () => {
    const sugName = document.getElementById('suggested-type-name').textContent;
    if (sugName && sugName !== 'None') {
      typeSelect.value = sugName;
      state.selectedContractType = sugName;
      document.getElementById('live-suggestion-box').style.display = 'none';
    }
  });

  runBtn?.addEventListener('click', () => {
    const text = textInput.value.trim();
    if (!text) {
      alert('Please paste contract text or upload a document before running analysis.');
      return;
    }
    executeAnalysis({
      text: text,
      contract_type: typeSelect.value || null,
      is_sample: false,
    });
  });

  // Quick Demo Buttons
  document.getElementById('btn-load-poc-demo')?.addEventListener('click', loadBaselineSample);
  document.getElementById('btn-load-service-sample')?.addEventListener('click', () => loadSampleByName('Service Agreement'));
  document.getElementById('btn-load-nda-sample')?.addEventListener('click', () => loadSampleByName('NDA / Confidentiality Agreement'));
  document.getElementById('btn-load-saas-sample')?.addEventListener('click', () => loadSampleByName('Software / IT Agreement'));
  document.getElementById('btn-open-samples-modal')?.addEventListener('click', loadBaselineSample);
  document.getElementById('btn-print-report')?.addEventListener('click', () => window.print());
}

function updateCounter(text) {
  const chars = text.length;
  const words = text.trim() ? text.trim().split(/\s+/).length : 0;
  document.getElementById('char-counter').textContent = `${chars.toLocaleString()} characters | ${words.toLocaleString()} words`;
}

async function requestTypeSuggestion(text) {
  try {
    const res = await fetch('/api/suggest-type', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text }),
    });

    if (res.ok) {
      const data = await res.json();
      const box = document.getElementById('live-suggestion-box');
      if (data.primary_suggestion) {
        document.getElementById('suggested-type-name').textContent = data.primary_suggestion;
        const confPercent = Math.round((data.confidence || 0) * 100);
        const badge = document.getElementById('suggested-conf-badge');
        badge.textContent = `${confPercent}% Conf`;

        if (data.is_uncertain) {
          badge.className = 'badge badge-med';
          badge.textContent += ' (Uncertain)';
        } else {
          badge.className = 'badge badge-teal';
        }

        document.getElementById('suggested-evidence-text').textContent = data.explanation || '';
        box.style.display = 'block';
      }
    }
  } catch (err) {
    console.warn('Type suggestion failed:', err);
  }
}

// ==========================================================================
// 4. Genuine File Drag-and-Drop & Upload
// ==========================================================================

function initFileUpload() {
  const dropzone = document.getElementById('file-dropzone');
  const fileInput = document.getElementById('file-input');
  const statusContainer = document.getElementById('file-status-container');

  ['dragenter', 'dragover'].forEach((evt) => {
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach((evt) => {
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
    });
  });

  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    if (dt && dt.files && dt.files.length > 0) {
      handleFileUpload(dt.files[0]);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files && fileInput.files.length > 0) {
      handleFileUpload(fileInput.files[0]);
    }
  });
}

async function handleFileUpload(file) {
  const statusContainer = document.getElementById('file-status-container');
  statusContainer.style.display = 'block';
  statusContainer.innerHTML = `<span class="file-status-pill">⏳ Extracting text from ${file.name}...</span>`;

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch('/api/upload', {
      method: 'POST',
      body: formData,
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'File extraction failed.');
    }

    // Populate textarea with extracted text
    const textInput = document.getElementById('contract-text-input');
    textInput.value = data.text || '';
    state.currentContractText = data.text || '';
    updateCounter(data.text || '');

    statusContainer.innerHTML = `
      <span class="file-status-pill">
        ✓ Loaded <strong>${data.filename}</strong> (${data.word_count.toLocaleString()} words)
      </span>
    `;

    // Apply suggestion if returned
    if (data.suggestion && data.suggestion.primary_suggestion) {
      const typeSelect = document.getElementById('contract-type-select');
      typeSelect.value = data.suggestion.primary_suggestion;
      state.selectedContractType = data.suggestion.primary_suggestion;
    }
  } catch (err) {
    statusContainer.innerHTML = `
      <span class="file-status-pill" style="background:#fef2f2; border-color:#fca5a5; color:#b91c1c;">
        ❌ ${err.message}
      </span>
    `;
  }
}

// ==========================================================================
// 5. Sample Loaders
// ==========================================================================

function loadBaselineSample() {
  const sample = state.sampleData['Baseline Demo (Original PoC)'];
  if (!sample) {
    alert('Sample data loading... Please retry in a moment.');
    return;
  }

  // Populate form
  document.getElementById('contract-text-input').value = sample.text;
  state.currentContractText = sample.text;
  updateCounter(sample.text);
  document.getElementById('contract-type-select').value = 'General Business Agreement';
  state.selectedContractType = 'General Business Agreement';

  // Execute analysis with the exact baseline extractions
  executeAnalysis({
    text: sample.text,
    extractions: sample.extractions,
    contract_type: null,
    is_sample: true,
  });
}

function loadSampleByName(typeName) {
  const sample = state.sampleData[typeName];
  if (!sample) {
    alert(`Sample for ${typeName} not found.`);
    return;
  }

  document.getElementById('contract-text-input').value = sample.text;
  state.currentContractText = sample.text;
  updateCounter(sample.text);
  document.getElementById('contract-type-select').value = sample.contract_type;
  state.selectedContractType = sample.contract_type;

  executeAnalysis({
    text: sample.text,
    extractions: sample.extractions,
    contract_type: sample.contract_type,
    is_sample: true,
  });
}

// ==========================================================================
// 6. Execute Analysis Pipeline via Backend API
// ==========================================================================

async function executeAnalysis(payload) {
  const runBtn = document.getElementById('btn-run-analysis');
  const originalText = runBtn.innerHTML;
  runBtn.disabled = true;
  runBtn.innerHTML = '⏳ Analysing Contract...';

  try {
    const res = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const report = await res.json();
    if (!res.ok) {
      throw new Error(report.detail || 'Analysis error occurred.');
    }

    state.currentReport = report;

    // Update Mode Badge in Header
    const modeBadge = document.getElementById('active-mode-badge');
    const modeText = document.getElementById('mode-text');
    if (payload.is_sample) {
      modeBadge.className = 'mode-badge sample';
      modeText.textContent = 'Demo Benchmark Mode';
    } else {
      modeBadge.className = 'mode-badge live';
      modeText.textContent = 'Live User Analysis';
    }

    // Populate all views with actual analysis results
    renderDashboard(report);
    renderXAI(report);
    renderMissingClauses(report);
    renderInteractions(report);
    renderExecutiveReport(report);

    // Switch to Dashboard View
    switchView('dashboard');
  } catch (err) {
    alert(`Error: ${err.message}`);
  } finally {
    runBtn.disabled = false;
    runBtn.innerHTML = originalText;
  }
}

// ==========================================================================
// 7. Render Dashboard View
// ==========================================================================

function renderDashboard(report) {
  const cr = report.contract_risk || {};
  const sum = report.summary || {};
  const cType = report.contract_type || {};

  // KPI Score Header
  const scoreVal = document.getElementById('dash-score-val');
  const levelBadge = document.getElementById('dash-level-badge');
  const baseScore = document.getElementById('dash-base-score');
  const bonusScore = document.getElementById('dash-bonus-score');
  const confVal = document.getElementById('dash-conf-val');
  const narrative = document.getElementById('dash-risk-narrative');
  const typeLabel = document.getElementById('dash-contract-type');

  scoreVal.textContent = (cr.contract_score !== undefined ? cr.contract_score : 0.0).toFixed(2);
  const lvl = cr.contract_level || 'Low';
  levelBadge.textContent = lvl;
  levelBadge.className = `score-level-badge ${lvl === 'High' ? 'badge-high' : lvl === 'Medium' ? 'badge-med' : 'badge-low'}`;

  baseScore.textContent = cr.base_weighted_score !== undefined ? cr.base_weighted_score : '0.0';
  bonusScore.textContent = cr.interaction_bonus !== undefined ? `+${cr.interaction_bonus}` : '+0.0';
  confVal.textContent = cr.average_confidence !== undefined ? `${Math.round(cr.average_confidence * 100)}%` : 'N/A';

  const typeName = cType.selected_type || (report.suggestion && report.suggestion.primary_suggestion) || 'Commercial Agreement';
  typeLabel.textContent = typeName;

  if (cr.note) {
    narrative.textContent = cr.note;
  } else if (lvl === 'High') {
    narrative.textContent = 'High overall risk detected. Significant financial exposure, restrictive covenants, or compounding interaction traps present.';
  } else if (lvl === 'Medium') {
    narrative.textContent = 'Moderate risk detected. Notable clauses requiring targeted review, negotiation, or reciprocal carve-outs.';
  } else {
    narrative.textContent = 'Low overall risk. Clauses align with standard commercial protections without compounding traps.';
  }

  // Secondary Tiles
  document.getElementById('dash-total-extracted').textContent = sum.total_extracted_clauses || 0;
  document.getElementById('dash-risky-count').textContent = (sum.high_risk_clauses || 0) + (sum.medium_risk_clauses || 0);
  document.getElementById('dash-missing-expected').textContent = sum.missing_expected_clauses || 0;
  document.getElementById('dash-interactions-count').textContent = (cr.interactions || []).length;

  // Render Table
  renderClauseTable(report.clauses || []);
}

function renderClauseTable(clauses) {
  const tbody = document.getElementById('clauses-tbody');
  tbody.innerHTML = '';

  const filterLevel = state.clauseLevelFilter;
  const searchQ = state.clauseSearchQuery.toLowerCase();

  const filtered = clauses.filter((c) => {
    if (filterLevel !== 'ALL' && c.risk_level !== filterLevel) return false;
    if (searchQ && !c.category.toLowerCase().includes(searchQ)) return false;
    return true;
  });

  if (filtered.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" style="text-align: center; color: var(--slate-400); padding: 30px;">
          No matching clauses found for the selected filter.
        </td>
      </tr>
    `;
    return;
  }

  filtered.forEach((c) => {
    const tr = document.createElement('tr');
    const badgeClass = c.risk_level === 'High' ? 'badge-high' : c.risk_level === 'Medium' ? 'badge-med' : c.risk_level === 'Low' ? 'badge-low' : 'badge-na';

    tr.innerHTML = `
      <td><strong>${c.category}</strong></td>
      <td><span style="font-size: 0.8rem; color: var(--slate-600);">${c.risk_type}</span></td>
      <td><strong style="font-size: 0.95rem;">${c.score}</strong>/10</td>
      <td><span class="badge ${badgeClass}">${c.risk_level}</span></td>
      <td>
        <div class="clause-text-snippet">${escapeHtml(c.clause_text || 'No text span recorded')}</div>
      </td>
      <td>
        <button class="btn btn-secondary btn-sm" onclick="openClauseModal('${escapeHtml(c.category)}')">
          Inspect 🔍
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

// Table Filter Event Listeners
document.getElementById('clause-filter-level')?.addEventListener('change', (e) => {
  state.clauseLevelFilter = e.target.value;
  if (state.currentReport) renderClauseTable(state.currentReport.clauses || []);
});

document.getElementById('clause-search-input')?.addEventListener('input', (e) => {
  state.clauseSearchQuery = e.target.value;
  if (state.currentReport) renderClauseTable(state.currentReport.clauses || []);
});

// ==========================================================================
// 8. Chart.js Interactive Visualizations
// ==========================================================================

function renderDashboardCharts() {
  if (!state.currentReport) return;
  const clauses = state.currentReport.clauses || [];

  // Destroy previous instances to prevent canvas reuse errors
  if (state.charts.riskDist) state.charts.riskDist.destroy();
  if (state.charts.categoryBar) state.charts.categoryBar.destroy();

  // 1. Donut Chart: Risk Level Distribution
  const highCount = clauses.filter((c) => c.risk_level === 'High').length;
  const medCount = clauses.filter((c) => c.risk_level === 'Medium').length;
  const lowCount = clauses.filter((c) => c.risk_level === 'Low').length;
  const naCount = clauses.filter((c) => c.risk_level === 'Not Applicable').length;

  const ctxDonut = document.getElementById('chart-risk-dist');
  if (ctxDonut && window.Chart) {
    state.charts.riskDist = new Chart(ctxDonut, {
      type: 'doughnut',
      data: {
        labels: ['High Risk', 'Medium Risk', 'Low Risk', 'Not Applicable'],
        datasets: [
          {
            data: [highCount, medCount, lowCount, naCount],
            backgroundColor: ['#ef4444', '#f59e0b', '#10b981', '#94a3b8'],
            borderWidth: 2,
            borderColor: '#ffffff',
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } },
        },
        cutout: '68%',
      },
    });
  }

  // 2. Bar Chart: Per-Category Scores
  const scoredClauses = clauses.filter((c) => c.risk_level !== 'Not Applicable').slice(0, 8);
  const barLabels = scoredClauses.map((c) => (c.category.length > 20 ? c.category.substring(0, 18) + '...' : c.category));
  const barScores = scoredClauses.map((c) => c.score);
  const barColors = scoredClauses.map((c) => (c.risk_level === 'High' ? '#ef4444' : c.risk_level === 'Medium' ? '#f59e0b' : '#10b981'));

  const ctxBar = document.getElementById('chart-category-bar');
  if (ctxBar && window.Chart) {
    state.charts.categoryBar = new Chart(ctxBar, {
      type: 'bar',
      data: {
        labels: barLabels,
        datasets: [
          {
            label: 'Clause Severity Score (0-10)',
            data: barScores,
            backgroundColor: barColors,
            borderRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y',
        plugins: {
          legend: { display: false },
        },
        scales: {
          x: { max: 10, min: 0, grid: { color: '#f1f5f9' } },
          y: { grid: { display: false } },
        },
      },
    });
  }
}

// ==========================================================================
// 9. Render Explainable AI (XAI)
// ==========================================================================

function renderXAI(report) {
  const container = document.getElementById('xai-cards-container');
  container.innerHTML = '';
  const clauses = report.clauses || [];

  if (clauses.length === 0) {
    container.innerHTML = '<div class="card" style="text-align:center; color:var(--slate-400);">No clauses extracted yet.</div>';
    return;
  }

  clauses.forEach((c) => {
    const card = document.createElement('div');
    const lvlClass = c.risk_level === 'High' ? 'high' : c.risk_level === 'Medium' ? 'med' : 'low';
    card.className = `card xai-card ${lvlClass}`;

    const attr = c.attribution || {};
    let highlightedText = escapeHtml(c.clause_text || '');

    // Highlight identified keywords
    const keywords = Object.keys(attr.keyword_contributions || {});
    keywords.forEach((kw) => {
      const regex = new RegExp(`(${escapeRegex(kw)})`, 'gi');
      highlightedText = highlightedText.replace(regex, `<span class="highlight-kw">$1</span>`);
    });

    let attrRows = `
      <tr><td>Base Category Severity</td><td>${attr.base_severity_contribution || 0}/10</td></tr>
    `;

    keywords.forEach((kw) => {
      const bonus = attr.keyword_contributions[kw];
      attrRows += `<tr><td>Keyword: <code>'${kw}'</code></td><td>${bonus > 0 ? '+' : ''}${bonus}</td></tr>`;
    });

    attrRows += `
      <tr><td>Raw Score Before Confidence</td><td>${attr.raw_score_before_confidence || 0}</td></tr>
      <tr><td>Confidence Calibration Adjustment</td><td>${attr.confidence_weighting_adjustment !== undefined ? attr.confidence_weighting_adjustment : 0}</td></tr>
      <tr style="background:#f8fafc; font-weight:700;"><td>Final Calibrated Score</td><td style="color:var(--teal-accent);">${c.score}/10</td></tr>
    `;

    card.innerHTML = `
      <div class="xai-header">
        <div>
          <div class="xai-category-title">${c.category}</div>
          <span style="font-size:0.78rem; color:var(--slate-500);">${c.risk_type}</span>
        </div>
        <div style="text-align:right;">
          <strong style="font-size:1.15rem;">${c.score}</strong>/10
          <span class="badge ${c.risk_level === 'High' ? 'badge-high' : c.risk_level === 'Medium' ? 'badge-med' : 'badge-low'}">${c.risk_level}</span>
        </div>
      </div>

      <div class="xai-quote-box">
        <strong>Extracted Evidence:</strong><br>
        ${highlightedText || '<em>No explicit text span attached</em>'}
      </div>

      <div style="font-size:0.84rem; color:var(--slate-700); margin-bottom:12px; line-height:1.5;">
        <strong>Justification:</strong> ${escapeHtml(c.explanation || '')}
      </div>

      <div style="font-size:0.78rem; font-weight:700; text-transform:uppercase; color:var(--slate-400); margin-bottom:6px;">
        Feature Attribution Breakdown
      </div>
      <table class="attribution-table">
        ${attrRows}
      </table>
    `;

    container.appendChild(card);
  });
}

// ==========================================================================
// 10. Render Missing Clauses Checklist
// ==========================================================================

function renderMissingClauses(report) {
  const checklist = report.contract_checklist || [];
  const tbody = document.getElementById('checklist-tbody');
  tbody.innerHTML = '';

  // Update Count Pills
  const total = checklist.length;
  const exp = checklist.filter((i) => i.relevance === 'Expected').length;
  const undet = checklist.filter((i) => i.status.includes('Not detected')).length;
  const cond = checklist.filter((i) => i.relevance === 'Conditional').length;
  const opt = checklist.filter((i) => i.relevance === 'Optional').length;

  document.getElementById('count-check-all').textContent = total;
  document.getElementById('count-check-exp').textContent = exp;
  document.getElementById('count-check-undet').textContent = undet;
  document.getElementById('count-check-cond').textContent = cond;
  document.getElementById('count-check-opt').textContent = opt;

  const currentF = state.checklistFilter;
  const filtered = checklist.filter((item) => {
    if (currentF === 'EXPECTED' && item.relevance !== 'Expected') return false;
    if (currentF === 'CONDITIONAL' && item.relevance !== 'Conditional') return false;
    if (currentF === 'OPTIONAL' && item.relevance !== 'Optional') return false;
    if (currentF === 'UNDETECTED' && !item.status.includes('Not detected')) return false;
    return true;
  });

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--slate-400); padding:30px;">No items match this checklist filter.</td></tr>`;
    return;
  }

  filtered.forEach((item) => {
    const tr = document.createElement('tr');
    const isDet = item.status === 'Detected';
    const isUncert = item.status.includes('Uncertain');

    const statusBadge = isDet
      ? `<span class="badge badge-low">✓ Detected</span>`
      : isUncert
      ? `<span class="badge badge-med">⚠️ Uncertain</span>`
      : `<span class="badge badge-high">❌ Not detected</span>`;

    const relBadge =
      item.relevance === 'Expected'
        ? `<span class="badge badge-high" style="font-size:0.7rem;">Expected</span>`
        : item.relevance === 'Conditional'
        ? `<span class="badge badge-teal" style="font-size:0.7rem;">Conditional</span>`
        : `<span class="badge badge-na" style="font-size:0.7rem;">Optional</span>`;

    tr.innerHTML = `
      <td><strong>${item.clause_name}</strong></td>
      <td>${relBadge}</td>
      <td>${statusBadge}</td>
      <td><code style="font-size:0.75rem;">${item.detection_method}</code></td>
      <td style="font-size:0.8rem; color:var(--slate-700); max-width:280px;">${escapeHtml(item.reason)}</td>
      <td style="font-size:0.8rem; color:var(--slate-600); max-width:260px;">${escapeHtml(item.recommended_action || '--')}</td>
    `;
    tbody.appendChild(tr);
  });
}

// Checklist Filter Pill Handler
document.querySelectorAll('.filter-pill[data-check-filter]').forEach((pill) => {
  pill.addEventListener('click', () => {
    document.querySelectorAll('.filter-pill[data-check-filter]').forEach((p) => p.classList.remove('active'));
    pill.classList.add('active');
    state.checklistFilter = pill.getAttribute('data-check-filter');
    if (state.currentReport) renderMissingClauses(state.currentReport);
  });
});

// ==========================================================================
// 11. Render Cross-Clause Interactions
// ==========================================================================

function renderInteractions(report) {
  const container = document.getElementById('interactions-container');
  container.innerHTML = '';
  const cr = report.contract_risk || {};
  const triggered = cr.interactions || [];

  // Known catalog of interaction rules
  const catalog = [
    {
      name: 'Uncapped Financial Exposure',
      bonus: 2.0,
      description: 'Liability is uncapped without a liability cap or insurance to contain exposure.',
      conditions: 'Requires Uncapped Liability present, Cap On Liability absent, Insurance absent.',
    },
    {
      name: 'Exclusive Lock-In Trap',
      bonus: 1.5,
      description: 'An exclusive dealing commitment automatically renews with no convenience exit clause.',
      conditions: 'Requires Exclusivity present, auto-renewing Renewal Term present, Convenience Termination absent.',
    },
    {
      name: 'Abrupt Walkaway Risk',
      bonus: 1.0,
      description: 'Either party can terminate without cause, but no post-termination wind-down or transition obligations exist.',
      conditions: 'Requires Termination For Convenience present, Post-Termination Services absent.',
    },
    {
      name: 'Unbounded IP Grant',
      bonus: 1.5,
      description: 'License granted is perpetual/irrevocable AND unlimited in scope.',
      conditions: 'Requires Perpetual License present AND All-You-Can-Eat License present.',
    },
    {
      name: 'Pricing Power Asymmetry',
      bonus: 1.0,
      description: 'Most Favored Nation clause combines with price increase restrictions.',
      conditions: 'Requires Most Favored Nation present AND Price Restrictions present.',
    },
  ];

  catalog.forEach((rule) => {
    const isTriggered = triggered.some((t) => t.name === rule.name);
    const trigItem = triggered.find((t) => t.name === rule.name);

    const card = document.createElement('div');
    card.className = `interaction-card ${isTriggered ? 'triggered' : ''}`;

    card.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px;">
        <h4 style="font-size:0.98rem; font-weight:700; color:var(--slate-900);">${rule.name}</h4>
        <span class="badge ${isTriggered ? 'badge-high' : 'badge-na'}">
          ${isTriggered ? 'TRIGGERED (+ ' + rule.bonus + ')' : 'Not Triggered'}
        </span>
      </div>

      <p style="font-size:0.84rem; color:var(--slate-700); line-height:1.5; margin-bottom:12px;">
        ${isTriggered ? escapeHtml(trigItem.message) : rule.description}
      </p>

      <div style="font-size:0.75rem; color:var(--slate-500); background:var(--slate-50); padding:8px 12px; border-radius:6px;">
        <strong>Condition Rule:</strong> ${rule.conditions}
      </div>
    `;

    container.appendChild(card);
  });
}

// ==========================================================================
// 12. Render Executive Report
// ==========================================================================

function renderExecutiveReport(report) {
  const cr = report.contract_risk || {};
  const cType = report.contract_type || {};
  const typeName = cType.selected_type || (report.suggestion && report.suggestion.primary_suggestion) || 'Commercial Agreement';

  document.getElementById('rep-contract-title').textContent = `${typeName} — Risk Analysis Memo`;
  document.getElementById('rep-meta-line').textContent = `Document Type: ${typeName} | Date: ${new Date().toLocaleDateString()} | System: ClauseGuard AI v2.0`;

  document.getElementById('rep-overall-score').textContent = `${(cr.contract_score !== undefined ? cr.contract_score : 0.0).toFixed(2)} / 10`;
  const lvl = cr.contract_level || 'Low';
  const lvlBadge = document.getElementById('rep-overall-level');
  lvlBadge.textContent = lvl;
  lvlBadge.className = `badge ${lvl === 'High' ? 'badge-high' : lvl === 'Medium' ? 'badge-med' : 'badge-low'}`;

  // Executive summary
  document.getElementById('rep-exec-summary').textContent = `
    This agreement was evaluated across 6 architectural layers using ClauseGuard AI. 
    The overall contract risk score is ${cr.contract_score}/10 (${lvl} risk). 
    Base weighted clause score is ${cr.base_weighted_score}, with ${cr.interaction_bonus} points contributed by cross-clause compounding interactions. 
    A total of ${(report.clauses || []).length} commercial clauses were extracted with an average extraction confidence of ${Math.round((cr.average_confidence || 0) * 100)}%.
  `;

  // Compounding interactions list
  const intList = document.getElementById('rep-interactions-list');
  const interactions = cr.interactions || [];
  if (interactions.length > 0) {
    intList.innerHTML = `<ul style="padding-left: 20px; line-height: 1.6;">` +
      interactions.map((i) => `<li><strong>${i.name} (+${i.bonus}):</strong> ${escapeHtml(i.message)}</li>`).join('') +
      `</ul>`;
  } else {
    intList.textContent = 'No compounding cross-clause risk interactions were triggered.';
  }

  // Missing clauses list
  const missList = document.getElementById('rep-missing-list');
  const missing = (report.contract_checklist || []).filter((item) => item.status.includes('Not detected') && item.relevance === 'Expected');
  if (missing.length > 0) {
    missList.innerHTML = `<ul style="padding-left: 20px; line-height: 1.6;">` +
      missing.map((m) => `<li><strong>${m.clause_name}:</strong> ${escapeHtml(m.reason)} (Recommended Action: ${escapeHtml(m.recommended_action)})</li>`).join('') +
      `</ul>`;
  } else {
    missList.textContent = 'All Expected essential protections for this contract type were detected.';
  }

  // Clauses table
  const repTbody = document.getElementById('rep-clauses-tbody');
  repTbody.innerHTML = '';
  (report.clauses || []).forEach((c) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${c.category}</strong></td>
      <td>${c.risk_type}</td>
      <td><strong>${c.score}</strong>/10</td>
      <td><span class="badge ${c.risk_level === 'High' ? 'badge-high' : c.risk_level === 'Medium' ? 'badge-med' : 'badge-low'}">${c.risk_level}</span></td>
      <td style="font-size:0.75rem; color:var(--slate-600);">${escapeHtml(c.explanation)}</td>
    `;
    repTbody.appendChild(tr);
  });
}

// ==========================================================================
// 13. Clause Inspector Modal
// ==========================================================================

function initModal() {
  const modal = document.getElementById('clause-modal');
  const closeBtn = document.getElementById('modal-close-btn');
  const dismissBtn = document.getElementById('modal-dismiss-btn');

  const hideModal = () => modal.classList.remove('open');
  closeBtn?.addEventListener('click', hideModal);
  dismissBtn?.addEventListener('click', hideModal);

  modal?.addEventListener('click', (e) => {
    if (e.target === modal) hideModal();
  });
}

window.openClauseModal = function (categoryName) {
  if (!state.currentReport) return;
  const clause = (state.currentReport.clauses || []).find((c) => c.category === categoryName);
  if (!clause) return;

  const modal = document.getElementById('clause-modal');
  document.getElementById('modal-clause-title').textContent = clause.category;
  const badge = document.getElementById('modal-clause-badge');
  badge.textContent = `${clause.risk_level} (${clause.score}/10)`;
  badge.className = `badge ${clause.risk_level === 'High' ? 'badge-high' : clause.risk_level === 'Medium' ? 'badge-med' : 'badge-low'}`;

  document.getElementById('modal-clause-risk-type').textContent = clause.risk_type;
  document.getElementById('modal-clause-text').textContent = clause.clause_text || 'No text span recorded.';
  document.getElementById('modal-clause-explanation').textContent = clause.explanation || '';

  const attr = clause.attribution || {};
  let attrRows = `
    <tr><td>Base Severity Rating</td><td>${attr.base_severity_contribution || 0}/10</td></tr>
  `;
  const kws = Object.keys(attr.keyword_contributions || {});
  kws.forEach((kw) => {
    const val = attr.keyword_contributions[kw];
    attrRows += `<tr><td>Keyword: '${kw}'</td><td>${val > 0 ? '+' : ''}${val}</td></tr>`;
  });
  attrRows += `
    <tr><td>Raw Score Before Confidence</td><td>${attr.raw_score_before_confidence || 0}</td></tr>
    <tr><td>Confidence Weighting Adjustment</td><td>${attr.confidence_weighting_adjustment || 0}</td></tr>
    <tr style="background:#f1f5f9; font-weight:700;"><td>Final Calibrated Score</td><td style="color:var(--teal-accent);">${clause.score}/10</td></tr>
  `;
  document.getElementById('modal-attribution-table').innerHTML = attrRows;

  modal.classList.add('open');
};

// ==========================================================================
// 14. Utilities
// ==========================================================================

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

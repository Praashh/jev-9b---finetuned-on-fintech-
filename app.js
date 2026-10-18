/**
 * FinTech Transaction Guardian - Frontend Application Logic
 * Interactive decision inspector, live gateway streaming, benchmark switching
 */

// Resilient API Base:
// If opened via Live Server (port 5500/5501) or file://, target FastAPI at http://127.0.0.1:8000
let API_BASE = (typeof window !== 'undefined' && window.API_BASE !== undefined)
  ? window.API_BASE
  : (window.location.port === '8000' ? '' : 'http://127.0.0.1:8000');

let appState = {
  activeTab: 'inspector',
  activeModel: 'default/jev-9b-v1',
  samples: [],
  activeSampleId: null,
  isStreaming: false,
  streamInterval: null,
  streamStats: {
    total: 0,
    approved: 0,
    blocked: 0,
    reviewed: 0,
    latencies: []
  }
};

// DOM Elements
const elements = {
  tabs: document.querySelectorAll('.nav-tab'),
  panes: document.querySelectorAll('.tab-pane'),
  activeModelSelect: document.getElementById('active-model-select'),
  endorStatusText: document.getElementById('endor-status-text'),
  endorStatusPill: document.getElementById('endor-status-pill'),
  utcClock: document.getElementById('utc-clock'),
  presetChipsContainer: document.getElementById('preset-chips-container'),
  payloadEditor: document.getElementById('payload-editor'),
  btnFormatJson: document.getElementById('btn-format-json'),
  btnResetJson: document.getElementById('btn-reset-json'),
  btnAnalyze: document.getElementById('btn-analyze'),
  latencyTag: document.getElementById('latency-tag'),
  evaluatedModelBadge: document.getElementById('evaluated-model-badge'),
  actionBanner: document.getElementById('action-banner'),
  actionIcon: document.getElementById('action-icon'),
  actionHeading: document.getElementById('action-heading'),
  actionSub: document.getElementById('action-sub'),
  riskBadge: document.getElementById('risk-badge'),
  fraudGaugePath: document.getElementById('fraud-gauge-path'),
  fraudGaugeValue: document.getElementById('fraud-gauge-value'),
  approveGaugePath: document.getElementById('approve-gauge-path'),
  approveGaugeValue: document.getElementById('approve-gauge-value'),
  amlGaugePath: document.getElementById('aml-gauge-path'),
  amlGaugeValue: document.getElementById('aml-gauge-value'),
  predictedCatLabel: document.getElementById('predicted-cat-label'),
  categoryBarsContainer: document.getElementById('category-bars-container'),
  reasonsList: document.getElementById('reasons-list'),
  btnToggleStream: document.getElementById('btn-toggle-stream'),
  streamToggleText: document.getElementById('stream-toggle-text'),
  btnStreamSingle: document.getElementById('btn-stream-single'),
  btnClearStream: document.getElementById('btn-clear-stream'),
  streamTbody: document.getElementById('stream-tbody'),
  statTotalTx: document.getElementById('stat-total-tx'),
  statApproveRate: document.getElementById('stat-approve-rate'),
  statBlockRate: document.getElementById('stat-block-rate'),
  statReviewRate: document.getElementById('stat-review-rate'),
  statAvgLatency: document.getElementById('stat-avg-latency'),
  dsTrainCount: document.getElementById('ds-train-count'),
  dsEvalCount: document.getElementById('ds-eval-count')
};

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
  initClock();
  initTabs();
  initModelSelect();
  initEditor();
  initStream();
  fetchStatus();
  fetchSamples();
});

// Live UTC Clock
function initClock() {
  function update() {
    const now = new Date();
    const utcStr = now.toUTCString().split(' ')[4];
    if (elements.utcClock) elements.utcClock.textContent = `UTC ${utcStr}`;
  }
  update();
  setInterval(update, 1000);
}

// Navigation Tabs
function initTabs() {
  elements.tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.tab;
      switchTab(target);
    });
  });
}

function switchTab(tabId) {
  appState.activeTab = tabId;
  elements.tabs.forEach(t => t.classList.toggle('active', t.dataset.tab === tabId));
  elements.panes.forEach(p => p.classList.toggle('active', p.id === `pane-${tabId}`));
}

// Model Selection
function initModelSelect() {
  if (!elements.activeModelSelect) return;
  elements.activeModelSelect.addEventListener('change', (e) => {
    selectModel(e.target.value);
  });
}

function selectModel(modelName) {
  appState.activeModel = modelName;
  if (elements.activeModelSelect) elements.activeModelSelect.value = modelName;
  if (elements.evaluatedModelBadge) elements.evaluatedModelBadge.textContent = modelName;
  
  fetch(`${API_BASE}/api/model-select`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: modelName })
  }).catch(() => {});

  if (appState.activeTab !== 'inspector') {
    switchTab('inspector');
  }

  // Re-run evaluation on current payload
  analyzeCurrentPayload();
}

// Server Status Check
async function fetchStatus() {
  try {
    let res = await fetch(`${API_BASE}/api/status`);
    if (!res.ok && API_BASE !== 'http://127.0.0.1:8000') {
      API_BASE = 'http://127.0.0.1:8000';
      res = await fetch(`${API_BASE}/api/status`);
    }
    const data = await res.json();
    if (data.status === 'online') {
      if (elements.endorStatusText) {
        elements.endorStatusText.textContent = data.connected_to_endor 
          ? 'ENDOR API CONNECTED' 
          : 'ONLINE (FASTAPI :8000)';
      }
      if (elements.endorStatusPill) {
        elements.endorStatusPill.className = 'status-indicator status-online';
      }
      if (data.dataset) {
        if (elements.dsTrainCount) elements.dsTrainCount.textContent = data.dataset.train_rows;
        if (elements.dsEvalCount) elements.dsEvalCount.textContent = data.dataset.eval_rows;
      }
    }
  } catch (err) {
    // Fallback attempt to http://127.0.0.1:8000 directly
    if (API_BASE !== 'http://127.0.0.1:8000') {
      try {
        API_BASE = 'http://127.0.0.1:8000';
        const res = await fetch(`${API_BASE}/api/status`);
        const data = await res.json();
        if (data.status === 'online') {
          if (elements.endorStatusText) {
            elements.endorStatusText.textContent = data.connected_to_endor 
              ? 'ENDOR API CONNECTED' 
              : 'ONLINE (FASTAPI :8000)';
          }
          if (elements.endorStatusPill) {
            elements.endorStatusPill.className = 'status-indicator status-online';
          }
          return;
        }
      } catch (e) {}
    }
    if (elements.endorStatusText) elements.endorStatusText.textContent = 'SERVER OFFLINE (:8000)';
    if (elements.endorStatusPill) elements.endorStatusPill.className = 'status-indicator status-offline';
  }
}

// Fetch Preset Scenarios
async function fetchSamples() {
  try {
    let res = await fetch(`${API_BASE}/api/samples`);
    if (!res.ok && API_BASE !== 'http://127.0.0.1:8000') {
      API_BASE = 'http://127.0.0.1:8000';
      res = await fetch(`${API_BASE}/api/samples`);
    }
    appState.samples = await res.json();
    renderPresetChips();
    if (appState.samples.length > 0) {
      loadSample(appState.samples[0]);
    }
  } catch (err) {
    if (API_BASE !== 'http://127.0.0.1:8000') {
      try {
        API_BASE = 'http://127.0.0.1:8000';
        const res = await fetch(`${API_BASE}/api/samples`);
        appState.samples = await res.json();
        renderPresetChips();
        if (appState.samples.length > 0) {
          loadSample(appState.samples[0]);
        }
      } catch (e) {
        console.error('Failed to load samples:', e);
      }
    }
  }
}

function renderPresetChips() {
  if (!elements.presetChipsContainer) return;
  elements.presetChipsContainer.innerHTML = '';
  appState.samples.forEach((sample, idx) => {
    const chip = document.createElement('button');
    chip.className = `scenario-chip ${idx === 0 ? 'active' : ''}`;
    chip.textContent = sample.title;
    chip.dataset.id = sample.id;
    chip.addEventListener('click', () => loadSample(sample));
    elements.presetChipsContainer.appendChild(chip);
  });
}

function loadSample(sample) {
  appState.activeSampleId = sample.id;
  document.querySelectorAll('.scenario-chip').forEach(c => {
    c.classList.toggle('active', c.dataset.id === sample.id);
  });

  if (elements.payloadEditor) {
    elements.payloadEditor.value = JSON.stringify(sample.data, null, 2);
  }
  analyzeCurrentPayload();
}

// Editor Controls
function initEditor() {
  if (elements.btnFormatJson) {
    elements.btnFormatJson.addEventListener('click', () => {
      try {
        const obj = JSON.parse(elements.payloadEditor.value);
        elements.payloadEditor.value = JSON.stringify(obj, null, 2);
      } catch (e) {
        alert('Invalid JSON syntax: ' + e.message);
      }
    });
  }

  if (elements.btnResetJson) {
    elements.btnResetJson.addEventListener('click', () => {
      if (appState.activeSampleId) {
        const s = appState.samples.find(x => x.id === appState.activeSampleId);
        if (s) loadSample(s);
      }
    });
  }

  if (elements.btnAnalyze) {
    elements.btnAnalyze.addEventListener('click', () => {
      analyzeCurrentPayload();
    });
  }
}

// Analyze Current Payload
async function analyzeCurrentPayload() {
  if (!elements.btnAnalyze || !elements.payloadEditor) return;
  elements.btnAnalyze.disabled = true;
  elements.btnAnalyze.textContent = 'ANALYZING...';

  let payloadObj = null;
  try {
    payloadObj = JSON.parse(elements.payloadEditor.value);
  } catch (err) {
    alert('JSON parse error: ' + err.message);
    elements.btnAnalyze.disabled = false;
    elements.btnAnalyze.textContent = 'ANALYZE TRANSACTION';
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/api/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payloadObj)
    });
    const result = await res.json();
    renderDecision(result);
  } catch (err) {
    console.error('Analysis request error:', err);
  } finally {
    elements.btnAnalyze.disabled = false;
    elements.btnAnalyze.textContent = 'ANALYZE TRANSACTION';
  }
}

// Render Decision Telemetry
function renderDecision(result) {
  const dec = result.decision;
  const dist = result.distributions;
  const analysis = result.risk_analysis;

  // Metadata
  if (elements.latencyTag) elements.latencyTag.textContent = `LATENCY: ${result.latency_ms}MS`;
  if (elements.evaluatedModelBadge) elements.evaluatedModelBadge.textContent = result.model_used;

  // Action Banner & Styling
  const actionClassMap = {
    'auto_approve': 'action-auto-approve',
    'hard_block': 'action-hard-block',
    'manual_review': 'action-manual-review',
    'step_up_2fa': 'action-step-up-2fa'
  };

  const actionTitleMap = {
    'auto_approve': 'AUTO-APPROVE',
    'hard_block': 'DECLINE & HARD BLOCK',
    'manual_review': 'HOLD FOR MANUAL REVIEW',
    'step_up_2fa': 'STEP-UP 2FA CHALLENGE'
  };

  const actionCodeMap = {
    'auto_approve': '[APPROVE]',
    'hard_block': '[BLOCK]',
    'manual_review': '[REVIEW]',
    'step_up_2fa': '[CHALLENGE]'
  };

  if (elements.actionBanner) {
    elements.actionBanner.className = `verdict-banner ${actionClassMap[dec.action] || 'action-auto-approve'}`;
  }
  if (elements.actionHeading) {
    elements.actionHeading.textContent = actionTitleMap[dec.action] || dec.action.toUpperCase();
  }
  if (elements.actionIcon) {
    elements.actionIcon.textContent = actionCodeMap[dec.action] || '[DECISION]';
  }
  if (elements.actionSub) {
    elements.actionSub.textContent = analysis.policy_summary;
  }

  // Risk Badge
  const riskClassMap = {
    'low': 'risk-low',
    'medium': 'risk-medium',
    'high': 'risk-high',
    'critical': 'risk-critical'
  };
  if (elements.riskBadge) {
    elements.riskBadge.className = `risk-pill ${riskClassMap[dec.risk_level] || 'risk-low'}`;
    elements.riskBadge.textContent = `RISK: ${dec.risk_level.toUpperCase()}`;
  }

  // Metric Meters
  const fraudPct = Math.round(dec.fraud_probability * 100);
  const approvePct = Math.round((dist.action.auto_approve || 0) * 100);
  const amlPct = Math.round(dec.aml_probability * 100);

  setMeter(elements.fraudGaugePath, elements.fraudGaugeValue, fraudPct);
  setMeter(elements.approveGaugePath, elements.approveGaugeValue, approvePct);
  setMeter(elements.amlGaugePath, elements.amlGaugeValue, amlPct);

  // Category Breakdown Bars
  renderCategoryBars(dist.category, dec.predicted_category);

  // Reasons & Risk Indicators
  if (elements.reasonsList) {
    elements.reasonsList.innerHTML = '';
    if (analysis.reasons && analysis.reasons.length > 0) {
      analysis.reasons.forEach(r => {
        const li = document.createElement('li');
        li.innerHTML = `<span class="audit-tag flag">[FLAG]</span> <span>${escapeHtml(r)}</span>`;
        elements.reasonsList.appendChild(li);
      });
    } else {
      elements.reasonsList.innerHTML = '<li><span class="audit-tag pass">[PASS]</span> Verified customer baseline: Trusted device, matching geo-IP. Clean profile.</li>';
    }
  }
}

function setMeter(barFillEl, textEl, percentage) {
  const clamped = Math.max(0, Math.min(100, percentage));
  if (textEl) textEl.textContent = `${clamped}%`;
  if (barFillEl) {
    if (barFillEl.tagName && barFillEl.tagName.toLowerCase() === 'path') {
      barFillEl.setAttribute('stroke-dasharray', `${clamped}, 100`);
    } else {
      barFillEl.style.width = `${clamped}%`;
    }
  }
}

function renderCategoryBars(categoryProbs, predictedCat) {
  if (elements.predictedCatLabel) {
    elements.predictedCatLabel.textContent = `${predictedCat} (${Math.round((categoryProbs[predictedCat] || 0) * 100)}%)`;
  }
  if (!elements.categoryBarsContainer) return;
  elements.categoryBarsContainer.innerHTML = '';

  const entries = Object.entries(categoryProbs).sort((a, b) => b[1] - a[1]);
  entries.forEach(([cat, prob]) => {
    const pct = Math.round(prob * 100);
    const row = document.createElement('div');
    row.className = 'cat-bar-row';
    row.innerHTML = `
      <span class="cat-bar-name">${cat}</span>
      <div class="cat-bar-track">
        <div class="cat-bar-fill" style="width: ${pct}%"></div>
      </div>
      <span class="cat-bar-pct">${pct}%</span>
    `;
    elements.categoryBarsContainer.appendChild(row);
  });
}

// Live Gateway Streaming
function initStream() {
  if (elements.btnToggleStream) {
    elements.btnToggleStream.addEventListener('click', toggleStream);
  }
  if (elements.btnStreamSingle) {
    elements.btnStreamSingle.addEventListener('click', () => injectStreamRow());
  }
  if (elements.btnClearStream) {
    elements.btnClearStream.addEventListener('click', clearStream);
  }
}

function toggleStream() {
  appState.isStreaming = !appState.isStreaming;
  if (appState.isStreaming) {
    elements.btnToggleStream.classList.add('btn-active');
    if (elements.streamToggleText) elements.streamToggleText.textContent = 'PAUSE GATEWAY FEED';
    injectStreamRow();
    appState.streamInterval = setInterval(injectStreamRow, 2200);
  } else {
    clearInterval(appState.streamInterval);
    elements.btnToggleStream.classList.remove('btn-active');
    if (elements.streamToggleText) elements.streamToggleText.textContent = 'START GATEWAY FEED';
  }
}

async function injectStreamRow() {
  try {
    const res = await fetch(`${API_BASE}/api/stream`);
    const decision = await res.json();
    addStreamRow(decision);
  } catch (err) {
    console.error('Stream inject error:', err);
  }
}

function addStreamRow(decision) {
  const tbody = elements.streamTbody;
  if (!tbody) return;
  const emptyRow = tbody.querySelector('.empty-row');
  if (emptyRow) emptyRow.remove();

  const state = decision.state_snapshot || {};
  const dec = decision.decision;
  const lat = decision.latency_ms;

  // Update Stats
  appState.streamStats.total++;
  if (dec.action === 'auto_approve') appState.streamStats.approved++;
  else if (dec.action === 'hard_block') appState.streamStats.blocked++;
  else appState.streamStats.reviewed++;
  appState.streamStats.latencies.push(lat);

  updateStreamStatsUI();

  // Create Table Row
  const tr = document.createElement('tr');
  tr.className = 'stream-row-item';

  const amtFormatted = state.currency === 'INR' 
    ? `₹${Number(state.amount).toLocaleString('en-IN')}` 
    : `$${Number(state.amount).toFixed(2)}`;

  const fraudPct = Math.round(dec.fraud_probability * 100);
  const fraudClass = fraudPct >= 80 ? 'val-red' : (fraudPct >= 40 ? 'val-yellow' : 'val-green');

  tr.innerHTML = `
    <td><code>${state.timestamp_utc || 'Just now'}</code></td>
    <td><code>${state.transaction_id || 'tx_unknown'}</code></td>
    <td><strong>${amtFormatted}</strong></td>
    <td>${escapeHtml(state.counterparty || 'N/A')}</td>
    <td><code>${dec.predicted_category}</code></td>
    <td class="${fraudClass}"><strong>${fraudPct}%</strong></td>
    <td><span class="risk-pill risk-${dec.risk_level}">${dec.risk_level.toUpperCase()}</span></td>
    <td><span class="action-pill action-${dec.action}">${dec.action.replace('_', ' ').toUpperCase()}</span></td>
    <td><button class="btn btn-sm btn-outline" onclick='inspectFromStream(${JSON.stringify(state)})'>INSPECT</button></td>
  `;

  tbody.insertBefore(tr, tbody.firstChild);

  // Keep max 50 rows
  if (tbody.children.length > 50) {
    tbody.removeChild(tbody.lastChild);
  }
}

function updateStreamStatsUI() {
  const s = appState.streamStats;
  if (elements.statTotalTx) elements.statTotalTx.textContent = s.total;
  if (elements.statApproveRate) elements.statApproveRate.textContent = `${Math.round((s.approved / s.total) * 100)}%`;
  if (elements.statBlockRate) elements.statBlockRate.textContent = `${Math.round((s.blocked / s.total) * 100)}%`;
  if (elements.statReviewRate) elements.statReviewRate.textContent = `${Math.round((s.reviewed / s.total) * 100)}%`;

  if (elements.statAvgLatency) {
    const avgLat = Math.round(s.latencies.reduce((a, b) => a + b, 0) / s.latencies.length);
    elements.statAvgLatency.textContent = `${avgLat} ms`;
  }
}

function clearStream() {
  if (elements.streamTbody) {
    elements.streamTbody.innerHTML = `
      <tr class="empty-row">
        <td colspan="9">Log cleared. Click "START GATEWAY FEED" to stream incoming transactions.</td>
      </tr>
    `;
  }
  appState.streamStats = { total: 0, approved: 0, blocked: 0, reviewed: 0, latencies: [] };
  if (elements.statTotalTx) elements.statTotalTx.textContent = '0';
  if (elements.statApproveRate) elements.statApproveRate.textContent = '0%';
  if (elements.statBlockRate) elements.statBlockRate.textContent = '0%';
  if (elements.statReviewRate) elements.statReviewRate.textContent = '0%';
  if (elements.statAvgLatency) elements.statAvgLatency.textContent = '0 ms';
}

function inspectFromStream(state) {
  if (elements.payloadEditor) {
    elements.payloadEditor.value = JSON.stringify(state, null, 2);
  }
  switchTab('inspector');
  analyzeCurrentPayload();
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

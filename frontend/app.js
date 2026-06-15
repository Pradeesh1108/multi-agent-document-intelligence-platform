/**
 * Multi-Agent Document Intelligence Platform — Frontend Application
 *
 * Vanilla JavaScript application handling:
 * - File upload (drag-and-drop + click)
 * - Text input for emails/JSON
 * - API communication with FastAPI backend
 * - Dynamic results rendering with rich UI components
 */

// ============================================================
// Configuration
// ============================================================
const API_BASE = window.location.origin;
const ENDPOINTS = {
    process: `${API_BASE}/documents/process`,
    upload: `${API_BASE}/documents/upload`,
    workflowRun: `${API_BASE}/workflow/run`,
    health: `${API_BASE}/health`,
    ragIngest: `${API_BASE}/rag/ingest`,
};

// Pipeline node definitions
const PIPELINE_NODES = [
    { id: 'intake', icon: '📥', label: 'Intake' },
    { id: 'intent', icon: '🎯', label: 'Intent' },
    { id: 'extraction', icon: '🔍', label: 'Extract' },
    { id: 'knowledge', icon: '📚', label: 'Knowledge' },
    { id: 'risk', icon: '⚡', label: 'Risk' },
    { id: 'decision', icon: '🧠', label: 'Decision' },
    { id: 'action', icon: '🚀', label: 'Action' },
];

// ============================================================
// State
// ============================================================
let selectedFile = null;
let activeTab = 'upload';

// ============================================================
// DOM Ready
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initDropZone();
    initSubmitButton();
    renderPipeline([]);
});

// ============================================================
// Tabs
// ============================================================
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.dataset.tab;
            activateTab(tabId);
        });
    });
}

function activateTab(tabId) {
    activeTab = tabId;
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabId);
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `tab-${tabId}`);
    });
}

// ============================================================
// File Upload / Drop Zone
// ============================================================
function initDropZone() {
    const dropZone = document.getElementById('dropZone');
    if (!dropZone) return;

    const fileInput = dropZone.querySelector('input[type="file"]');

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length > 0) {
            handleFileSelected(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelected(e.target.files[0]);
        }
    });
}

function handleFileSelected(file) {
    const allowedExts = ['pdf', 'json', 'txt', 'eml'];
    const ext = file.name.split('.').pop().toLowerCase();

    if (!allowedExts.includes(ext)) {
        alert(`Unsupported file type: .${ext}\nSupported: .pdf, .json, .txt, .eml`);
        return;
    }

    selectedFile = file;
    renderFilePreview(file);
}

function renderFilePreview(file) {
    const previewContainer = document.getElementById('filePreview');
    const sizeKB = (file.size / 1024).toFixed(1);

    previewContainer.innerHTML = `
        <div class="file-preview">
            <span>📄</span>
            <span class="file-name">${file.name}</span>
            <span class="file-size">${sizeKB} KB</span>
            <button class="remove-file" onclick="removeFile()" title="Remove file">✕</button>
        </div>
    `;
}

function removeFile() {
    selectedFile = null;
    document.getElementById('filePreview').innerHTML = '';
    const fileInput = document.querySelector('#dropZone input[type="file"]');
    if (fileInput) fileInput.value = '';
}

// ============================================================
// Submit
// ============================================================
function initSubmitButton() {
    const btn = document.getElementById('submitBtn');
    if (btn) {
        btn.addEventListener('click', handleSubmit);
    }
}

async function handleSubmit() {
    const btn = document.getElementById('submitBtn');
    const resultsSection = document.getElementById('resultsSection');
    const provider = document.getElementById('providerSelect').value;

    // Determine input
    let hasInput = false;
    const formData = new FormData();

    if (activeTab === 'upload' && selectedFile) {
        formData.append('file', selectedFile);
        hasInput = true;
    } else if (activeTab === 'text') {
        const textInput = document.getElementById('textInput').value.trim();
        if (textInput) {
            formData.append('raw_text_input', textInput);
            hasInput = true;
        }
    }

    if (!hasInput) {
        alert('Please provide a file or paste text content before submitting.');
        return;
    }

    if (provider) {
        formData.append('llm_provider', provider);
    }

    // Show loading state
    btn.disabled = true;
    btn.classList.add('loading');
    btn.textContent = '⏳ Processing through 7 Agent Pipeline...';
    resultsSection.classList.remove('hidden');

    // Animate pipeline
    renderPipeline([]);
    await animatePipelineSequence();

    try {
        const response = await fetch(ENDPOINTS.process, {
            method: 'POST',
            body: formData,
        });

        const result = await response.json();

        if (response.ok) {
            renderPipeline(PIPELINE_NODES.map(n => n.id)); // All completed
            renderResults(result);
        } else {
            renderError(result.detail || 'Processing failed. Check the backend logs.');
            renderPipeline([]);
        }
    } catch (error) {
        console.error('Request failed:', error);
        renderError(`Connection failed: ${error.message}. Is the backend running?`);
        renderPipeline([]);
    } finally {
        btn.disabled = false;
        btn.classList.remove('loading');
        btn.textContent = '🚀 Process Document';
    }
}

// ============================================================
// Pipeline Visualization
// ============================================================
function renderPipeline(completedNodes) {
    const container = document.getElementById('pipelineVisual');
    if (!container) return;

    container.innerHTML = PIPELINE_NODES.map((node, i) => {
        const isCompleted = completedNodes.includes(node.id);
        const nodeClass = isCompleted ? 'completed' : '';
        const arrowClass = isCompleted ? 'completed' : '';

        let html = `
            <div class="pipeline-step">
                <div class="pipeline-node ${nodeClass}" id="pipe-${node.id}">
                    <span class="node-icon">${isCompleted ? '✅' : node.icon}</span>
                    <span class="node-label">${node.label}</span>
                </div>
        `;

        if (i < PIPELINE_NODES.length - 1) {
            html += `<span class="pipeline-arrow ${arrowClass}">→</span>`;
        }

        html += '</div>';
        return html;
    }).join('');
}

async function animatePipelineSequence() {
    for (let i = 0; i < PIPELINE_NODES.length; i++) {
        const node = PIPELINE_NODES[i];
        const el = document.getElementById(`pipe-${node.id}`);
        if (el) {
            el.classList.add('active');
            await sleep(200);
            el.classList.remove('active');
        }
    }
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// ============================================================
// Results Rendering
// ============================================================
function renderResults(data) {
    const container = document.getElementById('resultsContent');
    container.innerHTML = '';

    // Processing stats bar
    container.appendChild(renderProcessingStats(data));

    // Results grid
    const grid = document.createElement('div');
    grid.className = 'results-grid';

    // Intent Card
    if (data.intent) {
        grid.appendChild(renderIntentCard(data.intent));
    }

    // Entities Card
    if (data.extracted_entities) {
        grid.appendChild(renderEntitiesCard(data.extracted_entities));
    }

    // Knowledge Card
    if (data.retrieved_context && data.retrieved_context.length > 0) {
        grid.appendChild(renderKnowledgeCard(data.retrieved_context));
    }

    // Risk Card
    if (data.risk_analysis) {
        grid.appendChild(renderRiskCard(data.risk_analysis));
    }

    // Decision Card
    if (data.decision) {
        grid.appendChild(renderDecisionCard(data.decision));
    }

    // Actions Card
    if (data.actions && data.actions.length > 0) {
        grid.appendChild(renderActionsCard(data.actions));
    }

    container.appendChild(grid);

    // Errors
    if (data.errors && data.errors.length > 0) {
        container.appendChild(renderErrorsCard(data.errors));
    }
}

function renderProcessingStats(data) {
    const stats = document.createElement('div');
    stats.className = 'processing-stats';

    const items = [
        { value: data.workflow_id || '—', label: 'Workflow ID' },
        { value: data.file_type || '—', label: 'File Type' },
        { value: data.status || '—', label: 'Status' },
        { value: data.processing_time_ms ? `${data.processing_time_ms.toFixed(0)}ms` : '—', label: 'Processing Time' },
    ];

    stats.innerHTML = items.map(item => `
        <div class="stat-item">
            <span class="stat-value">${item.value}</span>
            <span class="stat-label">${item.label}</span>
        </div>
    `).join('');

    return stats;
}

function renderIntentCard(intent) {
    const card = createResultCard('🎯', 'Intent Classification');
    const confidencePercent = Math.round((intent.confidence || 0) * 100);

    card.querySelector('.result-card-body').innerHTML = `
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
            <span class="badge intent">${intent.intent || 'unknown'}</span>
            <span style="font-size:0.8125rem;color:var(--text-muted)">${confidencePercent}% confidence</span>
        </div>
        <div class="confidence-bar">
            <div class="confidence-bar-fill" style="width:${confidencePercent}%"></div>
        </div>
        <p style="margin-top:12px;font-size:0.8125rem;color:var(--text-secondary)">${intent.reasoning || ''}</p>
    `;

    return card;
}

function renderEntitiesCard(entities) {
    const card = createResultCard('🔍', 'Extracted Entities');
    const entityData = entities.entities || {};
    const entityType = entities.entity_type || 'generic';

    let html = `<div class="badge intent" style="margin-bottom:12px">${entityType}</div>`;
    html += '<div class="kv-grid">';

    for (const [key, value] of Object.entries(entityData)) {
        if (value === null || value === undefined) continue;
        const displayValue = typeof value === 'object' ? JSON.stringify(value) : String(value);
        html += `
            <div class="kv-row">
                <span class="kv-key">${formatKey(key)}</span>
                <span class="kv-value">${truncate(displayValue, 80)}</span>
            </div>
        `;
    }

    html += '</div>';
    card.querySelector('.result-card-body').innerHTML = html;
    return card;
}

function renderKnowledgeCard(contexts) {
    const card = createResultCard('📚', 'Retrieved Knowledge');

    let html = '';
    contexts.forEach(chunk => {
        html += `<div class="context-chunk">${truncate(chunk, 300)}</div>`;
    });

    card.querySelector('.result-card-body').innerHTML = html;
    return card;
}

function renderRiskCard(risk) {
    const card = createResultCard('⚡', 'Risk Assessment');
    const level = risk.risk_level || 'low';
    const score = risk.risk_score || 0;

    let html = `
        <div class="risk-meter ${level}">
            <div class="risk-score-circle ${level}">${(score * 100).toFixed(0)}%</div>
            <div class="risk-details">
                <div class="risk-level-label ${level}">${level.toUpperCase()} RISK</div>
                <div style="font-size:0.8125rem;color:var(--text-secondary);margin-top:2px">
                    ${risk.recommended_action || ''}
                </div>
            </div>
        </div>
    `;

    if (risk.risk_factors && risk.risk_factors.length > 0) {
        html += '<ul class="risk-factors-list">';
        risk.risk_factors.forEach(factor => {
            html += `<li>${factor}</li>`;
        });
        html += '</ul>';
    }

    if (risk.explanation) {
        html += `<p style="margin-top:12px;font-size:0.8125rem;color:var(--text-muted)">${risk.explanation}</p>`;
    }

    card.querySelector('.result-card-body').innerHTML = html;
    return card;
}

function renderDecisionCard(decision) {
    const card = createResultCard('🧠', 'Workflow Decision');
    const confidence = Math.round((decision.confidence || 0) * 100);

    card.querySelector('.result-card-body').innerHTML = `
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px">
            <span class="badge intent">${formatDecision(decision.decision)}</span>
            <span class="badge ${decision.priority === 'high' || decision.priority === 'critical' ? 'failed' : 'success'}">
                ${(decision.priority || 'medium').toUpperCase()}
            </span>
        </div>
        <div class="confidence-bar" style="margin-bottom:12px">
            <div class="confidence-bar-fill" style="width:${confidence}%"></div>
        </div>
        <p style="font-size:0.8125rem;color:var(--text-secondary)">${decision.reasoning || ''}</p>
    `;

    return card;
}

function renderActionsCard(actions) {
    const card = createResultCard('🚀', 'Actions Executed');

    let html = '<div class="action-timeline">';
    actions.forEach(action => {
        html += `
            <div class="action-item">
                <div class="action-dot ${action.status || 'skipped'}"></div>
                <div class="action-content">
                    <div class="action-type">${formatKey(action.action_type || 'unknown')}</div>
                    <div class="action-status">
                        <span class="badge ${action.status === 'success' ? 'success' : 'failed'}">${action.status || 'unknown'}</span>
                    </div>
                </div>
            </div>
        `;
    });
    html += '</div>';

    card.querySelector('.result-card-body').innerHTML = html;
    return card;
}

function renderErrorsCard(errors) {
    const card = createResultCard('⚠️', 'Errors');
    card.querySelector('.result-card-body').innerHTML = errors.map(err =>
        `<div class="context-chunk" style="border-color:rgba(239,68,68,0.2);color:var(--risk-high)">${err}</div>`
    ).join('');
    return card;
}

function renderError(message) {
    const container = document.getElementById('resultsContent');
    container.innerHTML = `
        <div class="result-card" style="border-color:rgba(239,68,68,0.3)">
            <div class="result-card-header">
                <div class="result-card-title">
                    <span class="card-icon">❌</span>
                    Error
                </div>
            </div>
            <p style="color:var(--risk-high);font-size:0.9375rem">${message}</p>
        </div>
    `;
}

// ============================================================
// Helpers
// ============================================================
function createResultCard(icon, title) {
    const card = document.createElement('div');
    card.className = 'result-card';
    card.innerHTML = `
        <div class="result-card-header">
            <div class="result-card-title">
                <span class="card-icon">${icon}</span>
                ${title}
            </div>
        </div>
        <div class="result-card-body"></div>
    `;
    return card;
}

function formatKey(key) {
    return key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function formatDecision(decision) {
    if (!decision) return 'Unknown';
    return decision.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function truncate(str, maxLen) {
    if (!str) return '';
    return str.length > maxLen ? str.substring(0, maxLen) + '…' : str;
}

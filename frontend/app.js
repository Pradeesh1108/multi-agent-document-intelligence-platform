/**
 * Workflow Simulator & Monitoring Dashboard — Frontend Application
 */

// ============================================================
// Configuration
// ============================================================
const API_BASE = window.location.origin;
const ENDPOINTS = {
    process: `${API_BASE}/documents/process`,
    upload: `${API_BASE}/documents/upload`
};

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
    const resultsContent = document.getElementById('resultsContent');
    const provider = document.getElementById('providerSelect').value;
    const apiKey = document.getElementById('apiKeyInput').value.trim();

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
        alert('Please provide a document or paste text content before submitting.');
        return;
    }

    if (apiKey && !provider) {
        alert('Please select an LLM Provider (Gemini or Groq) when providing a custom API Key.');
        return;
    }

    if (provider) {
        formData.append('llm_provider', provider);
    }
    if (apiKey) {
        formData.append('api_key', apiKey);
    }

    // Set Loading State
    btn.disabled = true;
    btn.textContent = 'Processing...';
    resultsSection.classList.remove('hidden');
    resultsContent.innerHTML = `<div class="empty-state">Processing document, please wait...</div>`;

    try {
        const response = await fetch(ENDPOINTS.process, {
            method: 'POST',
            body: formData,
        });

        const result = await response.json();

        if (response.ok) {
            renderResults(result);
        } else {
            renderError(result.detail || 'Processing failed.');
        }
    } catch (error) {
        console.error('Request failed:', error);
        renderError(`Connection failed: ${error.message}`);
    } finally {
        btn.disabled = false;
        btn.textContent = 'Process Document';
    }
}

// ============================================================
// Results Rendering
// ============================================================
function renderResults(data) {
    const container = document.getElementById('resultsContent');
    container.innerHTML = '';

    // 1. High Level Summary Grid
    container.appendChild(renderSummaryGrid(data));

    // If the workflow failed completely (e.g. invalid API key), just show the errors and stop.
    if (data.status === 'failed') {
        if (data.errors && data.errors.length > 0) {
            container.appendChild(createSectionHeader('Errors'));
            const errDiv = document.createElement('div');
            errDiv.style.color = 'var(--status-error)';
            errDiv.innerHTML = data.errors.map(e => `<p>${e}</p>`).join('');
            container.appendChild(errDiv);
        }
        return;
    }

    // 2. Document Summary / Intent
    if (data.intent) {
        container.appendChild(createSectionHeader('Document Summary'));
        container.appendChild(renderIntentData(data.intent));
    }

    // 3. Extracted Information
    if (data.extracted_entities && data.extracted_entities.entities) {
        container.appendChild(createSectionHeader('Extracted Information'));
        container.appendChild(renderExtractedEntities(data.extracted_entities.entities));
    }

    // 4. Risk Assessment
    if (data.risk_analysis) {
        container.appendChild(createSectionHeader('Risk Assessment'));
        container.appendChild(renderRiskData(data.risk_analysis));
    }

    // 5. Recommended Action (Decision + Actions taken)
    if (data.decision || (data.actions && data.actions.length > 0)) {
        container.appendChild(createSectionHeader('Workflow Actions'));
        container.appendChild(renderActionsData(data.decision, data.actions));
    }

    // 6. Errors (if any)
    if (data.errors && data.errors.length > 0) {
        container.appendChild(createSectionHeader('Errors'));
        const errDiv = document.createElement('div');
        errDiv.style.color = 'var(--status-error)';
        errDiv.innerHTML = data.errors.map(e => `<p>${e}</p>`).join('');
        container.appendChild(errDiv);
    }
}

// --- Render Components ---

function renderSummaryGrid(data) {
    const grid = document.createElement('div');
    grid.className = 'summary-grid';

    const items = [
        { label: 'Workflow ID', value: data.workflow_id || '—' },
        { label: 'Document Type', value: (data.file_type || '—').toUpperCase() },
        { label: 'Status', value: formatStatus(data.status) },
        { label: 'Processing Time', value: data.processing_time_ms ? `${data.processing_time_ms.toFixed(1)} ms` : '—' }
    ];

    grid.innerHTML = items.map(item => `
        <div class="summary-item">
            <span class="summary-label">${item.label}</span>
            <span class="summary-value">${item.value}</span>
        </div>
    `).join('');

    return grid;
}

function renderIntentData(intent) {
    const div = document.createElement('div');
    const intentVal = formatKey(intent.intent || 'Unknown');
    const conf = intent.confidence ? Math.round(intent.confidence * 100) : 0;
    
    div.innerHTML = `
        <p class="text-sm" style="margin-bottom: var(--spacing-sm)">
            <span style="font-weight: 500; margin-right: 8px;">Detected Intent:</span>
            <span class="badge info">${intentVal}</span>
            <span class="text-muted" style="margin-left: 8px;">(${conf}% confidence)</span>
        </p>
        <p class="text-sm text-muted">${intent.reasoning || ''}</p>
    `;
    return div;
}

function renderExtractedEntities(entities) {
    const table = document.createElement('table');
    table.className = 'data-table';
    
    let html = '<tbody>';
    for (const [key, value] of Object.entries(entities)) {
        if (value === null || value === undefined) continue;
        const displayValue = typeof value === 'object' ? JSON.stringify(value) : String(value);
        html += `
            <tr>
                <th>${formatKey(key)}</th>
                <td>${displayValue}</td>
            </tr>
        `;
    }
    html += '</tbody>';
    table.innerHTML = html;
    
    return table;
}

function renderRiskData(risk) {
    const div = document.createElement('div');
    const level = (risk.risk_level || 'low').toLowerCase();
    
    let badgeClass = 'success';
    if (level === 'medium') badgeClass = 'warning';
    if (level === 'high' || level === 'critical') badgeClass = 'error';

    let html = `
        <p class="text-sm" style="margin-bottom: var(--spacing-sm)">
            <span style="font-weight: 500; margin-right: 8px;">Risk Level:</span>
            <span class="badge ${badgeClass}">${level.toUpperCase()}</span>
        </p>
    `;

    if (risk.risk_factors && risk.risk_factors.length > 0) {
        html += `<ul style="margin-left: 20px; margin-bottom: var(--spacing-sm); font-size: 0.875rem; color: var(--text-secondary)">`;
        risk.risk_factors.forEach(f => {
            html += `<li>${f}</li>`;
        });
        html += `</ul>`;
    }

    if (risk.explanation) {
        html += `<p class="text-sm text-muted">${risk.explanation}</p>`;
    }

    div.innerHTML = html;
    return div;
}

function renderActionsData(decision, actions) {
    const div = document.createElement('div');
    
    let html = '';
    
    // Display primary decision
    if (decision) {
        const decVal = formatKey(decision.decision || 'None');
        html += `
            <p class="text-sm" style="margin-bottom: var(--spacing-md)">
                <span style="font-weight: 500; margin-right: 8px;">Recommended Action:</span>
                <span style="font-weight: 600; color: var(--text-primary)">${decVal}</span>
            </p>
            <p class="text-sm text-muted" style="margin-bottom: var(--spacing-md)">${decision.reasoning || ''}</p>
        `;
    }

    // Display executed actions in a simple list
    if (actions && actions.length > 0) {
        html += `<div style="background: #F8FAFC; border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: var(--spacing-md)">`;
        html += `<h4 style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-secondary); margin-bottom: var(--spacing-sm)">Execution Log</h4>`;
        
        actions.forEach(act => {
            const statusClass = act.status === 'success' ? 'success' : 'error';
            html += `
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 0.875rem">
                    <span>${formatKey(act.action_type || 'Unknown Action')}</span>
                    <span class="badge ${statusClass}">${act.status || 'unknown'}</span>
                </div>
            `;
        });
        html += `</div>`;
    }

    div.innerHTML = html;
    return div;
}

function renderError(message) {
    const container = document.getElementById('resultsContent');
    container.innerHTML = `
        <div style="color: var(--status-error); padding: var(--spacing-md); background: var(--status-error-bg); border-radius: var(--radius-sm);">
            <strong>Error:</strong> ${message}
        </div>
    `;
}

// --- Helpers ---

function createSectionHeader(title) {
    const h3 = document.createElement('h3');
    h3.className = 'result-section-header';
    h3.textContent = title;
    return h3;
}

function formatKey(key) {
    if (!key) return '';
    return key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function formatStatus(status) {
    if (!status) return '—';
    const s = status.toLowerCase();
    let badgeClass = 'info';
    if (s === 'completed' || s === 'success') badgeClass = 'success';
    if (s === 'failed' || s === 'error') badgeClass = 'error';
    if (s === 'processing' || s === 'running') badgeClass = 'warning';
    
    return `<span class="badge ${badgeClass}">${status.toUpperCase()}</span>`;
}

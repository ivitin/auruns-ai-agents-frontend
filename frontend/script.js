const API_URL = 'http://localhost:8000/api/v1';
let conversationId = null;
let currentUser = null;
let selectedArea = null;
let selectedAssets = [];
let isSending = false;
let statsCache = null;

// ── Persistência de conversa (por usuário) ───────────────────────
let _storedMsgs = [];
let _isRestoring = false;

function _skConv() { return `chat_conv_${currentUser?.user_id || 'anon'}`; }
function _skMsgs() { return `chat_msgs_${currentUser?.user_id || 'anon'}`; }

function _persistMsg(text, type, sources, interactionId) {
    if (_isRestoring) return;
    _storedMsgs.push({ text, type, sources: sources || null, interactionId: interactionId || null });
    try { localStorage.setItem(_skMsgs(), JSON.stringify(_storedMsgs)); } catch(e) {}
}

function _clearStorage() {
    localStorage.removeItem(_skConv());
    localStorage.removeItem(_skMsgs());
    _storedMsgs = [];
}

function restoreConversation() {
    const savedId   = localStorage.getItem(_skConv());
    const savedMsgs = localStorage.getItem(_skMsgs());
    if (!savedMsgs) return;

    let msgs;
    try { msgs = JSON.parse(savedMsgs); } catch(_) { _clearStorage(); return; }
    if (!Array.isArray(msgs) || msgs.length === 0) return;

    if (savedId) conversationId = savedId;
    _storedMsgs = msgs;

    const welcome = chatMessages.querySelector('.welcome-message');
    if (welcome) welcome.remove();

    _isRestoring = true;
    msgs.forEach(m => {
        try { addMessage(m.text, m.type, m.sources, m.interactionId); }
        catch(e) { console.error('[restore] addMessage falhou:', e, m); }
    });
    _isRestoring = false;
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
// ─────────────────────────────────────────────────────────────────

const chatMessages = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const clearBtn = document.getElementById('clearBtn');
const statusEl = document.getElementById('status');
const areaList = document.getElementById('areaList');
const statsEl = document.getElementById('stats');
const userInfo = document.getElementById('userInfo');
const logoutBtn = document.getElementById('logoutBtn');

const architectureModal = document.getElementById('architectureModal');
const showArchitectureBtn = document.getElementById('showArchitectureBtn');
const closeModal = document.getElementById('closeModal');
const areaFilter = document.getElementById('areaFilter');
const loadArchitecture = document.getElementById('loadArchitecture');

document.addEventListener('DOMContentLoaded', () => {
    checkAuthentication();
    checkHealth();
    loadAreas();
    loadStats();
    loadUserStats();
    setupEventListeners();
    setupAssetListModal();
    restoreConversation();
});

function checkAuthentication() {
    const userData = localStorage.getItem('currentUser');
    if (!userData) {
        window.location.href = 'login.html';
        return;
    }
    currentUser = JSON.parse(userData);
    document.getElementById('username').textContent = `👤 ${currentUser.username}`;
}

function setupEventListeners() {
    chatForm.addEventListener('submit', handleSendMessage);
    clearBtn.addEventListener('click', clearConversation);
    logoutBtn?.addEventListener('click', handleLogout);
    showArchitectureBtn.addEventListener('click', openArchitectureModal);
    closeModal.addEventListener('click', closeArchitectureModal);
    loadArchitecture.addEventListener('click', loadArchitectureData);
    
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });
    
    architectureModal.addEventListener('click', (e) => {
        if (e.target === architectureModal) closeArchitectureModal();
    });
}

function handleLogout() {
    if (confirm('Deseja sair?')) {
        localStorage.removeItem('currentUser');
        localStorage.removeItem('authToken');
        window.location.href = 'login.html';
    }
}

async function loadUserStats() {
    try {
        const response = await fetch(`${API_URL}/auth/user/${currentUser.user_id}`);
        const data = await response.json();

        const interactionsEl = document.getElementById('userInteractions');
        if (interactionsEl) interactionsEl.textContent = data.total_interactions;

        const userStatsEl = document.getElementById('userStats');
        if (userStatsEl && data.common_topics && data.common_topics.length > 0) {
            const topicsEl = document.createElement('div');
            topicsEl.className = 'stat-item';
            topicsEl.innerHTML = `
                <span class="stat-label">Tópicos:</span>
                <span class="stat-value" style="font-size: 0.75rem;">${data.common_topics.join(', ')}</span>
            `;
            userStatsEl.appendChild(topicsEl);
        }
    } catch (error) {
        console.error('Erro ao carregar stats do usuário:', error);
    }
}

async function checkHealth() {
    try {
        const response = await fetch(`${API_URL.replace('/api/v1', '')}/health`);
        const data = await response.json();
        if (data.status === 'healthy') {
            statusEl.classList.add('connected');
            statusEl.querySelector('span:last-child').textContent = 'Conectado';
        }
    } catch (error) {
        statusEl.querySelector('span:last-child').textContent = 'Desconectado';
    }
}

async function loadAreas() {
    try {
        const response = await fetch(`${API_URL}/chat/areas`);
        const data = await response.json();
        data.areas.forEach(area => {
            const btn = document.createElement('button');
            btn.className = 'area-btn';
            btn.dataset.area = area;
            btn.textContent = area;
            areaList.appendChild(btn);

            const option = document.createElement('option');
            option.value = area;
            option.textContent = area;
            areaFilter.appendChild(option);
        });
        areaList.querySelector('.area-btn').classList.add('active');

        areaList.addEventListener('click', (e) => {
            const btn = e.target.closest('.area-btn');
            if (!btn) return;
            areaList.querySelectorAll('.area-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            selectedArea = btn.dataset.area || null;
        });
    } catch (error) {
        console.error('Erro ao carregar áreas:', error);
    }
}

async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/chat/stats`);
        const data = await response.json();
        statsCache = data;
        document.getElementById('totalEquipments').textContent = data.total_equipments;

        // Dropdown de tipo → distribui por área
        const tipoSelect = document.getElementById('tipoSelect');
        if (tipoSelect) {
            tipoSelect.addEventListener('change', () => updateTipoByArea(tipoSelect.value));
        }

        Object.entries(data.by_area).forEach(([area, count]) => {
            const statItem = document.createElement('div');
            statItem.className = 'stat-item';
            statItem.innerHTML = `
                <span class="stat-label">${area}:</span>
                <span class="stat-value">${count}</span>
            `;
            statsEl.appendChild(statItem);
        });

        // Preenche selects de filtro de ativos com as mesmas áreas
        const assetAreaSelect = document.getElementById('assetListArea');
        if (assetAreaSelect && data.by_area) {
            Object.keys(data.by_area).forEach(area => {
                const opt = document.createElement('option');
                opt.value = area;
                opt.textContent = area;
                assetAreaSelect.appendChild(opt);
            });
        }

        // Inicializa dropdown de tipo com robôs como default
        updateTipoByArea('robo');
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
    }
}

function updateTipoByArea(tipo) {
    const container = document.getElementById('tipoByAreaStats');
    if (!container) return;
    if (!tipo || !statsCache?.by_type_and_area?.[tipo]) {
        container.innerHTML = '<div class="stat-item"><span class="stat-label" style="font-size:0.75rem">Selecione um tipo acima</span></div>';
        return;
    }
    const byArea = statsCache.by_type_and_area[tipo];
    const total = Object.values(byArea).reduce((s, v) => s + v, 0);
    container.innerHTML = `
        <div class="stat-item" style="font-weight:600;">
            <span class="stat-label">Total:</span>
            <span class="stat-value">${total}</span>
        </div>
        ${Object.entries(byArea).sort((a, b) => b[1] - a[1]).map(([area, count]) => `
            <div class="stat-item">
                <span class="stat-label">${area}:</span>
                <span class="stat-value">${count}</span>
            </div>
        `).join('')}
    `;

    // Sincroniza o select do dropdown
    const tipoSelect = document.getElementById('tipoSelect');
    if (tipoSelect && tipoSelect.value !== tipo) tipoSelect.value = tipo;
}

function setupAssetListModal() {
    const listBtn = document.getElementById('listAssetsBtn');
    const modal = document.getElementById('assetListModal');
    const closeBtn = document.getElementById('closeAssetListModal');

    if (!listBtn || !modal) return;

    listBtn.addEventListener('click', async () => {
        const area = document.getElementById('assetListArea').value;
        const tipo = document.getElementById('assetListType').value;
        modal.classList.add('active');
        await loadAssetList(area, tipo);
    });

    closeBtn.addEventListener('click', () => modal.classList.remove('active'));
    modal.addEventListener('click', (e) => { if (e.target === modal) modal.classList.remove('active'); });
}

async function loadAssetList(area, tipo) {
    const body = document.getElementById('assetListBody');
    const title = document.getElementById('assetListTitle');
    body.innerHTML = '<div class="loading-spinner">Carregando...</div>';

    const params = new URLSearchParams();
    if (area) params.append('area', area);
    if (tipo) params.append('tipo', tipo);

    const labelArea = area || 'Todas as áreas';
    const labelTipo = tipo ? `— ${tipo}` : '';
    title.textContent = `📋 Ativos: ${labelArea} ${labelTipo}`;

    try {
        const response = await fetch(`${API_URL}/chat/equipment-list?${params}`);
        const data = await response.json();

        if (!data.equipments || data.equipments.length === 0) {
            body.innerHTML = '<p style="padding:16px">Nenhum ativo encontrado para os filtros selecionados.</p>';
            return;
        }

        const typeIcons = {robo:'🤖', prensa:'🔨', elevador:'⬆️', bomba:'💧', chiller:'❄️', ponte_rolante:'🏗️', mesa:'🪑', outro:'📦'};

        body.innerHTML = `
            <p style="padding:8px 16px;color:var(--text-secondary);font-size:0.85rem;">Total: <strong>${data.total}</strong> ativos</p>
            <table style="width:100%;border-collapse:collapse;font-size:0.82rem;">
                <thead>
                    <tr style="background:var(--bg-secondary);text-align:left;">
                        <th style="padding:8px 12px;">Tipo</th>
                        <th style="padding:8px 12px;">Código</th>
                        <th style="padding:8px 12px;">Descrição</th>
                        <th style="padding:8px 12px;">Área</th>
                        <th style="padding:8px 12px;">UTE / Linha</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.equipments.map((eq, i) => `
                        <tr style="border-bottom:1px solid var(--border-color);background:${i % 2 === 0 ? 'transparent' : 'var(--bg-secondary)'};">
                            <td style="padding:7px 12px;">${typeIcons[eq.tipo] || '📦'} ${eq.tipo}</td>
                            <td style="padding:7px 12px;font-family:monospace;">${eq.codigo || '—'}</td>
                            <td style="padding:7px 12px;">${eq.descricao || eq.maquina || '—'}</td>
                            <td style="padding:7px 12px;">${eq.area || '—'}</td>
                            <td style="padding:7px 12px;">${[eq.ute, eq.linha].filter(Boolean).join(' / ') || '—'}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        body.innerHTML = '<p style="padding:16px;color:red;">Erro ao carregar ativos.</p>';
        console.error('Erro ao carregar lista de ativos:', error);
    }
}

async function handleSendMessage(e) {
    e.preventDefault();
    if (isSending) return;
    const message = messageInput.value.trim();
    if (!message) return;

    isSending = true;
    addMessage(message, 'user');
    messageInput.value = '';
    sendBtn.disabled = true;
    sendBtn.querySelector('span:first-child').style.display = 'none';
    sendBtn.querySelector('.loading').style.display = 'inline';

    try {
        const response = await fetch(`${API_URL}/chat/message`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                message: message,
                conversation_id: conversationId,
                context: {
                    user_id: currentUser.user_id,
                    area: selectedArea,
                    selected_assets: selectedAssets
                }
            })
        });
        const data = await response.json();
        if (!response.ok) {
            const errMsg = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
            console.error('Erro do backend:', errMsg);
            addMessage(`❌ Erro do servidor: ${errMsg}`, 'ai');
        } else {
            conversationId = data.conversation_id;
            try { localStorage.setItem(_skConv(), conversationId); } catch(_) {}
            addMessage(data.response, 'ai', data.sources, data.metadata?.interaction_id);
            loadUserStats();
        }
    } catch (error) {
        console.error('Erro ao enviar mensagem:', error);
        addMessage(`Desculpe, ocorreu um erro: ${error.message}`, 'ai');
    } finally {
        isSending = false;
        sendBtn.disabled = false;
        sendBtn.querySelector('span:first-child').style.display = 'inline';
        sendBtn.querySelector('.loading').style.display = 'none';
    }
}

function renderSelectedAssets() {
    const container = document.getElementById('selectedAssetsChips');
    if (!container) return;
    if (selectedAssets.length === 0) {
        container.style.display = 'none';
        container.innerHTML = '';
        return;
    }
    container.style.display = 'flex';
    container.innerHTML = selectedAssets.map((a, i) => `
        <span style="display:inline-flex;align-items:center;gap:4px;background:var(--primary-color,#2563eb);color:#fff;border-radius:12px;padding:2px 10px;font-size:0.75rem;">
            📦 ${a.codigo || a.descricao || 'Ativo'}
            <button onclick="removeSelectedAsset(${i})" style="background:none;border:none;color:#fff;cursor:pointer;font-size:0.9rem;padding:0;line-height:1;">&times;</button>
        </span>
    `).join('');
}

function removeSelectedAsset(index) {
    selectedAssets.splice(index, 1);
    renderSelectedAssets();
}

function parseMarkdown(text) {
    text = text.replace(/^##### (.*$)/gim, '<h5>$1</h5>');
    text = text.replace(/^#### (.*$)/gim, '<h4>$1</h4>');
    text = text.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    text = text.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    text = text.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    text = text.replace(/`(.*?)`/g, '<code>$1</code>');
    text = text.replace(/\[([^\]]+)\]\(([^\)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
    text = text.replace(/^---$/gim, '<hr>');
    
    const lines = text.split('\n');
    let inList = false;
    let result = [];
    for (let line of lines) {
        if (line.match(/^[\-\•]\s+/)) {
            if (!inList) {
                result.push('<ul>');
                inList = true;
            }
            result.push('<li>' + line.replace(/^[\-\•]\s+/, '') + '</li>');
        } else {
            if (inList) {
                result.push('</ul>');
                inList = false;
            }
            result.push(line);
        }
    }
    if (inList) result.push('</ul>');
    
    text = result.join('\n');
    text = text.replace(/\n\n/g, '</p><p>');
    text = text.replace(/\n/g, '<br>');
    if (!text.startsWith('<')) text = '<p>' + text + '</p>';
    return text;
}

function addMessage(text, type, sources = null, interactionId = null) {
    const welcomeMsg = chatMessages.querySelector('.welcome-message');
    if (welcomeMsg) welcomeMsg.remove();
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    const avatar = type === 'user' ? '👤' : '��';
    const processedText = type === 'ai' ? parseMarkdown(text) : text;
    
    let sourcesHtml = '';
    if (sources && sources.length > 0) {
        sourcesHtml = `<div class="message-sources"><strong>📚 Fontes:</strong> ${sources.length} equipamento(s)</div>`;
    }
    
    let feedbackHtml = '';
    if (type === 'ai' && interactionId) {
        feedbackHtml = `
            <div class="message-feedback">
                <span>Útil?</span>
                <button class="feedback-btn" data-id="${interactionId}" data-type="positive">👍</button>
                <button class="feedback-btn" data-id="${interactionId}" data-type="negative">👎</button>
            </div>`;
    }
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <div class="message-text">${processedText}</div>
            ${sourcesHtml}${feedbackHtml}
        </div>`;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    if (interactionId) {
        messageDiv.querySelectorAll('.feedback-btn').forEach(btn => {
            btn.addEventListener('click', () => handleFeedback(btn.dataset.id, btn.dataset.type, btn));
        });
    }

    if (type === 'user' || type === 'ai') {
        _persistMsg(text, type, sources, interactionId);
    }
}

async function handleFeedback(interactionId, feedbackType, button) {
    try {
        const response = await fetch(`${API_URL}/auth/feedback`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({interaction_id: interactionId, feedback: feedbackType})
        });
        if (response.ok) {
            const feedbackDiv = button.parentElement;
            feedbackDiv.querySelectorAll('.feedback-btn').forEach(btn => {
                btn.disabled = true;
                btn.style.opacity = '0.5';
            });
            button.style.opacity = '1';
            button.style.transform = 'scale(1.2)';
            const thanks = document.createElement('span');
            thanks.textContent = ' Obrigado!';
            thanks.style.color = 'var(--success-color)';
            thanks.style.fontSize = '0.875rem';
            feedbackDiv.appendChild(thanks);
        }
    } catch (error) {
        console.error('Erro ao enviar feedback:', error);
    }
}

function clearConversation() {
    if (confirm('Deseja limpar a conversa?')) {
        conversationId = null;
        _clearStorage();
        chatMessages.innerHTML = `
            <div class="welcome-message">
                <h2>👋 Bem-vindo de volta, ${currentUser.username}!</h2>
                <p>Faça perguntas sobre equipamentos industriais.</p>
            </div>`;
    }
}

function openArchitectureModal() {
    architectureModal.classList.add('active');
    loadArchitectureData();
}

function closeArchitectureModal() {
    architectureModal.classList.remove('active');
}

function switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    document.getElementById(`${tabName}Tab`).classList.add('active');
}

async function loadArchitectureData() {
    const area = areaFilter.value;
    try {
        await Promise.all([loadTreeView(area), loadSummaryView(area), loadJsonView(area)]);
    } catch (error) {
        console.error('Erro ao carregar arquitetura:', error);
    }
}

async function loadTreeView(area) {
    const treeContainer = document.getElementById('architectureTree');
    treeContainer.innerHTML = '<div class="loading-spinner">Carregando...</div>';
    try {
        const response = await fetch(`${API_URL}/chat/generate-architecture`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({format: 'markdown', area: area || null})
        });
        const data = await response.json();
        treeContainer.innerHTML = parseMarkdown(data.architecture);
    } catch (error) {
        treeContainer.innerHTML = '<p>Erro ao carregar arquitetura.</p>';
    }
}

async function loadSummaryView(area) {
    const summaryContainer = document.getElementById('architectureSummary');
    summaryContainer.innerHTML = '<div class="loading-spinner">Carregando...</div>';
    try {
        const response = await fetch(`${API_URL}/chat/generate-architecture`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({format: 'summary', area: area || null})
        });
        const data = await response.json();
        summaryContainer.innerHTML = parseMarkdown(data.architecture);
    } catch (error) {
        summaryContainer.innerHTML = '<p>Erro ao carregar resumo.</p>';
    }
}

async function loadJsonView(area) {
    const jsonContainer = document.getElementById('architectureJson');
    jsonContainer.innerHTML = '<code>Carregando...</code>';
    try {
        const response = await fetch(`${API_URL}/chat/generate-architecture`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({format: 'json', area: area || null})
        });
        const data = await response.json();
        jsonContainer.innerHTML = '<code>' + JSON.stringify(data.architecture, null, 2) + '</code>';
    } catch (error) {
        jsonContainer.innerHTML = '<code>Erro ao carregar JSON.</code>';
    }
}


// Adicione esta função no seu script.js ou em um novo arquivo
function setupBotAvatar() {
    // Seleciona todos os avatares de bot (mensagens AI)
    document.querySelectorAll('.message.ai .message-avatar').forEach(avatar => {
        // Verifica se o avatar está vazio ou tem caracteres inválidos
        if (!avatar.textContent.trim() || avatar.textContent.includes('�')) {
            // Substitui por um emoji de robô ou outro texto
            avatar.textContent = '🤖';
            
            // Alternativa: usar uma imagem
            /*
            avatar.innerHTML = '';
            const img = document.createElement('img');
            img.src = 'caminho/para/sua/imagem-bot.png';
            img.alt = 'AI Bot';
            img.style.width = '100%';
            img.style.height = '100%';
            img.style.borderRadius = '50%';
            avatar.appendChild(img);
            */
        }
    });
    
    // Observador para monitorar novas mensagens
    const observer = new MutationObserver(mutations => {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === 1 && node.classList.contains('message') && node.classList.contains('ai')) {
                    const avatar = node.querySelector('.message-avatar');
                    if (avatar && (!avatar.textContent.trim() || avatar.textContent.includes('�'))) {
                        avatar.textContent = '🤖';
                    }
                }
            });
        });
    });
    
    // Inicia a observação do contêiner de mensagens
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        observer.observe(chatMessages, { childList: true });
    }
}

// Chame esta função quando o documento estiver carregado
document.addEventListener('DOMContentLoaded', setupBotAvatar);
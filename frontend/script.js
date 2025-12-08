const API_URL = 'http://localhost:8000/api/v1';
let conversationId = null;
let currentUser = null;

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
    logoutBtn.addEventListener('click', handleLogout);
    showArchitectureBtn.addEventListener('click', openArchitectureModal);
    closeModal.addEventListener('click', closeArchitectureModal);
    loadArchitecture.addEventListener('click', loadArchitectureData);
    
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });
    
    architectureModal.addEventListener('click', (e) => {
        if (e.target === architectureModal) closeArchitectureModal();
    });
    
    document.querySelectorAll('.example-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            messageInput.value = btn.dataset.query;
            handleSendMessage(new Event('submit'));
        });
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
        document.getElementById('userInteractions').textContent = data.total_interactions;
        
        if (data.common_topics && data.common_topics.length > 0) {
            const topicsEl = document.createElement('div');
            topicsEl.className = 'stat-item';
            topicsEl.innerHTML = `
                <span class="stat-label">Tópicos:</span>
                <span class="stat-value" style="font-size: 0.75rem;">${data.common_topics.join(', ')}</span>
            `;
            document.getElementById('userStats').appendChild(topicsEl);
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
    } catch (error) {
        console.error('Erro ao carregar áreas:', error);
    }
}

async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/chat/stats`);
        const data = await response.json();
        document.getElementById('totalEquipments').textContent = data.total_equipments;
        Object.entries(data.by_area).forEach(([area, count]) => {
            const statItem = document.createElement('div');
            statItem.className = 'stat-item';
            statItem.innerHTML = `
                <span class="stat-label">${area}:</span>
                <span class="stat-value">${count}</span>
            `;
            statsEl.appendChild(statItem);
        });
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
    }
}

async function handleSendMessage(e) {
    e.preventDefault();
    const message = messageInput.value.trim();
    if (!message) return;
    
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
                context: {user_id: currentUser.user_id}
            })
        });
        const data = await response.json();
        conversationId = data.conversation_id;
        addMessage(data.response, 'ai', data.sources, data.metadata.interaction_id);
        loadUserStats();
    } catch (error) {
        addMessage('Desculpe, ocorreu um erro ao processar sua mensagem.', 'ai');
    } finally {
        sendBtn.disabled = false;
        sendBtn.querySelector('span:first-child').style.display = 'inline';
        sendBtn.querySelector('.loading').style.display = 'none';
    }
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
        chatMessages.innerHTML = `
            <div class="welcome-message">
                <h2>�� Bem-vindo de volta, ${currentUser.username}!</h2>
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
// Arquivo: buttons-fix.js

document.addEventListener('DOMContentLoaded', () => {
    console.log('🔄 Corrigindo botões...');
    
    // 1. Consertar botão de arquitetura
    const archBtn = document.getElementById('showArchitectureBtn');
    if (archBtn) {
        console.log('🔍 Encontrado botão de arquitetura');
        archBtn.onclick = function() {
            console.log('🏗️ Abrindo modal de arquitetura');
            const modal = document.getElementById('architectureModal');
            if (modal) modal.classList.add('active');
            loadArchitectureData();
        };
    }
    
    // 2. Consertar botões de exemplo
    document.querySelectorAll('.example-btn').forEach(btn => {
        console.log(`🔍 Encontrado botão de exemplo: ${btn.textContent.trim()}`);
        btn.onclick = function() {
            console.log(`📝 Usando exemplo: ${btn.dataset.query}`);
            const messageInput = document.getElementById('messageInput');
            if (messageInput) {
                messageInput.value = btn.dataset.query;
                
                // Simular envio do formulário
                const chatForm = document.getElementById('chatForm');
                if (chatForm) {
                    console.log('📤 Enviando exemplo...');
                    
                    // Tenta usar a função existente
                    if (typeof handleSendMessage === 'function') {
                        const event = new Event('submit');
                        handleSendMessage(event);
                    } 
                    // Alternativa: dispara submit no formulário
                    else {
                        const submitEvent = new SubmitEvent('submit', {
                            bubbles: true,
                            cancelable: true
                        });
                        chatForm.dispatchEvent(submitEvent);
                    }
                }
            }
        };
    });
    
    // 3. Consertar tabs do modal
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.onclick = function() {
            const tab = btn.dataset.tab;
            console.log(`🔄 Mudando para tab: ${tab}`);
            
            // Ativa o botão
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Ativa o conteúdo
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            const tabContent = document.getElementById(`${tab}Tab`);
            if (tabContent) tabContent.classList.add('active');
        };
    });
    
    // 4. Corrigir botão de carregar arquitetura
    const loadBtn = document.getElementById('loadArchitecture');
    if (loadBtn) {
        loadBtn.onclick = function() {
            console.log('🔄 Carregando arquitetura...');
            loadArchitectureData();
        };
    }
    
    // 5. Corrigir botão de fechar modal
    const closeBtn = document.getElementById('closeModal');
    if (closeBtn) {
        closeBtn.onclick = function() {
            console.log('❌ Fechando modal...');
            const modal = document.getElementById('architectureModal');
            if (modal) modal.classList.remove('active');
        };
    }
    
    console.log('✅ Todos os botões corrigidos!');
});

// Definir função loadArchitectureData se não existir
if (typeof loadArchitectureData !== 'function') {
    window.loadArchitectureData = async function() {
        console.log('🔄 Carregando dados de arquitetura...');
        try {
            const area = document.getElementById('areaFilter')?.value || '';
            
            // Carregar as diferentes visualizações
            await Promise.all([
                loadTreeView(area),
                loadSummaryView(area),
                loadJsonView(area)
            ]);
        } catch (error) {
            console.error('❌ Erro ao carregar arquitetura:', error);
        }
    };
}

// Funções de carregamento caso não existam
if (typeof loadTreeView !== 'function') {
    window.loadTreeView = async function(area) {
        const treeContainer = document.getElementById('architectureTree');
        if (!treeContainer) return;
        
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
            console.error('❌ Erro ao carregar visualização em árvore:', error);
        }
    };
}

if (typeof loadSummaryView !== 'function') {
    window.loadSummaryView = async function(area) {
        const summaryContainer = document.getElementById('architectureSummary');
        if (!summaryContainer) return;
        
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
            console.error('❌ Erro ao carregar resumo:', error);
        }
    };
}

if (typeof loadJsonView !== 'function') {
    window.loadJsonView = async function(area) {
        const jsonContainer = document.getElementById('architectureJson');
        if (!jsonContainer) return;
        
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
            console.error('❌ Erro ao carregar JSON:', error);
        }
    };
}

// Função parseMarkdown se não existir
if (typeof parseMarkdown !== 'function') {
    window.parseMarkdown = function(text) {
        if (!text) return '';
        
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
        
        // Listas
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
    };
}
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
    
    // 6. Botão "Ver Lista" de ativos
    const listAssetsBtn = document.getElementById('listAssetsBtn');
    const assetListModal = document.getElementById('assetListModal');
    const closeAssetListModal = document.getElementById('closeAssetListModal');

    function fecharAssetModal() {
        if (!assetListModal) return;
        assetListModal.classList.remove('active');
        assetListModal.style.display = 'none';
    }

    if (listAssetsBtn && assetListModal) {
        listAssetsBtn.onclick = async function () {
            const area = document.getElementById('assetListArea')?.value || '';
            const tipo = document.getElementById('assetListType')?.value || '';

            // Força exibição do modal independente de CSS
            assetListModal.classList.add('active');
            assetListModal.style.cssText = 'display:flex!important;align-items:center;justify-content:center;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.7);z-index:9999;';

            const bodyEl = document.getElementById('assetListBody');
            const titleEl = document.getElementById('assetListTitle');
            if (titleEl) titleEl.textContent = `📋 Ativos: ${area || 'Todas'} ${tipo ? '— ' + tipo : ''}`;
            if (bodyEl) bodyEl.innerHTML = '<div style="padding:20px;text-align:center;">⏳ Carregando...</div>';

            try {
                const base = (typeof API_URL !== 'undefined') ? API_URL : 'http://localhost:8000/api/v1';
                const params = new URLSearchParams();
                if (area) params.append('area', area);
                if (tipo) params.append('tipo', tipo);

                const resp = await fetch(`${base}/chat/equipment-list?${params}`);
                if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
                const data = await resp.json();

                if (!bodyEl) return;
                if (!data.equipments || data.equipments.length === 0) {
                    bodyEl.innerHTML = '<p style="padding:16px">Nenhum ativo encontrado.</p>';
                    return;
                }

                const icons = {robo:'🤖',prensa:'🔨',elevador:'⬆️',bomba:'💧',chiller:'❄️',ponte_rolante:'🏗️',mesa:'🪑',outro:'📦'};
                // Rastreia seleção local no modal
                const modalSelected = new Map(); // codigo → asset obj

                function renderModalFooter() {
                    let footer = document.getElementById('assetModalFooter');
                    if (!footer) {
                        footer = document.createElement('div');
                        footer.id = 'assetModalFooter';
                        footer.style.cssText = 'position:sticky;bottom:0;padding:10px 16px;background:#fff;border-top:1px solid #e2e8f0;display:flex;align-items:center;justify-content:space-between;';
                        bodyEl.parentElement.appendChild(footer);
                    }
                    const count = modalSelected.size;
                    footer.innerHTML = count === 0
                        ? '<span style="font-size:.8rem;color:#64748b">Clique em uma linha para selecioná-la como contexto</span>'
                        : `<span style="font-size:.85rem"><strong>${count}</strong> ativo(s) selecionado(s)</span>
                           <button id="addAssetsCtxBtn" style="background:#2563eb;color:#fff;border:none;border-radius:6px;padding:6px 14px;cursor:pointer;font-size:.85rem;">
                               ✅ Usar como contexto
                           </button>`;
                    const btn = document.getElementById('addAssetsCtxBtn');
                    if (btn) btn.onclick = () => {
                        if (typeof selectedAssets !== 'undefined') {
                            modalSelected.forEach(asset => {
                                if (!selectedAssets.find(a => a.codigo === asset.codigo)) {
                                    selectedAssets.push(asset);
                                }
                            });
                            if (typeof renderSelectedAssets === 'function') renderSelectedAssets();
                        }
                        fecharAssetModal();
                    };
                }

                function toggleRow(tr, eq) {
                    const key = eq.codigo || eq.descricao;
                    if (modalSelected.has(key)) {
                        modalSelected.delete(key);
                        tr.style.background = tr.dataset.origBg || '';
                        tr.style.outline = '';
                    } else {
                        modalSelected.set(key, eq);
                        tr.style.background = '#dbeafe';
                        tr.style.outline = '2px solid #2563eb';
                    }
                    renderModalFooter();
                }

                bodyEl.innerHTML = `
                    <p style="padding:8px 16px;font-size:.85rem;">Total: <strong>${data.total}</strong> ativos</p>
                    <div style="overflow-x:auto;">
                    <table style="width:100%;border-collapse:collapse;font-size:.82rem;">
                        <thead><tr style="background:#f1f5f9;text-align:left;">
                            <th style="padding:8px 12px;">Tipo</th>
                            <th style="padding:8px 12px;">Código</th>
                            <th style="padding:8px 12px;">Descrição</th>
                            <th style="padding:8px 12px;">Área</th>
                            <th style="padding:8px 12px;">UTE / Linha</th>
                        </tr></thead>
                        <tbody>${data.equipments.map((eq, i) => `
                            <tr data-idx="${i}" data-orig="${i%2===0?'transparent':'#f8fafc'}"
                                style="border-bottom:1px solid #e2e8f0;background:${i%2===0?'transparent':'#f8fafc'};cursor:pointer;"
                                title="Clique para selecionar como contexto">
                                <td style="padding:7px 12px;">${icons[eq.tipo]||'📦'} ${eq.tipo}</td>
                                <td style="padding:7px 12px;font-family:monospace;">${eq.codigo||'—'}</td>
                                <td style="padding:7px 12px;">${eq.descricao||eq.maquina||'—'}</td>
                                <td style="padding:7px 12px;">${eq.area||'—'}</td>
                                <td style="padding:7px 12px;">${[eq.ute,eq.linha].filter(Boolean).join(' / ')||'—'}</td>
                            </tr>`).join('')}
                        </tbody>
                    </table></div>`;

                // Bind click em cada linha
                bodyEl.querySelectorAll('tbody tr').forEach((tr, i) => {
                    tr.dataset.origBg = data.equipments[i] && i%2===0 ? 'transparent' : '#f8fafc';
                    tr.onclick = () => toggleRow(tr, data.equipments[i]);
                });
                renderModalFooter();
            } catch (err) {
                if (bodyEl) bodyEl.innerHTML = `<p style="padding:16px;color:red;">❌ Erro: ${err.message}</p>`;
                console.error('Erro lista de ativos:', err);
            }
        };

        if (closeAssetListModal) closeAssetListModal.onclick = fecharAssetModal;
        assetListModal.addEventListener('click', (e) => { if (e.target === assetListModal) fecharAssetModal(); });
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
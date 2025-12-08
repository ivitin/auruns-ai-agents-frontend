// Arquivo: scroll-fix.js

// Função para adicionar rolagem em mensagens grandes
function setupMessageScrolling() {
    // Processa mensagens existentes
    document.querySelectorAll('.message-content').forEach(enableScrollIfNeeded);
    
    // Observa novas mensagens adicionadas ao chat
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.addedNodes.length) {
                    mutation.addedNodes.forEach((node) => {
                        if (node.classList && node.classList.contains('message')) {
                            const content = node.querySelector('.message-content');
                            if (content) enableScrollIfNeeded(content);
                        }
                    });
                }
            });
        });
        
        observer.observe(chatMessages, { childList: true });
    }
    
    console.log('✅ Sistema de rolagem para mensagens grandes ativado');
}

// Verifica se o elemento precisa de rolagem e habilita
function enableScrollIfNeeded(element) {
    // Redefine classes
    element.classList.remove('scrollable', 'has-more-content');
    
    // Verifica se o conteúdo é maior que o contêiner
    if (element.scrollHeight > element.clientHeight + 20) { // +20px para margem
        element.classList.add('scrollable');
        
        // Adiciona evento para verificar posição de rolagem
        element.addEventListener('scroll', checkScrollPosition);
        
        // Verifica inicialmente
        if (element.scrollHeight > element.clientHeight && element.scrollTop === 0) {
            element.classList.add('has-more-content');
        }
    }
}

// Verifica posição de rolagem para mostrar/ocultar indicador
function checkScrollPosition(event) {
    const element = event.target;
    
    // Se estiver no topo e tiver conteúdo para rolar
    if (element.scrollTop === 0 && element.scrollHeight > element.clientHeight) {
        element.classList.add('has-more-content');
    } else {
        element.classList.remove('has-more-content');
    }
}

// Inicia quando o documento estiver pronto
document.addEventListener('DOMContentLoaded', setupMessageScrolling);

// Também executa imediatamente caso o DOM já esteja carregado
if (document.readyState === 'interactive' || document.readyState === 'complete') {
    setupMessageScrolling();
}
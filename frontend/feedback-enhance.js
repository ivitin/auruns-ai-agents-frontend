// Melhoria para sistema de feedback com comentários
document.addEventListener('DOMContentLoaded', function() {
    // Sobrescrever o comportamento dos botões de feedback
    document.addEventListener('click', function(event) {
        // Verifica se clicou em um botão de feedback
        if (event.target.classList.contains('feedback-btn')) {
            event.preventDefault();
            
            const button = event.target;
            const interactionId = button.dataset.id;
            const feedbackType = button.dataset.type;
            const feedbackDiv = button.parentElement;
            
            // Verifica se já foi selecionado
            if (button.disabled) return;
            
            // Destaca o botão selecionado
            feedbackDiv.querySelectorAll('.feedback-btn').forEach(btn => {
                btn.classList.remove('selected');
            });
            button.classList.add('selected');
            
            // Remove formulário anterior se existir
            const existingForm = document.getElementById('feedback-comment-form');
            if (existingForm) existingForm.remove();
            
            // Cria formulário para comentário
            const commentForm = document.createElement('div');
            commentForm.id = 'feedback-comment-form';
            commentForm.innerHTML = `
                <textarea id="feedback-comment" 
                    placeholder="Comentário opcional (pressione Enter para enviar)" 
                    rows="2" 
                    style="width: 100%; margin-top: 0.5rem; padding: 0.5rem; border: 1px solid var(--border-color); border-radius: 8px; font-size: 0.875rem;"></textarea>
                <div style="display: flex; justify-content: flex-end; margin-top: 0.5rem;">
                    <button id="cancel-feedback" 
                        style="background: none; border: none; color: var(--text-light); margin-right: 0.5rem; cursor: pointer; font-size: 0.875rem;">
                        Cancelar
                    </button>
                    <button id="submit-feedback" 
                        style="background: var(--primary-color); color: white; border: none; padding: 0.25rem 0.75rem; border-radius: 4px; cursor: pointer; font-size: 0.875rem;">
                        Enviar
                    </button>
                </div>
            `;
            
            // Adiciona após os botões
            feedbackDiv.appendChild(commentForm);
            
            // Foco no textarea
            document.getElementById('feedback-comment').focus();
            
            // Evento para cancelar
            document.getElementById('cancel-feedback').addEventListener('click', function() {
                commentForm.remove();
                button.classList.remove('selected');
            });
            
            // Evento para enviar feedback com comentário
            function submitFeedback() {
                const commentText = document.getElementById('feedback-comment').value.trim();
                sendFeedbackToServer(interactionId, feedbackType, commentText, feedbackDiv, button);
                commentForm.remove();
            }
            
            // Evento para o botão de enviar
            document.getElementById('submit-feedback').addEventListener('click', submitFeedback);
            
            // Evento para enviar com Enter (mas permitir shift+enter para nova linha)
            document.getElementById('feedback-comment').addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    submitFeedback();
                }
            });
        }
    });
    
    // Função para enviar feedback para o servidor
    async function sendFeedbackToServer(interactionId, feedbackType, comment, feedbackDiv, selectedButton) {
        try {
            const response = await fetch(`${API_URL}/auth/feedback`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    interaction_id: interactionId, 
                    feedback: feedbackType,
                    comment: comment || null
                })
            });
            
            if (response.ok) {
                // Desabilita os botões
                feedbackDiv.querySelectorAll('.feedback-btn').forEach(btn => {
                    btn.disabled = true;
                    btn.style.opacity = '0.5';
                });
                
                // Destaca o botão selecionado
                selectedButton.style.opacity = '1';
                selectedButton.style.transform = 'scale(1.2)';
                
                // Mensagem de agradecimento
                const thanks = document.createElement('span');
                thanks.classList.add('feedback-thanks');
                if (comment) {
                    thanks.innerHTML = ` Obrigado pelo feedback!<br><small style="font-style: italic; opacity: 0.8;">"${comment}"</small>`;
                } else {
                    thanks.textContent = ' Obrigado pelo feedback!';
                }
                thanks.style.color = 'var(--success-color)';
                thanks.style.fontSize = '0.875rem';
                feedbackDiv.appendChild(thanks);
            }
        } catch (error) {
            console.error('Erro ao enviar feedback:', error);
            alert('Erro ao enviar feedback. Por favor, tente novamente.');
        }
    }
    
    // Adiciona estilos CSS
    const style = document.createElement('style');
    style.textContent = `
        .feedback-btn.selected {
            transform: scale(1.2);
            border-color: var(--primary-color);
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.2);
        }
        #feedback-comment-form {
            width: 100%;
            margin-top: 0.5rem;
            animation: fadeIn 0.3s;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    `;
    document.head.appendChild(style);
    
    console.log('✅ Sistema de feedback com comentários ativado!');
});
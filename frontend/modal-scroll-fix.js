// Força a habilitação da rolagem para os conteúdos do modal
   document.addEventListener('DOMContentLoaded', function() {
       // Funções auxiliares para melhorar a rolagem
       function enhanceScrolling() {
           // Adiciona overflow:auto a todos os containers relevantes
           document.querySelectorAll('.tab-content, .architecture-tree, .architecture-summary, .json-viewer').forEach(element => {
               element.style.overflowY = 'auto';
               element.style.maxHeight = '60vh';
           });

           console.log('✅ Rolagem do modal aprimorada');
       }

       // Observa quando o modal é aberto
       const observer = new MutationObserver(mutations => {
           mutations.forEach(mutation => {
               if (mutation.target.classList.contains('active') && 
                   mutation.target.id === 'architectureModal') {
                   console.log('🔍 Modal aberto detectado');
                   setTimeout(enhanceScrolling, 500);
               }
           });
       });

       // Observa o modal de arquitetura
       const modal = document.getElementById('architectureModal');
       if (modal) {
           observer.observe(modal, { attributes: true });
           console.log('✅ Observador de modal instalado');
       }

       // Melhora também o comportamento das tabs
       document.querySelectorAll('.tab-btn').forEach(btn => {
           btn.addEventListener('click', function() {
               const tabName = this.dataset.tab;
               console.log(`🔄 Tab alterada para: ${tabName}`);
               setTimeout(enhanceScrolling, 100);
           });
       });
   });
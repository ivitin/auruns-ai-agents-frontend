// Script de Debug para identificar problemas com os gráficos
// Cole este código no Console do navegador (F12) para diagnosticar

console.log('=== DEBUG DE GRÁFICOS ===');

// 1. Verificar se Chart.js está carregado
console.log('1. Chart.js carregado?', typeof Chart !== 'undefined' ? '✅ SIM' : '❌ NÃO');

// 2. Verificar todos os canvas
const allCanvas = document.querySelectorAll('canvas');
console.log(`2. Total de canvas encontrados: ${allCanvas.length}`);

allCanvas.forEach((canvas, index) => {
    const rect = canvas.getBoundingClientRect();
    console.log(`   Canvas ${index + 1} (${canvas.id}):`);
    console.log(`   - Largura: ${rect.width}px`);
    console.log(`   - Altura: ${rect.height}px`);
    console.log(`   - Visível: ${rect.width > 0 && rect.height > 0 ? '✅' : '❌'}`);
    console.log(`   - Display: ${window.getComputedStyle(canvas).display}`);
});

// 3. Verificar instâncias de gráficos
const chartInstances = [
    'feedbackChart',
    'hoursChart',
    'weekdayChart',
    'areasChart',
    'intentsChart',
    'usersChart'
];

console.log('3. Instâncias de gráficos:');
chartInstances.forEach(name => {
    const exists = window[name] !== undefined;
    console.log(`   - ${name}: ${exists ? '✅ Existe' : '❌ Não existe'}`);
});

// 4. Verificar se há dados carregados
console.log('4. Dados de analytics:', window.lastAnalyticsData ? '✅ Carregados' : '❌ Não carregados');
if (window.lastAnalyticsData) {
    console.log('   Estrutura dos dados:', Object.keys(window.lastAnalyticsData));
}

// 5. Verificar erros no console
console.log('5. Verifique se há erros VERMELHOS acima neste console');

// 6. Verificar containers dos gráficos
const containers = document.querySelectorAll('.chart-container');
console.log(`6. Containers de gráficos: ${containers.length}`);
containers.forEach((container, index) => {
    const rect = container.getBoundingClientRect();
    console.log(`   Container ${index + 1}:`);
    console.log(`   - Largura: ${rect.width}px`);
    console.log(`   - Altura: ${rect.height}px`);
    console.log(`   - Display: ${window.getComputedStyle(container).display}`);
});

// 7. Testar criação manual de um gráfico
console.log('7. Testando criação manual de gráfico...');
try {
    const testCanvas = document.getElementById('feedback-chart');
    if (testCanvas) {
        const testCtx = testCanvas.getContext('2d');
        const testChart = new Chart(testCtx, {
            type: 'doughnut',
            data: {
                labels: ['Teste A', 'Teste B', 'Teste C'],
                datasets: [{
                    data: [10, 20, 30],
                    backgroundColor: ['#ff6384', '#36a2eb', '#ffce56']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
        console.log('   ✅ Gráfico de teste criado com sucesso!');
        console.log('   Se você ver um gráfico colorido agora, o problema é com os dados da API');
        
        // Destruir depois de 5 segundos
        setTimeout(() => {
            testChart.destroy();
            console.log('   Gráfico de teste removido');
        }, 5000);
    } else {
        console.log('   ❌ Canvas feedback-chart não encontrado');
    }
} catch (e) {
    console.log('   ❌ Erro ao criar gráfico de teste:', e);
}

console.log('=== FIM DO DEBUG ===');
console.log('📋 COPIE TODOS OS RESULTADOS ACIMA E ME ENVIE');
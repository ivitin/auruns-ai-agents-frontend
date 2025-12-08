// Configuração
const API_URL = 'http://localhost:8000/api/v1';
let currentUser = null;

// Cores para gráficos
const chartColors = {
    primary: '#2563eb',
    secondary: '#1e40af',
    success: '#10b981',
    danger: '#ef4444',
    light: '#64748b',
    backgrounds: [
        'rgba(37, 99, 235, 0.8)',
        'rgba(16, 185, 129, 0.8)',
        'rgba(236, 72, 153, 0.8)',
        'rgba(245, 158, 11, 0.8)',
        'rgba(139, 92, 246, 0.8)',
        'rgba(6, 182, 212, 0.8)',
        'rgba(239, 68, 68, 0.8)',
        'rgba(16, 185, 129, 0.8)'
    ]
};

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Analytics iniciando...');
    
    // Verificar se Chart.js está carregado
    if (typeof Chart === 'undefined') {
        console.error('❌ Chart.js não está carregado!');
        alert('ERRO: Chart.js não foi carregado. Verifique a conexão com a internet.');
        return;
    }
    console.log('✅ Chart.js carregado');
    
    checkAuthentication();
    setupEventListeners();
    
    // Pequeno delay para garantir que o DOM está pronto
    setTimeout(() => {
        loadAnalyticsData();
    }, 500);
});

function getDefaultChartOptions() {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'bottom',
                labels: {
                    boxWidth: 12,
                    font: {
                        size: 11
                    }
                }
            },
            title: {
                display: false
            }
        }
    };
}

function getPieChartOptions() {
    return {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
            padding: {
                top: 20,
                right: 20,
                bottom: 40,
                left: 20
            }
        },
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    boxWidth: 12,
                    font: {
                        size: 11
                    },
                    padding: 15
                }
            }
        },
        animation: {
            duration: 500
        },
        elements: {
            arc: {
                borderWidth: 0
            }
        }
    };
}

function getBarChartOptions() {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
            y: {
                beginAtZero: true
            }
        }
    };
}

function checkAuthentication() {
    const userData = localStorage.getItem('currentUser');
    if (!userData) {
        console.warn('⚠️ Usuário não autenticado, redirecionando...');
        window.location.href = 'login.html';
        return;
    }
    currentUser = JSON.parse(userData);
    console.log('✅ Usuário autenticado:', currentUser.username);
}

function setupEventListeners() {
    console.log('🔧 Configurando event listeners...');
    
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const section = btn.dataset.section;
            changeSection(section);
        });
    });

    document.getElementById('refreshBtn').addEventListener('click', () => {
        console.log('🔄 Recarregando dados...');
        loadAnalyticsData();
    });

    document.getElementById('exportBtn').addEventListener('click', () => {
        exportReport();
    });

    document.getElementById('backToChat').addEventListener('click', () => {
        window.location.href = 'index.html';
    });

    document.getElementById('dateRangeFilter').addEventListener('change', (e) => {
        loadAnalyticsData(e.target.value);
    });
    
    console.log('✅ Event listeners configurados');
}

function changeSection(section) {
    console.log(`📊 Mudando para seção: ${section}`);
    
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.section === section) {
            btn.classList.add('active');
        }
    });

    document.querySelectorAll('.dashboard-section').forEach(sec => {
        sec.classList.remove('active');
    });
    
    const targetSection = document.getElementById(`${section}-section`);
    if (targetSection) {
        targetSection.classList.add('active');
        
        // Forçar resize dos gráficos após mudança de seção
        setTimeout(() => {
            forceChartResize();
        }, 100);
    }
}

function forceChartResize() {
    console.log('🔄 Forçando resize dos gráficos...');
    const charts = ['feedbackChart', 'hoursChart', 'weekdayChart', 'areasChart', 'intentsChart', 'usersChart'];
    
    charts.forEach(chartName => {
        if (window[chartName]) {
            try {
                window[chartName].resize();
                console.log(`✅ ${chartName} redimensionado`);
            } catch (e) {
                console.error(`❌ Erro ao redimensionar ${chartName}:`, e);
            }
        }
    });
}

async function loadAnalyticsData(dateRange = 'all') {
    console.log('📥 Carregando dados de analytics...');
    showLoading(true);
    
    try {
        const response = await fetch(`${API_URL}/analytics/report`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ Dados recebidos:', data);
        
        window.lastAnalyticsData = data;
        
        // Verificar se os dados têm a estrutura esperada
        if (!data.overall || !data.usage || !data.content || !data.performance || !data.engagement) {
            console.error('❌ Estrutura de dados inválida:', data);
            throw new Error('Estrutura de dados inválida');
        }
        
        console.log('📊 Atualizando métricas gerais...');
        updateOverallMetrics(data.overall);
        
        console.log('⏰ Atualizando métricas de uso...');
        updateUsageMetrics(data.usage);
        
        console.log('🧠 Atualizando métricas de conteúdo...');
        updateContentMetrics(data.content);
        
        console.log('⚡ Atualizando métricas de performance...');
        updatePerformanceMetrics(data.performance);
        
        console.log('👥 Atualizando métricas de engajamento...');
        updateEngagementMetrics(data.engagement);
        
        console.log('✅ Todos os dados carregados com sucesso!');
        
    } catch (error) {
        console.error('❌ Erro ao carregar analytics:', error);
        showError(`Não foi possível carregar os dados de analytics.\nErro: ${error.message}\nVerifique se a API está rodando em ${API_URL}`);
    } finally {
        showLoading(false);
    }
}

function exportReport() {
    const reportData = {
        title: "Relatório de Analytics - Industrial AI Agent",
        generated: new Date().toLocaleString(),
        overall: getMetricsData('overall'),
        usage: getMetricsData('usage'),
        content: getMetricsData('content'),
        performance: getMetricsData('performance'),
        engagement: getMetricsData('engagement')
    };
    
    const jsonData = JSON.stringify(reportData, null, 2);
    const blob = new Blob([jsonData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `analytics-report-${new Date().toISOString().slice(0,10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    console.log('✅ Relatório exportado');
}

function updateOverallMetrics(data) {
    console.log('📊 Criando gráfico de feedback...');
    
    document.getElementById('total-users').textContent = data.total_users || '0';
    document.getElementById('active-users').textContent = data.active_users_24h || '0';
    document.getElementById('total-interactions').textContent = data.total_interactions || '0';
    document.getElementById('avg-interactions').textContent = data.avg_interactions_per_user || '0';
    document.getElementById('satisfaction-rate').textContent = `${data.feedback?.satisfaction || '0'}%`;
    document.getElementById('feedback-rate').textContent = data.feedback?.rate || '0';
    
    const feedbackCanvas = document.getElementById('feedback-chart');
    if (!feedbackCanvas) {
        console.error('❌ Canvas feedback-chart não encontrado!');
        return;
    }
    
    console.log('Canvas feedback encontrado:', feedbackCanvas);
    console.log('Dimensões:', feedbackCanvas.clientWidth, 'x', feedbackCanvas.clientHeight);
    
    // Forçar altura do canvas
    feedbackCanvas.style.height = '200px';
    feedbackCanvas.height = 200;
    
    const feedbackCtx = feedbackCanvas.getContext('2d');
    
    if (window.feedbackChart) {
        window.feedbackChart.destroy();
    }
    
    const chartData = {
        labels: ['Positivo', 'Negativo', 'Sem Feedback'],
        datasets: [{
            data: [
                data.feedback?.positive || 0, 
                data.feedback?.negative || 0,
                data.total_interactions - (data.feedback?.positive || 0) - (data.feedback?.negative || 0)
            ],
            backgroundColor: [
                chartColors.success,
                chartColors.danger,
                chartColors.light
            ]
        }]
    };
    
    console.log('Dados do gráfico:', chartData);
    
    try {
        window.feedbackChart = new Chart(feedbackCtx, {
            type: 'doughnut',
            data: chartData,
            options: getPieChartOptions()
        });
        console.log('✅ Gráfico de feedback criado!');
    } catch (e) {
        console.error('❌ Erro ao criar gráfico de feedback:', e);
    }
}

function updateUsageMetrics(data) {
    console.log('⏰ Criando gráficos de uso...');
    
    // Gráfico de horas
    const hoursData = data.peak_hours || {};
    const hours = Object.keys(hoursData);
    const hoursCounts = Object.values(hoursData);
    
    const hoursCanvas = document.getElementById('hours-chart');
    if (!hoursCanvas) {
        console.error('❌ Canvas hours-chart não encontrado!');
        return;
    }
    
    hoursCanvas.style.height = '250px';
    hoursCanvas.height = 250;
    
    const hoursCtx = hoursCanvas.getContext('2d');
    if (window.hoursChart) window.hoursChart.destroy();
    
    try {
        window.hoursChart = new Chart(hoursCtx, {
            type: 'bar',
            data: {
                labels: hours.map(h => `${h}:00`),
                datasets: [{
                    label: 'Interações',
                    data: hoursCounts,
                    backgroundColor: chartColors.primary,
                    borderWidth: 0
                }]
            },
            options: getBarChartOptions()
        });
        console.log('✅ Gráfico de horas criado!');
    } catch (e) {
        console.error('❌ Erro ao criar gráfico de horas:', e);
    }
    
    // Gráfico de dias da semana
    const weekdayData = data.weekday_distribution || {};
    const weekdays = Object.keys(weekdayData);
    const weekdayCounts = Object.values(weekdayData);
    
    const weekdayCanvas = document.getElementById('weekday-chart');
    if (!weekdayCanvas) {
        console.error('❌ Canvas weekday-chart não encontrado!');
        return;
    }
    
    weekdayCanvas.style.height = '250px';
    weekdayCanvas.height = 250;
    
    const weekdayCtx = weekdayCanvas.getContext('2d');
    if (window.weekdayChart) window.weekdayChart.destroy();
    
    try {
        window.weekdayChart = new Chart(weekdayCtx, {
            type: 'bar',
            data: {
                labels: weekdays,
                datasets: [{
                    label: 'Interações',
                    data: weekdayCounts,
                    backgroundColor: chartColors.secondary,
                    borderWidth: 0
                }]
            },
            options: getBarChartOptions()
        });
        console.log('✅ Gráfico de dias da semana criado!');
    } catch (e) {
        console.error('❌ Erro ao criar gráfico de dias:', e);
    }
    
    // Tabela de top queries
    const topQueriesTable = document.getElementById('top-queries-table').querySelector('tbody');
    topQueriesTable.innerHTML = '';
    
    const topQueries = data.top_queries || [];
    
    if (topQueries.length === 0) {
        topQueriesTable.innerHTML = '<tr><td colspan="2">Nenhum dado disponível</td></tr>';
    } else {
        topQueries.forEach(query => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${query.query}</td>
                <td>${query.count}</td>
            `;
            topQueriesTable.appendChild(row);
        });
    }
}

function updateContentMetrics(data) {
    console.log('🧠 Criando gráficos de conteúdo...');
    
    const areasData = data.top_areas || {};
    const areas = Object.keys(areasData);
    const areaCounts = Object.values(areasData);
    
    const areasCanvas = document.getElementById('areas-chart');
    if (!areasCanvas) {
        console.error('❌ Canvas areas-chart não encontrado!');
        return;
    }
    
    areasCanvas.style.height = '300px';
    areasCanvas.height = 300;
    
    const areasCtx = areasCanvas.getContext('2d');
    if (window.areasChart) window.areasChart.destroy();
    
    try {
        window.areasChart = new Chart(areasCtx, {
            type: 'pie',
            data: {
                labels: areas,
                datasets: [{
                    data: areaCounts,
                    backgroundColor: chartColors.backgrounds
                }]
            },
            options: getPieChartOptions()
        });
        console.log('✅ Gráfico de áreas criado!');
    } catch (e) {
        console.error('❌ Erro ao criar gráfico de áreas:', e);
    }
    
    document.getElementById('rag-success-rate').textContent = `${data.rag_success_rate || '0'}%`;
    document.getElementById('no-results').textContent = data.queries_without_results || '0';
    
    const topEquipmentsTable = document.getElementById('top-equipments-table').querySelector('tbody');
    topEquipmentsTable.innerHTML = '';
    
    const topEquipments = Object.entries(data.top_equipments || {}).map(([code, count]) => ({ code, count }));
    
    if (topEquipments.length === 0) {
        topEquipmentsTable.innerHTML = '<tr><td colspan="2">Nenhum dado disponível</td></tr>';
    } else {
        topEquipments.forEach(eq => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${eq.code}</td>
                <td>${eq.count}</td>
            `;
            topEquipmentsTable.appendChild(row);
        });
    }
}

function updatePerformanceMetrics(data) {
    console.log('⚡ Criando gráficos de performance...');
    
    const intentData = data.intent_distribution || {};
    const intents = Object.keys(intentData);
    const intentCounts = Object.values(intentData);
    
    const intentsCanvas = document.getElementById('intents-chart');
    if (!intentsCanvas) {
        console.error('❌ Canvas intents-chart não encontrado!');
        return;
    }
    
    intentsCanvas.style.height = '300px';
    intentsCanvas.height = 300;
    
    const intentsCtx = intentsCanvas.getContext('2d');
    if (window.intentsChart) window.intentsChart.destroy();
    
    try {
        window.intentsChart = new Chart(intentsCtx, {
            type: 'doughnut',
            data: {
                labels: intents,
                datasets: [{
                    data: intentCounts,
                    backgroundColor: chartColors.backgrounds
                }]
            },
            options: getPieChartOptions()
        });
        console.log('✅ Gráfico de intents criado!');
    } catch (e) {
        console.error('❌ Erro ao criar gráfico de intents:', e);
    }
    
    document.getElementById('avg-response-length').textContent = data.avg_response_length || '0';
    document.getElementById('total-responses').textContent = data.total_responses_generated || '0';
}

function updateEngagementMetrics(data) {
    console.log('👥 Criando gráficos de engajamento...');
    
    document.getElementById('power-users').textContent = data.power_users || '0';
    document.getElementById('regular-users').textContent = data.regular_users || '0';
    document.getElementById('casual-users').textContent = data.casual_users || '0';
    document.getElementById('retention-rate').textContent = `${data.retention_rate || '0'}%`;
    
    const usersCanvas = document.getElementById('users-distribution-chart');
    if (!usersCanvas) {
        console.error('❌ Canvas users-distribution-chart não encontrado!');
        return;
    }
    
    usersCanvas.style.height = '300px';
    usersCanvas.height = 300;
    
    const usersCtx = usersCanvas.getContext('2d');
    if (window.usersChart) window.usersChart.destroy();
    
    try {
        window.usersChart = new Chart(usersCtx, {
            type: 'bar',
            data: {
                labels: ['Power Users', 'Usuários Regulares', 'Usuários Casuais'],
                datasets: [{
                    label: 'Quantidade',
                    data: [
                        data.power_users || 0,
                        data.regular_users || 0,
                        data.casual_users || 0
                    ],
                    backgroundColor: [
                        chartColors.primary,
                        chartColors.success,
                        chartColors.light
                    ],
                    borderWidth: 0
                }]
            },
            options: getBarChartOptions()
        });
        console.log('✅ Gráfico de usuários criado!');
    } catch (e) {
        console.error('❌ Erro ao criar gráfico de usuários:', e);
    }
}

function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    if (show) {
        overlay.style.display = 'flex';
    } else {
        overlay.style.display = 'none';
    }
}

function showError(message) {
    alert(message);
    console.error('Erro:', message);
}

function getMetricsData(section) {
    switch (section) {
        case 'overall':
            return {
                total_users: document.getElementById('total-users').textContent,
                active_users: document.getElementById('active-users').textContent,
                total_interactions: document.getElementById('total-interactions').textContent,
                satisfaction: document.getElementById('satisfaction-rate').textContent
            };
        default:
            return {};
    }
}
// Arquivo: chart-fix.js

// Função para corrigir problemas de visibilidade com gráficos
document.addEventListener('DOMContentLoaded', function() {
    // Garantir que os contêineres de gráficos tenham altura adequada
    document.querySelectorAll('.chart-container canvas').forEach(canvas => {
        canvas.style.height = '250px';
    });

    // Forçar altura para gráficos de pizza/rosca
    document.querySelectorAll('.pie-chart-container').forEach(container => {
        container.style.minHeight = '300px';
    });

    // Forçar renderização de todos os gráficos após um pequeno delay
    setTimeout(function() {
        forceChartsRender();
    }, 500);

    // Adicionar evento para redimensionar gráficos quando seção ficar visível
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            setTimeout(function() {
                forceChartsRender();
            }, 300);
        });
    });

    // Função para forçar a renderização de todos os gráficos
    function forceChartsRender() {
        try {
            if (window.feedbackChart) {
                window.feedbackChart.resize();
                window.feedbackChart.render();
            }
            if (window.areasChart) {
                window.areasChart.resize();
                window.areasChart.render();
            }
            if (window.intentsChart) {
                window.intentsChart.resize();
                window.intentsChart.render();
            }
            if (window.hoursChart) {
                window.hoursChart.resize();
                window.hoursChart.render();
            }
            if (window.weekdayChart) {
                window.weekdayChart.resize();
                window.weekdayChart.render();
            }
            if (window.usersChart) {
                window.usersChart.resize();
                window.usersChart.render();
            }
            console.log('Gráficos redimensionados e renderizados');
        } catch (e) {
            console.error('Erro ao renderizar gráficos:', e);
        }
    }
});

// Solução de contingência para gráficos que não aparecem
window.addEventListener('load', function() {
    setTimeout(function() {
        // Forçar visibilidade de todos os canvas
        document.querySelectorAll('canvas').forEach(canvas => {
            canvas.style.display = 'block';
            canvas.style.height = '250px';
            canvas.style.width = '100%';
        });
        
        // Reexecutar todas as funções de atualização de gráficos
        if (window.lastAnalyticsData) {
            updateOverallMetrics(window.lastAnalyticsData.overall);
            updateUsageMetrics(window.lastAnalyticsData.usage);
            updateContentMetrics(window.lastAnalyticsData.content);
            updatePerformanceMetrics(window.lastAnalyticsData.performance);
            updateEngagementMetrics(window.lastAnalyticsData.engagement);
        } else {
            // Se não tiver dados, recarregar
            document.getElementById('refreshBtn').click();
        }
    }, 1000);
});
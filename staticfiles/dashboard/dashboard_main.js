(function () {
    const C = window.CUVETAS;
    if (!C) {
        console.warn('Datos de CUVETAS no encontrados');
        return;
    }

    const INDIGO  = '#4F6EF7';
    const AMBER   = '#F59E0B';
    const GREEN   = '#22C55E';
    const RED     = '#EF4444';
    const PURPLE  = '#8B5CF6';
    const GRID_C  = 'rgba(0,0,0,.06)';

    Chart.defaults.font.family = "'Inter', system-ui, sans-serif";
    Chart.defaults.color = '#8898AA';

    // ─── Función para obtener el contenedor padre ───
    function getContainer(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;
        return canvas.parentElement;
    }

    // ─── Inicializar gráficas ───
    const chartInstances = [];

    // 1. Cuvetas por mes — barras agrupadas
    const ctxMes = document.getElementById('chartMes');
    let chartMes = null;
    if (ctxMes) {
        chartMes = new Chart(ctxMes, {
            type: 'bar',
            data: {
                labels: C.mesLabels,
                datasets: [
                    { label: 'Grandes', data: C.mesGrandes, backgroundColor: INDIGO, borderRadius: 5, borderSkipped: false },
                    { label: 'Pequeñas', data: C.mesPequenas, backgroundColor: AMBER, borderRadius: 5, borderSkipped: false },
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top', labels: { usePointStyle: true, pointStyle: 'circle', padding: 14 } },
                    tooltip: { mode: 'index', intersect: false }
                },
                scales: {
                    x: { grid: { display: false }, ticks: { font: { size: 11 } } },
                    y: { grid: { color: GRID_C }, beginAtZero: true, ticks: { precision: 0 } }
                }
            }
        });
        chartInstances.push(chartMes);
    }

    // 2. Estados — dona
    const ctxEstados = document.getElementById('chartEstados');
    let chartEstados = null;
    if (ctxEstados) {
        chartEstados = new Chart(ctxEstados, {
            type: 'doughnut',
            data: {
                labels: C.estadoLabels,
                datasets: [{
                    data: C.estadoVals,
                    backgroundColor: [GREEN, AMBER, INDIGO, RED],
                    borderWidth: 2,
                    borderColor: '#fff',
                    hoverOffset: 6,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '65%',
                plugins: {
                    legend: { position: 'bottom', labels: { usePointStyle: true, pointStyle: 'circle', padding: 10, font: { size: 11 } } }
                }
            }
        });
        chartInstances.push(chartEstados);
    }

    // 3. Actividad semanal — línea
    const ctxSemana = document.getElementById('chartSemana');
    let chartSemana = null;
    if (ctxSemana) {
        chartSemana = new Chart(ctxSemana, {
            type: 'line',
            data: {
                labels: C.semLabels,
                datasets: [{
                    label: 'Registros',
                    data: C.semVals,
                    borderColor: PURPLE,
                    backgroundColor: 'rgba(139,92,246,.12)',
                    fill: true,
                    tension: .4,
                    pointRadius: 4,
                    pointBackgroundColor: PURPLE,
                    borderWidth: 2,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, ticks: { font: { size: 10 } } },
                    y: { grid: { color: GRID_C }, beginAtZero: true, ticks: { precision: 0 } }
                }
            }
        });
        chartInstances.push(chartSemana);
    }

    // 4. Proporción grande vs pequeña — pie
    const ctxProp = document.getElementById('chartProp');
    let chartProp = null;
    if (ctxProp) {
        chartProp = new Chart(ctxProp, {
            type: 'pie',
            data: {
                labels: ['Grandes', 'Pequeñas'],
                datasets: [{
                    data: [C.totalGrandes, C.totalPequenas],
                    backgroundColor: [INDIGO, AMBER],
                    borderWidth: 2,
                    borderColor: '#fff',
                    hoverOffset: 6,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { usePointStyle: true, pointStyle: 'circle', padding: 10, font: { size: 11 } } },
                    tooltip: {
                        callbacks: {
                            label: function (ctx) {
                                const tot = ctx.dataset.data.reduce((a, b) => a + b, 0);
                                const pct = tot ? ((ctx.raw / tot) * 100).toFixed(1) : 0;
                                return ` ${ctx.label}: ${ctx.raw} (${pct}%)`;
                            }
                        }
                    }
                }
            }
        });
        chartInstances.push(chartProp);
    }

    // ─── ACTUALIZAR FECHA ───
    const dateRange = document.getElementById('kdDateRange');
    if (dateRange) {
        const hoy = new Date();
        const mes = hoy.toLocaleString('es', { month: 'long' });
        dateRange.textContent = `${mes} ${hoy.getFullYear()}`;
    }

    // ═══════════════════════════════════════════════════════════════════
    // ─── SISTEMA DE REDIMENSIONAMIENTO ROBUSTO ──────────────────────
    // ═══════════════════════════════════════════════════════════════════

    // ─── Función para redimensionar todas las gráficas ───
    function resizeAllCharts() {
        chartInstances.forEach(function(chart) {
            if (chart && typeof chart.resize === 'function') {
                try {
                    chart.resize();
                } catch (e) {
                    // Silenciar errores
                }
            }
        });
    }

    // ─── 1. Redimensionar al cambiar el tamaño de la ventana ───
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(resizeAllCharts, 100);
    });

    // ─── 2. Redimensionar al colapsar/expandir el sidebar ───
    const sidebar = document.getElementById('alpSidebar');
    if (sidebar) {
        const observer = new MutationObserver(function() {
            // Esperar a que termine la animación del sidebar
            setTimeout(resizeAllCharts, 350);
        });
        observer.observe(sidebar, { attributes: true, attributeFilter: ['class'] });
    }

    // ─── 3. Redimensionar al hacer clic en el botón de toggle ───
    const toggleBtn = document.getElementById('alpToggle');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            setTimeout(resizeAllCharts, 400);
        });
    }

    // ─── 4. Redimensionar al cambiar el modo oscuro/claro ───
    const darkToggle = document.getElementById('alpDarkToggle');
    if (darkToggle) {
        darkToggle.addEventListener('click', function() {
            setTimeout(resizeAllCharts, 150);
        });
    }

    // ─── 5. Redimensionar al cambiar el tema de color ───
    document.querySelectorAll('.alp-tc').forEach(function(el) {
        el.addEventListener('click', function() {
            setTimeout(resizeAllCharts, 150);
        });
    });

    // ─── 6. Redimensionar después de cargar completamente ───
    window.addEventListener('load', function() {
        // Dar tiempo para que todo se renderice
        setTimeout(resizeAllCharts, 300);
        // También después de 1 segundo por si hay retardos
        setTimeout(resizeAllCharts, 1000);
    });

    // ─── 7. Redimensionar cuando se abre/cierra el selector de tema ───
    const themeFab = document.getElementById('alpThemeFab');
    if (themeFab) {
        themeFab.addEventListener('click', function() {
            setTimeout(resizeAllCharts, 200);
        });
    }

    // ─── 8. ResizeObserver para detectar cambios en los contenedores ───
    if (window.ResizeObserver) {
        const containers = [
            document.getElementById('chartMesContainer'),
            document.getElementById('chartEstadosContainer'),
            document.getElementById('chartSemanaContainer'),
            document.getElementById('chartPropContainer')
        ].filter(el => el !== null);

        const ro = new ResizeObserver(function() {
            resizeAllCharts();
        });

        containers.forEach(function(container) {
            ro.observe(container);
        });
    }

    // ─── 9. Redimensionar al cambiar la orientación del dispositivo ───
    window.addEventListener('orientationchange', function() {
        setTimeout(resizeAllCharts, 400);
    });

    console.log('📊 Dashboard de Cuvetas inicializado correctamente');
    console.log('📈 ' + chartInstances.length + ' gráficas registradas para redimensionamiento');

})();
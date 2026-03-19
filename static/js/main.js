/**
 * GigShield — Main JS v2
 * Clean, no-glitch sidebar + charts
 */

document.addEventListener('DOMContentLoaded', () => {
    initSidebar();
    initCharts();
});

/* ========================
   SIDEBAR
   ======================== */
function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const toggle = document.getElementById('sidebarToggle');
    const mobile = document.getElementById('mobileToggle');
    const main = document.getElementById('mainContent');

    if (toggle && sidebar) {
        toggle.addEventListener('click', e => {
            e.stopPropagation();
            sidebar.classList.toggle('collapsed');
            if (main) {
                main.style.marginLeft = sidebar.classList.contains('collapsed')
                    ? 'var(--sidebar-w-collapsed)'
                    : 'var(--sidebar-w)';
            }
        });
    }

    if (mobile && sidebar) {
        mobile.addEventListener('click', e => {
            e.stopPropagation();
            sidebar.classList.toggle('open');
        });

        document.addEventListener('click', e => {
            if (window.innerWidth <= 768 &&
                sidebar.classList.contains('open') &&
                !sidebar.contains(e.target) &&
                !mobile.contains(e.target)) {
                sidebar.classList.remove('open');
            }
        });
    }
}

/* ========================
   CHARTS
   ======================== */
function initCharts() {
    // ---- Claims Trend (line) ----
    const trendEl = document.getElementById('claimsTrendChart');
    if (trendEl) {
        const data = JSON.parse(trendEl.dataset.trend || '[]');
        new Chart(trendEl.getContext('2d'), {
            type: 'line',
            data: {
                labels: data.map(d => d.date),
                datasets: [{
                    label: 'Claims',
                    data: data.map(d => d.count),
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99,102,241,0.06)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.35,
                    pointRadius: 2,
                    pointBackgroundColor: '#6366f1',
                }]
            },
            options: chartOptions()
        });
    }

    // ---- Claims by Type (doughnut) ----
    const typeEl = document.getElementById('claimsByTypeChart');
    if (typeEl) {
        const data = JSON.parse(typeEl.dataset.types || '[]');
        const colors = {
            heavy_rain: '#38bdf8', extreme_heat: '#facc15',
            severe_pollution: '#a855f7', flooding: '#06b6d4',
            cyclone: '#f87171', civil_unrest: '#fbbf24',
            platform_outage: '#71717a',
        };
        new Chart(typeEl.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: data.map(d => d.disruption_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())),
                datasets: [{
                    data: data.map(d => d.count),
                    backgroundColor: data.map(d => colors[d.disruption_type] || '#6366f1'),
                    borderWidth: 0,
                    hoverOffset: 6,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '62%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#a1a1aa', padding: 10, font: { size: 11 }, usePointStyle: true }
                    }
                }
            }
        });
    }

    // ---- Premium Factors (radar) ----
    const factorsEl = document.getElementById('premiumFactorsChart');
    if (factorsEl) {
        const f = JSON.parse(factorsEl.dataset.factors || '{}');
        const labels = Object.keys(f).map(k => k.replace(/_factor|_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()));
        new Chart(factorsEl.getContext('2d'), {
            type: 'radar',
            data: {
                labels,
                datasets: [{
                    label: 'Risk Factor',
                    data: Object.values(f),
                    backgroundColor: 'rgba(99,102,241,0.10)',
                    borderColor: '#6366f1',
                    borderWidth: 2,
                    pointBackgroundColor: '#6366f1',
                    pointRadius: 3,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    r: {
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        angleLines: { color: 'rgba(255,255,255,0.05)' },
                        pointLabels: { color: '#a1a1aa', font: { size: 10 } },
                        ticks: { display: false },
                        suggestedMin: 0.7, suggestedMax: 1.5,
                    }
                }
            }
        });
    }
}

function chartOptions() {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
            x: {
                grid: { color: 'rgba(255,255,255,0.03)' },
                ticks: { color: '#71717a', font: { size: 10 } }
            },
            y: {
                grid: { color: 'rgba(255,255,255,0.03)' },
                ticks: { color: '#71717a', font: { size: 10 } },
                beginAtZero: true,
            }
        }
    };
}

/* ========================
   FORMAT
   ======================== */
function formatINR(n) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency', currency: 'INR', maximumFractionDigits: 0
    }).format(n);
}

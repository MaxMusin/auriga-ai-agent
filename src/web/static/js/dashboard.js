/**
 * JavaScript pour la page du tableau de bord
 */
document.addEventListener('DOMContentLoaded', function() {
    // Éléments du DOM
    const filterForm = document.getElementById('filter-form');
    const carSelect = document.getElementById('car-select');
    const trackSelect = document.getElementById('track-select');
    const setupsTable = document.getElementById('setups-table');
    const pagination = document.getElementById('pagination');
    const refreshSetupsBtn = document.getElementById('refresh-setups-btn');
    
    // Variables globales
    let currentPage = 1;
    const pageSize = 10;
    let totalPages = 1;
    let selectedCar = '';
    let selectedTrack = '';
    
    // Graphiques
    let lapTimeChart = null;
    let scoreChart = null;
    
    // Charge les voitures disponibles
    loadCars(carSelect);
    
    // Événement de changement de voiture
    carSelect.addEventListener('change', function() {
        loadTracks(this.value, trackSelect);
    });
    
    // Événement de soumission du formulaire de filtres
    filterForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        selectedCar = carSelect.value;
        selectedTrack = trackSelect.value;
        currentPage = 1;
        
        loadSetups();
        loadPerformanceData();
    });
    
    // Événement du bouton de rafraîchissement
    refreshSetupsBtn.addEventListener('click', function() {
        loadSetups();
        loadPerformanceData();
    });
    
    /**
     * Charge les setups pour la voiture et le circuit sélectionnés
     */
    async function loadSetups() {
        if (!selectedCar || !selectedTrack) {
            return;
        }
        
        // Affiche un indicateur de chargement
        setupsTable.querySelector('tbody').innerHTML = `
            <tr>
                <td colspan="6" class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Chargement...</span>
                    </div>
                </td>
            </tr>
        `;
        
        // Récupère les setups
        const result = await fetchAPI(`/api/web/setups?car_id=${selectedCar}&track_id=${selectedTrack}&page=${currentPage}&page_size=${pageSize}`);
        if (!result) {
            setupsTable.querySelector('tbody').innerHTML = `
                <tr>
                    <td colspan="6" class="text-center">Erreur lors du chargement des setups</td>
                </tr>
            `;
            return;
        }
        
        if (result.setups.length === 0) {
            setupsTable.querySelector('tbody').innerHTML = `
                <tr>
                    <td colspan="6" class="text-center">Aucun setup trouvé</td>
                </tr>
            `;
            pagination.innerHTML = '';
            return;
        }
        
        // Calcule le nombre total de pages
        totalPages = Math.ceil(result.total / pageSize);
        
        // Génère les lignes du tableau
        let html = '';
        for (const setup of result.setups) {
            // Récupère le temps au tour (si disponible)
            let lapTime = '-';
            if (setup.telemetry_results && setup.telemetry_results.length > 0) {
                lapTime = formatLapTime(setup.telemetry_results[0].lap_time);
            }
            
            html += `
                <tr>
                    <td>${setup.id}</td>
                    <td>${formatDate(setup.generation_time)}</td>
                    <td>${setup.source}</td>
                    <td>${lapTime}</td>
                    <td>${formatScore(setup.score)}</td>
                    <td>
                        <a href="/setup/${setup.id}" class="btn btn-sm btn-primary">Détails</a>
                    </td>
                </tr>
            `;
        }
        
        setupsTable.querySelector('tbody').innerHTML = html;
        
        // Met à jour la pagination
        updatePagination();
    }
    
    /**
     * Met à jour les contrôles de pagination
     */
    function updatePagination() {
        if (totalPages <= 1) {
            pagination.innerHTML = '';
            return;
        }
        
        let html = '';
        
        // Bouton "Précédent"
        html += `
            <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${currentPage - 1}">Précédent</a>
            </li>
        `;
        
        // Pages
        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || (i >= currentPage - 1 && i <= currentPage + 1)) {
                html += `
                    <li class="page-item ${i === currentPage ? 'active' : ''}">
                        <a class="page-link" href="#" data-page="${i}">${i}</a>
                    </li>
                `;
            } else if (i === currentPage - 2 || i === currentPage + 2) {
                html += `
                    <li class="page-item disabled">
                        <span class="page-link">...</span>
                    </li>
                `;
            }
        }
        
        // Bouton "Suivant"
        html += `
            <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${currentPage + 1}">Suivant</a>
            </li>
        `;
        
        pagination.innerHTML = html;
        
        // Ajoute les événements de clic sur les liens de pagination
        pagination.querySelectorAll('.page-link').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                
                const page = parseInt(this.dataset.page);
                if (isNaN(page) || page < 1 || page > totalPages) {
                    return;
                }
                
                currentPage = page;
                loadSetups();
            });
        });
    }
    
    /**
     * Charge les données de performance pour les graphiques
     */
    async function loadPerformanceData() {
        if (!selectedCar || !selectedTrack) {
            return;
        }
        
        // Récupère les données de performance
        const data = await fetchAPI(`/api/web/performance?car_id=${selectedCar}&track_id=${selectedTrack}`);
        if (!data || !data.setup_ids || data.setup_ids.length === 0) {
            // Aucune donnée disponible
            return;
        }
        
        // Crée le graphique des temps au tour
        createLapTimeChart(data);
        
        // Crée le graphique des scores
        createScoreChart(data);
    }
    
    /**
     * Crée le graphique des temps au tour
     */
    function createLapTimeChart(data) {
        const ctx = document.getElementById('lap-time-chart').getContext('2d');
        
        // Détruit le graphique existant s'il y en a un
        if (lapTimeChart) {
            lapTimeChart.destroy();
        }
        
        // Crée un nouveau graphique
        lapTimeChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.setup_ids.map(id => `Setup #${id}`),
                datasets: [{
                    label: 'Temps au tour (s)',
                    data: data.lap_times,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Temps (s)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Setup'
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Temps: ${formatLapTime(context.raw)}`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    /**
     * Crée le graphique des scores
     */
    function createScoreChart(data) {
        const ctx = document.getElementById('score-chart').getContext('2d');
        
        // Détruit le graphique existant s'il y en a un
        if (scoreChart) {
            scoreChart.destroy();
        }
        
        // Crée un nouveau graphique
        scoreChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.setup_ids.map(id => `Setup #${id}`),
                datasets: [{
                    label: 'Score',
                    data: data.scores,
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    tension: 0.1,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Score'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Setup'
                        }
                    }
                }
            }
        });
    }
});

/**
 * JavaScript pour la page de détails d'un setup
 */
document.addEventListener('DOMContentLoaded', function() {
    // Récupère l'ID du setup depuis l'URL
    const setupId = document.getElementById('setup-id').textContent;
    
    // Éléments du DOM
    const setupInfoEl = document.getElementById('setup-info');
    const setupPerformanceEl = document.getElementById('setup-performance');
    const setupParametersTable = document.getElementById('setup-parameters-table');
    const driverNotesEl = document.getElementById('driver-notes');
    
    // Graphiques
    let temperaturesChart = null;
    let wearChart = null;
    let stabilityChart = null;
    
    // Charge les détails du setup
    loadSetupDetails();
    
    /**
     * Charge les détails du setup
     */
    async function loadSetupDetails() {
        const setup = await fetchAPI(`/api/web/setup/${setupId}`);
        if (!setup) {
            showNotification('Erreur lors du chargement des détails du setup', 'danger');
            return;
        }
        
        // Affiche les informations générales
        displaySetupInfo(setup);
        
        // Affiche les performances
        displaySetupPerformance(setup);
        
        // Affiche les paramètres du setup
        displaySetupParameters(setup);
        
        // Affiche les données de télémétrie
        if (setup.telemetry_results && setup.telemetry_results.length > 0) {
            const telemetry = setup.telemetry_results[0];
            displayTelemetryData(telemetry);
        } else {
            // Aucune donnée de télémétrie disponible
            document.getElementById('temperatures-chart').parentNode.innerHTML = '<p class="text-center">Aucune donnée de télémétrie disponible</p>';
            document.getElementById('wear-chart').parentNode.innerHTML = '<p class="text-center">Aucune donnée de télémétrie disponible</p>';
            document.getElementById('stability-chart').parentNode.innerHTML = '<p class="text-center">Aucune donnée de télémétrie disponible</p>';
        }
    }
    
    /**
     * Affiche les informations générales du setup
     */
    function displaySetupInfo(setup) {
        setupInfoEl.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <div class="setup-info-item">
                        <span class="setup-info-label">Voiture:</span>
                        <span class="setup-info-value">${setup.car_id}</span>
                    </div>
                    <div class="setup-info-item">
                        <span class="setup-info-label">Circuit:</span>
                        <span class="setup-info-value">${setup.track_id}</span>
                    </div>
                    <div class="setup-info-item">
                        <span class="setup-info-label">Date de génération:</span>
                        <span class="setup-info-value">${formatDate(setup.generation_time)}</span>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="setup-info-item">
                        <span class="setup-info-label">Statut:</span>
                        <span class="setup-info-value">${setup.status}</span>
                    </div>
                    <div class="setup-info-item">
                        <span class="setup-info-label">Source:</span>
                        <span class="setup-info-value">${setup.source}</span>
                    </div>
                    <div class="setup-info-item">
                        <span class="setup-info-label">Score:</span>
                        <span class="setup-info-value">${formatScore(setup.score)}</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Affiche les performances du setup
     */
    function displaySetupPerformance(setup) {
        if (!setup.telemetry_results || setup.telemetry_results.length === 0) {
            setupPerformanceEl.innerHTML = '<p class="text-center">Aucune donnée de performance disponible</p>';
            return;
        }
        
        const telemetry = setup.telemetry_results[0];
        
        setupPerformanceEl.innerHTML = `
            <div class="row">
                <div class="col-md-12">
                    <div class="setup-info-item">
                        <span class="setup-info-label">Temps au tour:</span>
                        <span class="setup-info-value">${formatLapTime(telemetry.lap_time)}</span>
                    </div>
                </div>
            </div>
            <div class="row mt-3">
                <div class="col-md-6">
                    <div class="setup-info-item">
                        <span class="setup-info-label">Stabilité de la voiture:</span>
                        <span class="setup-info-value">${telemetry.telemetry_data.car_stability || '-'}/10</span>
                    </div>
                    <div class="setup-info-item">
                        <span class="setup-info-label">Stabilité en entrée de virage:</span>
                        <span class="setup-info-value">${telemetry.telemetry_data.corner_entry_stability || '-'}/10</span>
                    </div>
                    <div class="setup-info-item">
                        <span class="setup-info-label">Stabilité en sortie de virage:</span>
                        <span class="setup-info-value">${telemetry.telemetry_data.corner_exit_stability || '-'}/10</span>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="setup-info-item">
                        <span class="setup-info-label">Traction:</span>
                        <span class="setup-info-value">${telemetry.telemetry_data.traction || '-'}/10</span>
                    </div>
                    <div class="setup-info-item">
                        <span class="setup-info-label">Stabilité au freinage:</span>
                        <span class="setup-info-value">${telemetry.telemetry_data.braking_stability || '-'}/10</span>
                    </div>
                    <div class="setup-info-item">
                        <span class="setup-info-label">Conditions météo:</span>
                        <span class="setup-info-value">
                            ${telemetry.weather_conditions ? 
                                `${telemetry.weather_conditions.track_temp || '-'}°C piste, ${telemetry.weather_conditions.air_temp || '-'}°C air` : 
                                '-'}
                        </span>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Affiche les paramètres du setup
     */
    function displaySetupParameters(setup) {
        if (!setup.setup_parameters) {
            setupParametersTable.querySelector('tbody').innerHTML = `
                <tr>
                    <td colspan="3" class="text-center">Aucun paramètre disponible</td>
                </tr>
            `;
            return;
        }
        
        let html = '';
        for (const [param, value] of Object.entries(setup.setup_parameters)) {
            // Détermine l'unité (à partir des métadonnées si disponibles)
            let unit = '';
            if (typeof value === 'object' && value.value !== undefined && value.unit !== undefined) {
                unit = value.unit;
            }
            
            // Formate le nom du paramètre
            const formattedParam = param.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            
            // Formate la valeur
            const formattedValue = typeof value === 'object' ? value.value : value;
            
            html += `
                <tr>
                    <td>${formattedParam}</td>
                    <td>${formattedValue}</td>
                    <td>${unit}</td>
                </tr>
            `;
        }
        
        setupParametersTable.querySelector('tbody').innerHTML = html;
    }
    
    /**
     * Affiche les données de télémétrie
     */
    function displayTelemetryData(telemetry) {
        // Affiche les notes du pilote
        if (telemetry.driver_notes) {
            driverNotesEl.innerHTML = `<div class="alert alert-info">${telemetry.driver_notes}</div>`;
        } else {
            driverNotesEl.innerHTML = '<p class="text-center">Aucune note disponible</p>';
        }
        
        // Crée les graphiques
        createTemperaturesChart(telemetry);
        createWearChart(telemetry);
        createStabilityChart(telemetry);
    }
    
    /**
     * Crée le graphique des températures des pneus
     */
    function createTemperaturesChart(telemetry) {
        const ctx = document.getElementById('temperatures-chart').getContext('2d');
        
        // Récupère les données de température
        const data = {
            fl: telemetry.telemetry_data.tire_avg_temp_fl,
            fr: telemetry.telemetry_data.tire_avg_temp_fr,
            rl: telemetry.telemetry_data.tire_avg_temp_rl,
            rr: telemetry.telemetry_data.tire_avg_temp_rr
        };
        
        // Si aucune donnée n'est disponible
        if (!data.fl && !data.fr && !data.rl && !data.rr) {
            document.getElementById('temperatures-chart').parentNode.innerHTML = '<p class="text-center">Aucune donnée de température disponible</p>';
            return;
        }
        
        // Crée le graphique
        temperaturesChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Avant Gauche', 'Avant Droit', 'Arrière Gauche', 'Arrière Droit'],
                datasets: [{
                    label: 'Température moyenne (°C)',
                    data: [data.fl, data.fr, data.rl, data.rr],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.5)',
                        'rgba(54, 162, 235, 0.5)',
                        'rgba(255, 206, 86, 0.5)',
                        'rgba(75, 192, 192, 0.5)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)'
                    ],
                    borderWidth: 1
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
                            text: 'Température (°C)'
                        }
                    }
                }
            }
        });
    }
    
    /**
     * Crée le graphique d'usure des pneus
     */
    function createWearChart(telemetry) {
        const ctx = document.getElementById('wear-chart').getContext('2d');
        
        // Récupère les données d'usure
        const data = {
            fl: telemetry.telemetry_data.tire_wear_fl,
            fr: telemetry.telemetry_data.tire_wear_fr,
            rl: telemetry.telemetry_data.tire_wear_rl,
            rr: telemetry.telemetry_data.tire_wear_rr
        };
        
        // Si aucune donnée n'est disponible
        if (!data.fl && !data.fr && !data.rl && !data.rr) {
            document.getElementById('wear-chart').parentNode.innerHTML = '<p class="text-center">Aucune donnée d\'usure disponible</p>';
            return;
        }
        
        // Crée le graphique
        wearChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Avant Gauche', 'Avant Droit', 'Arrière Gauche', 'Arrière Droit'],
                datasets: [{
                    label: 'Usure (%)',
                    data: [data.fl, data.fr, data.rl, data.rr],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.5)',
                        'rgba(54, 162, 235, 0.5)',
                        'rgba(255, 206, 86, 0.5)',
                        'rgba(75, 192, 192, 0.5)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Usure (%)'
                        }
                    }
                }
            }
        });
    }
    
    /**
     * Crée le graphique de stabilité
     */
    function createStabilityChart(telemetry) {
        const ctx = document.getElementById('stability-chart').getContext('2d');
        
        // Récupère les données de stabilité
        const data = {
            car: telemetry.telemetry_data.car_stability,
            entry: telemetry.telemetry_data.corner_entry_stability,
            exit: telemetry.telemetry_data.corner_exit_stability,
            traction: telemetry.telemetry_data.traction,
            braking: telemetry.telemetry_data.braking_stability
        };
        
        // Si aucune donnée n'est disponible
        if (!data.car && !data.entry && !data.exit && !data.traction && !data.braking) {
            document.getElementById('stability-chart').parentNode.innerHTML = '<p class="text-center">Aucune donnée de stabilité disponible</p>';
            return;
        }
        
        // Crée le graphique
        stabilityChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Stabilité générale', 'Entrée de virage', 'Sortie de virage', 'Traction', 'Freinage'],
                datasets: [{
                    label: 'Évaluation (1-10)',
                    data: [data.car, data.entry, data.exit, data.traction, data.braking],
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(54, 162, 235, 1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        angleLines: {
                            display: true
                        },
                        suggestedMin: 0,
                        suggestedMax: 10
                    }
                }
            }
        });
    }
});

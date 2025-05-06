/**
 * JavaScript pour la page d'accueil
 */
document.addEventListener('DOMContentLoaded', function() {
    // Éléments du DOM
    const optimizationStatusEl = document.getElementById('optimization-status');
    const optimizationForm = document.getElementById('optimization-form');
    const carSelect = document.getElementById('car-select');
    const trackSelect = document.getElementById('track-select');
    const startOptimizationBtn = document.getElementById('start-optimization-btn');
    const stopOptimizationBtn = document.getElementById('stop-optimization-btn');
    const recentSetupsTable = document.getElementById('recent-setups-table');
    
    // Charge les voitures disponibles
    loadCars(carSelect);
    
    // Événement de changement de voiture
    carSelect.addEventListener('change', function() {
        loadTracks(this.value, trackSelect);
    });
    
    // Charge le statut de l'optimisation
    loadOptimizationStatus();
    
    // Charge les setups récents
    loadRecentSetups();
    
    // Rafraîchit les données toutes les 30 secondes
    setInterval(function() {
        loadOptimizationStatus();
        loadRecentSetups();
    }, 30000);
    
    // Événement de soumission du formulaire d'optimisation
    optimizationForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const carId = carSelect.value;
        const trackId = trackSelect.value;
        
        if (!carId || !trackId) {
            showNotification('Veuillez sélectionner une voiture et un circuit', 'danger');
            return;
        }
        
        // Désactive le bouton pendant la requête
        startOptimizationBtn.disabled = true;
        startOptimizationBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Démarrage...';
        
        // Envoie la requête à l'API
        const result = await postAPI('/api/v1/optimization/start', {
            car_id: carId,
            track_id: trackId
        });
        
        // Réactive le bouton
        startOptimizationBtn.disabled = false;
        startOptimizationBtn.textContent = 'Démarrer l\'optimisation';
        
        if (result && result.success) {
            showNotification('Optimisation démarrée avec succès');
            loadOptimizationStatus();
        } else {
            showNotification(result?.error || 'Erreur lors du démarrage de l\'optimisation', 'danger');
        }
    });
    
    // Événement du bouton d'arrêt de l'optimisation
    stopOptimizationBtn.addEventListener('click', async function() {
        // Désactive le bouton pendant la requête
        stopOptimizationBtn.disabled = true;
        stopOptimizationBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Arrêt...';
        
        // Envoie la requête à l'API
        const result = await postAPI('/api/v1/optimization/stop', {});
        
        // Réactive le bouton
        stopOptimizationBtn.disabled = false;
        stopOptimizationBtn.textContent = 'Arrêter l\'optimisation';
        
        if (result && result.success) {
            showNotification('Optimisation arrêtée avec succès');
            loadOptimizationStatus();
        } else {
            showNotification(result?.error || 'Erreur lors de l\'arrêt de l\'optimisation', 'danger');
        }
    });
    
    /**
     * Charge le statut de l'optimisation
     */
    async function loadOptimizationStatus() {
        const status = await fetchAPI('/api/web/optimization/status');
        if (!status) {
            optimizationStatusEl.innerHTML = '<div class="alert alert-danger">Erreur lors du chargement du statut</div>';
            return;
        }
        
        let html = '';
        
        if (status.is_active) {
            html = `
                <div class="status-card status-active">
                    <h4 class="text-success">Optimisation en cours</h4>
                    <p><strong>Voiture:</strong> ${status.car_id}</p>
                    <p><strong>Circuit:</strong> ${status.track_id}</p>
                    <p><strong>Démarré le:</strong> ${formatDate(status.start_time)}</p>
                    <p><strong>Setups testés:</strong> ${status.trials_completed}</p>
                    <p><strong>Setups en attente:</strong> ${status.trials_pending}</p>
                    <p><strong>Meilleur score:</strong> ${formatScore(status.best_score)}</p>
                </div>
            `;
            
            // Désactive le bouton de démarrage et active le bouton d'arrêt
            startOptimizationBtn.disabled = true;
            stopOptimizationBtn.disabled = false;
        } else {
            html = `
                <div class="status-card status-inactive">
                    <h4 class="text-danger">Aucune optimisation en cours</h4>
                    <p>Utilisez le formulaire ci-contre pour démarrer une nouvelle optimisation.</p>
                </div>
            `;
            
            // Active le bouton de démarrage et désactive le bouton d'arrêt
            startOptimizationBtn.disabled = false;
            stopOptimizationBtn.disabled = true;
        }
        
        optimizationStatusEl.innerHTML = html;
    }
    
    /**
     * Charge les setups récents
     */
    async function loadRecentSetups() {
        // Récupère d'abord la voiture et le circuit actifs
        const status = await fetchAPI('/api/web/optimization/status');
        if (!status || !status.is_active) {
            // Si aucune optimisation n'est en cours, on affiche un message
            recentSetupsTable.querySelector('tbody').innerHTML = `
                <tr>
                    <td colspan="6" class="text-center">Aucune optimisation en cours</td>
                </tr>
            `;
            return;
        }
        
        // Récupère les setups pour la voiture et le circuit actifs
        const result = await fetchAPI(`/api/web/setups?car_id=${status.car_id}&track_id=${status.track_id}&page=1&page_size=5`);
        if (!result) {
            recentSetupsTable.querySelector('tbody').innerHTML = `
                <tr>
                    <td colspan="6" class="text-center">Erreur lors du chargement des setups</td>
                </tr>
            `;
            return;
        }
        
        if (result.setups.length === 0) {
            recentSetupsTable.querySelector('tbody').innerHTML = `
                <tr>
                    <td colspan="6" class="text-center">Aucun setup trouvé</td>
                </tr>
            `;
            return;
        }
        
        // Génère les lignes du tableau
        let html = '';
        for (const setup of result.setups) {
            html += `
                <tr>
                    <td>${setup.id}</td>
                    <td>${setup.car_id}</td>
                    <td>${setup.track_id}</td>
                    <td>${formatDate(setup.generation_time)}</td>
                    <td>${formatScore(setup.score)}</td>
                    <td>
                        <a href="/setup/${setup.id}" class="btn btn-sm btn-primary">Détails</a>
                    </td>
                </tr>
            `;
        }
        
        recentSetupsTable.querySelector('tbody').innerHTML = html;
    }
});

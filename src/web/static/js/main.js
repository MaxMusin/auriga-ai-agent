/**
 * Fonctions utilitaires communes à toutes les pages
 */

// Formatte une date au format local
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// Formatte un temps au tour (secondes) au format mm:ss.SSS
function formatLapTime(lapTime) {
    if (!lapTime) return '-';
    
    const minutes = Math.floor(lapTime / 60);
    const seconds = Math.floor(lapTime % 60);
    const milliseconds = Math.floor((lapTime % 1) * 1000);
    
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}.${milliseconds.toString().padStart(3, '0')}`;
}

// Formatte un score avec 2 décimales
function formatScore(score) {
    if (score === null || score === undefined) return '-';
    return score.toFixed(2);
}

// Effectue une requête GET à l'API
async function fetchAPI(endpoint) {
    try {
        const response = await fetch(endpoint);
        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Erreur lors de la requête à ${endpoint}:`, error);
        return null;
    }
}

// Effectue une requête POST à l'API
async function postAPI(endpoint, data) {
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Erreur lors de la requête à ${endpoint}:`, error);
        return null;
    }
}

// Charge la liste des voitures disponibles
async function loadCars(selectElement) {
    const cars = await fetchAPI('/api/web/cars');
    if (!cars) return;
    
    selectElement.innerHTML = '<option value="" selected disabled>Sélectionner une voiture</option>';
    
    cars.forEach(car => {
        const option = document.createElement('option');
        option.value = car;
        option.textContent = car;
        selectElement.appendChild(option);
    });
}

// Charge la liste des circuits disponibles pour une voiture
async function loadTracks(carId, selectElement) {
    const tracks = await fetchAPI(`/api/web/tracks?car_id=${carId}`);
    if (!tracks) return;
    
    selectElement.innerHTML = '<option value="" selected disabled>Sélectionner un circuit</option>';
    
    tracks.forEach(track => {
        const option = document.createElement('option');
        option.value = track;
        option.textContent = track;
        selectElement.appendChild(option);
    });
}

// Affiche une notification
function showNotification(message, type = 'success') {
    // Crée l'élément de notification
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Ajoute la notification au body
    document.body.appendChild(notification);
    
    // Supprime la notification après 5 secondes
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 150);
    }, 5000);
}

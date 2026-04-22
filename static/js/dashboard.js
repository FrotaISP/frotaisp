/* static/js/dashboard.js */

(function() {
    // ---------- GRÁFICO DE CONSUMO ----------
    const labelsElem = document.getElementById('consumption-labels');
    const dataElem = document.getElementById('consumption-data');
    
    if (labelsElem && dataElem) {
        const labels = JSON.parse(labelsElem.textContent);
        const data = JSON.parse(dataElem.textContent);
        
        const ctx = document.getElementById('fuelConsumptionChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Litros',
                    data: data,
                    borderColor: '#0d6efd',
                    backgroundColor: 'rgba(13, 110, 253, 0.02)',
                    borderWidth: 3,
                    pointBackgroundColor: '#0d6efd',
                    pointBorderColor: '#fff',
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    tension: 0.2,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: '#e9ecef' },
                        title: {
                            display: true,
                            text: 'Litros'
                        }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        });
    }

    // ---------- MAPA LEAFLET ----------
    const mapElem = document.getElementById('vehicleMap');
    if (mapElem) {
        const map = L.map('vehicleMap').setView([-23.5505, -46.6333], 10);
        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);

        // Dados mockados – no futuro, substitua por fetch('/api/vehicles/locations/')
        const mockLocations = [
            { plate: 'ABC-1234', driver: 'João M.', lat: -23.561, lng: -46.655, status: 'moving' },
            { plate: 'DEF-5678', driver: 'Ana P.', lat: -23.580, lng: -46.610, status: 'idle' }
        ];

        mockLocations.forEach(v => {
            let color = v.status === 'moving' ? '#28a745' : '#ffc107';
            const icon = L.divIcon({
                html: `<i class="bi bi-truck" style="font-size:1.8rem;color:${color};-webkit-text-stroke:1px white;"></i>`,
                className: 'custom-marker',
                iconSize: [30, 30],
                popupAnchor: [0, -15]
            });
            L.marker([v.lat, v.lng], { icon }).addTo(map)
                .bindPopup(`<b>${v.plate}</b><br>${v.driver}`);
        });
    }
})();
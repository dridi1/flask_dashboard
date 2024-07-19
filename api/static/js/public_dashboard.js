window.onload = function() {
    // Initialize the map centered on Tunisia
    const map = L.map('map').setView([33.8869, 9.5375], 6);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // Leaflet Draw Control
    const drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    const drawControl = new L.Control.Draw({
        edit: {
            featureGroup: drawnItems
        },
        draw: {
            polygon: true,
            polyline: false,
            rectangle: false,
            circle: false,
            marker: false,
            circlemarker: false
        }
    });
    map.addControl(drawControl);

    // Handle the creation of drawn polygons
    map.on(L.Draw.Event.CREATED, function (event) {
        const layer = event.layer;
        drawnItems.addLayer(layer);

        // Store the coordinates of the polygon
        const polygonCoordinates = layer.getLatLngs()[0].map(coord => [coord.lat, coord.lng]);
        console.log('Polygon coordinates:', polygonCoordinates);

        // Send the coordinates to the server (Flask backend)
        fetch('/save_polygon', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ coordinates: polygonCoordinates })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Polygon saved:', data);
            if (data.status === 'success') {
                alert('Polygon has been successfully registered!');
            } else {
                alert('Failed to register the polygon. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error saving polygon:', error);
            alert('An error occurred while saving the polygon. Please try again.');
        });
    });
};

let navigation = document.querySelector('.navigation');
        let toggle = document.querySelector('.toggle');
        toggle.onclick = function(){
            navigation.classList.toggle('active')
        }
        ;
                
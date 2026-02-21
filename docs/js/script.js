// const API_BASE_URL = "http://192.168.68.107:8000";
const API_BASE_URL = "data/mock-response.json"; // for testing with local JSON file

// // worldwide search
// const SEARCH_QUERY = `https://nominatim.openstreetmap.org/search?format=json&limit=10&q=${query}`;
// bounded search for Portugal
const SEARCH_QUERY = "https://nominatim.openstreetmap.org/search?format=json&limit=10&countrycodes=pt&bounded=1&viewbox=-9.25,38.85,-9.05,38.65&q=${query}";
const BASE_MAP = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';

const isMobileDevice =
    /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
        navigator.userAgent
    );



const defaultLocation = [38.7369, -9.1427];
const defaultZoom = isMobileDevice ? 12 : 13;
const currentZoom = isMobileDevice ? 15 : 16;

const sidebarWidthPercent = isMobileDevice ? 0 : 30;
const bottomPanelHeightPercent = isMobileDevice ? 8 : 0;

const resetBtn = document.getElementById("resetAddress");
const latInput = document.getElementById("latInput");
const lonInput = document.getElementById("lonInput");
const addressInput = document.getElementById("addressInput");
const suggestionsBox = document.getElementById("suggestions");
const suggestionsWrapper = document.querySelector(".suggestions-wrapper");
const clearBtn = document.getElementById("clearSearch");
const searchWrapper = document.querySelector(".search-wrapper");
const scoreCard = document.querySelector(".score-card");

const thumbUpBtn = document.getElementById("thumbUp");
const thumbDownBtn = document.getElementById("thumbDown");

thumbUpBtn.addEventListener("click", () => sendFeedback(1));
thumbDownBtn.addEventListener("click", () => sendFeedback(0));

let debounceTimer;
let recenterBtn;
let marker;
let bufferCircle;
let currentLocation = null;
let parksLayer;
let routeLayer;

const map = L.map('map', {
    center: defaultLocation,
    zoom: defaultZoom,
    attributionControl: false,
    zoomControl: false,
});

L.tileLayer(BASE_MAP).addTo(map);

L.control.scale({
    position: isMobileDevice ? 'topleft' : 'bottomleft',
    metric: true,
    imperial: false,
    maxWidth: 200
}).addTo(map);

L.control.zoom({
    position: isMobileDevice ? 'topright' : 'bottomright'
}).addTo(map);

const recenterControl = L.Control.extend({
    options: { position: isMobileDevice ? 'topright' : 'bottomright' },

    onAdd: function () {
        recenterBtn = L.DomUtil.create('div', 'recenter-control');
        recenterBtn.innerHTML = "<img src='assets/icons/recenter.svg' alt='Recenter'>";
        recenterBtn.title = "Recenter Map";

        L.DomEvent.disableClickPropagation(recenterBtn);

        recenterBtn.onclick = function () {
            if (currentLocation) {
                map.setView(getOffsetLatLng(currentLocation, currentZoom), currentZoom);
            } else {
                map.setView(getOffsetLatLng(defaultLocation, defaultZoom), defaultZoom);
            }
        };

        return recenterBtn;
    }
});

map.addControl(new recenterControl());

// custom marker 
const lollipopIcon = L.divIcon({
    className: '',
    html: `
        <div class="lollipop-marker">
            <div class="lollipop-stick"></div>
            <div class="lollipop-head"></div>
        </div>
    `,
    iconSize: [20, 40],
    iconAnchor: [10, 40]
});

map.on('click', function (e) {
    updateLocation(e.latlng.lat, e.latlng.lng);
});



function updateLocation(lat, lon) {
    scoreCard.style.visibility = "hidden";

    currentLocation = [lat, lon];
    resetBtn.style.visibility = "visible";

    document.getElementById("latInput").value = lat.toFixed(6);
    document.getElementById("lonInput").value = lon.toFixed(6);

    if (marker) map.removeLayer(marker);
    if (bufferCircle) map.removeLayer(bufferCircle);
    if (parksLayer) map.removeLayer(parksLayer);
    if (routeLayer) map.removeLayer(routeLayer);

    marker = L.marker([lat, lon], { icon: lollipopIcon }).addTo(map);

    map.setView(getOffsetLatLng(currentLocation, currentZoom), currentZoom);
}

function getOffsetLatLng(latlng, zoom) {
    const projectedPoint = map.project(latlng, zoom);

    const mapSize = map.getSize();

    const overlayWidth = mapSize.x * (sidebarWidthPercent / 100);
    const offsetX = overlayWidth / 2;

    const overlayHeight = mapSize.y * (bottomPanelHeightPercent / 100);
    const offsetY = overlayHeight / 2;

    let shiftedPoint;

    if (isMobileDevice) {
        shiftedPoint = projectedPoint.subtract([0, -offsetY]);
    } else {
        shiftedPoint = projectedPoint.subtract([offsetX, 0]);
    }
    return map.unproject(shiftedPoint, zoom);
}


addressInput.addEventListener("input", function () {
    clearTimeout(debounceTimer);
    const query = this.value;

    if (query.length < 3) {
        suggestionsBox.innerHTML = "";
        suggestionsWrapper.style.visibility = "hidden";
        searchWrapper.classList.remove("active");
        clearBtn.style.display = "none";
        return;
    }

    clearBtn.style.display = query ? "block" : "none";

    debounceTimer = setTimeout(() => {
        fetchSuggestions(query);
    }, 250);
});

async function fetchSuggestions(query) {
    const response = await fetch(SEARCH_QUERY.replace("${query}", encodeURIComponent(query)));

    const data = await response.json();
    suggestionsBox.innerHTML = "";

    if (data.length > 0) {
        searchWrapper.classList.add("active");
        suggestionsWrapper.style.visibility = "visible";
    } else {
        searchWrapper.classList.remove("active");
        suggestionsWrapper.style.visibility = "hidden";
    }

    data.forEach(place => {
        const div = document.createElement("div");
        div.textContent = place.display_name;

        div.onclick = () => {
            updateLocation(parseFloat(place.lat), parseFloat(place.lon));
            suggestionsBox.innerHTML = "";
            suggestionsWrapper.style.visibility = "hidden";
            searchWrapper.classList.remove("active");
            addressInput.value = place.display_name;
        };

        suggestionsBox.appendChild(div);
    });
}

clearBtn.addEventListener("click", () => {
    addressInput.value = "";
    suggestionsBox.innerHTML = "";
    suggestionsWrapper.style.visibility = "hidden";
    searchWrapper.classList.remove("active");
    clearBtn.style.display = "none";
});

resetBtn.addEventListener("click", () => {
    // clear inputs
    addressInput.value = "";
    document.getElementById("latInput").value = "";
    document.getElementById("lonInput").value = "";

    // hide suggestions and clear button
    suggestionsBox.innerHTML = "";
    suggestionsWrapper.style.visibility = "hidden";
    searchWrapper.classList.remove("active");
    clearBtn.style.display = "none";
    scoreCard.style.visibility = "hidden";
    resetBtn.style.visibility = "hidden";

    // remove marker and circle
    if (marker) map.removeLayer(marker);
    if (bufferCircle) map.removeLayer(bufferCircle);
    if (parksLayer) map.removeLayer(parksLayer);
    if (routeLayer) map.removeLayer(routeLayer);
    routeLayer = null;
    marker = null;
    bufferCircle = null;
    currentLocation = null;

    // reset map view
    map.setView(getOffsetLatLng(defaultLocation, defaultZoom), defaultZoom);
});

latInput.addEventListener("change", updateFromLatLonInputs);
lonInput.addEventListener("change", updateFromLatLonInputs);

function updateFromLatLonInputs() {
    const lat = parseFloat(latInput.value);
    const lon = parseFloat(lonInput.value);

    if (isNaN(lat) || isNaN(lon)) return;

    updateLocation(lat, lon);
}

function getScore() {
    const lat = document.getElementById("latInput").value;
    const lon = document.getElementById("lonInput").value;

    if (!lat || !lon) {
        alert("Select a location first.");
        return;
    }

    if (bufferCircle) map.removeLayer(bufferCircle);
    if (parksLayer) map.removeLayer(parksLayer);
    if (routeLayer) map.removeLayer(routeLayer);

    bufferCircle = L.circle([lat, lon], {
        radius: 500,
        color: '#0ee071',
        fillColor: '#0ee071',
        fillOpacity: 0.07
    }).addTo(map);

    recenterBtn.click();


    // // for testing with local JSON file
    fetch(API_BASE_URL)
    // fetch(API_BASE_URL + `/api/v1/accessibility/accessibility-score?lat=${lat}&lon=${lon}&buffer_m=500`)
        .then(res => res.json())
        .then(data => {

            updateScores(data);
            drawParks(data.scores.parks);
            drawRoute(data.nearest_park_route);

            scoreCard.style.visibility = "visible";
        })
        .catch(err => {
            console.error(err);
            alert("Error fetching accessibility data.");
        });

}

function updateScores(data) {

    document.getElementById("score").innerText =
        data.accessibility_score.toFixed(2);

    document.getElementById("proximity").innerText =
        data.scores.proximity.toFixed(2);

    document.getElementById("quantity").innerText =
        data.scores.quantity.toFixed(2);

    document.getElementById("area").innerText =
        data.scores.area.toFixed(2);

    document.getElementById("diversity").innerText =
        data.scores.diversity.toFixed(2);

    document.getElementById("proximity-desc").innerText =
        `Nearest park is ${Math.round(
            Math.min(...data.scores.parks.map(p => p.distance))
        )}m away`;

    document.getElementById("quantity-desc").innerText =
        `${data.parks_found} green areas found within ${data.buffer_m}m`;

    document.getElementById("area-desc").innerText =
        `${Math.round(
            data.scores.parks.reduce((sum, p) => sum + p.area, 0)
        )} m² total green space`;

    const types = [...new Set(data.scores.parks.map(p => p.type))];

    document.getElementById("diversity-desc").innerText =
        `Types: ${types.join(", ")}`;
}

function drawParks(parks) {

    if (parksLayer) map.removeLayer(parksLayer);

    parksLayer = L.layerGroup();

    parks.forEach(park => {

        const geojsonFeature = {
            type: "Feature",
            geometry: park.geometry,
            properties: {
                name: park.name,
                type: park.type,
                area: park.area,
                distance: park.distance
            }
        };

        const layer = L.geoJSON(geojsonFeature, {
            style: {
                color: "#4ade80",
                weight: 1,
                fillOpacity: 0.4
            }
        });

        layer.bindPopup(`
            <strong>${park.name}</strong><br>
            Type: ${park.type}<br>
            Area: ${park.area.toFixed(0)} m²<br>
            Distance: ${park.distance.toFixed(0)} m
        `);

        parksLayer.addLayer(layer);
    });

    parksLayer.addTo(map);
}


function drawRoute(routeFeature) {

    if (!routeFeature) return;

    routeLayer = L.geoJSON(routeFeature, {
        style: function () {
            return {
                color: "#f92672",
                weight: getRouteWeight(map.getZoom()),
                opacity: 0.95,
                lineCap: "round",
                lineJoin: "round"
            };
        }
    }).addTo(map);

    routeLayer.bringToFront();
}

function getRouteWeight(zoom) {
    const minZoom = 12;
    const maxZoom = 18;
    const minWeight = 8;
    const maxWeight = 2;

    const clampedZoom = Math.max(minZoom, Math.min(maxZoom, zoom));

    return minWeight +
        ((clampedZoom - minZoom) / (maxZoom - minZoom)) *
        (maxWeight - minWeight);
}


function sendFeedback(liked) {

    if (liked == 1) {
        thumbUpBtn.classList.add('animate-up')
        setTimeout(() => {
            thumbUpBtn.classList.remove('animate-up');
        }, 400);
    } else {
        thumbDownBtn.classList.add('animate-down')
        setTimeout(() => {
            thumbDownBtn.classList.remove('animate-down');
        }, 400);
    }

    if (!currentLocation) return;

    const lat = currentLocation[0];
    const lon = currentLocation[1];

    const payload = {
        lat: lat,
        lon: lon,
        liked: liked,
        accessibility_score: parseFloat(document.getElementById("score").innerText),
        proximity_score: parseFloat(document.getElementById("proximity").innerText),
        quantity_score: parseFloat(document.getElementById("quantity").innerText),
        area_score: parseFloat(document.getElementById("area").innerText),
        diversity_score: parseFloat(document.getElementById("diversity").innerText),
        timestamp: new Date().toISOString(),
    };

    fetch(API_BASE_URL + `/api/v1/feedback/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    })
        .then(res => {
            if (!res.ok) throw new Error("Failed to send feedback");
            return res.json();
        })
        .then(() => {

            if (liked === 1) {
                thumbUpBtn.classList.add("active");
                thumbDownBtn.classList.remove("active");
            } else {
                thumbDownBtn.classList.add("active");
                thumbUpBtn.classList.remove("active");
            }

            console.log("Feedback saved");
        })
        .catch(err => {
            console.error(err);
        });
}
---
layout: default
title: "Bay Area Trail Explorer"
---

<style>
#map {
    height: 80vh;
    width: 100%;
    margin-bottom: 20px;
}

.filters {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
}

.filter-group {
    margin-bottom: 15px;
}

.filter-group label {
    display: inline-block;
    width: 120px;
    font-weight: bold;
}

.filter-group select, .filter-group input {
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    margin-right: 10px;
}

.filter-group input[type="range"] {
    width: 200px;
    margin-right: 10px;
}

#trip-date-label, #length-label, #elevation-label, #rating-label {
    font-weight: bold;
    color: #2c5530;
    min-width: 120px;
    display: inline-block;
}


.trail-info {
    background: white;
    padding: 10px;
    max-width: 300px;
    font-size: 14px;
}

.trail-name {
    font-weight: bold;
    color: #2c5530;
    margin-bottom: 5px;
}

.trail-rating {
    color: #ff6b35;
    font-weight: bold;
}

.trail-details {
    margin: 5px 0;
    color: #666;
}

.trail-features {
    margin-top: 8px;
}

.feature-tag {
    background: #e8f5e8;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 11px;
    margin-right: 4px;
    margin-bottom: 2px;
    display: inline-block;
}

.loading {
    text-align: center;
    padding: 20px;
    color: #666;
}

.stats {
    background: #fff;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.weather-info {
    margin-top: 10px;
    padding: 8px;
    background: #e3f2fd;
    border-radius: 4px;
    font-size: 12px;
}
</style>

<div class="stats">
    <div id="trail-stats">Loading trail statistics...</div>
</div>

<div class="filters">
    <div class="filter-group">
        <label for="difficulty-filter">Difficulty:</label>
        <select id="difficulty-filter">
            <option value="">All</option>
            <option value="Easy" selected>Easy</option>
            <option value="Moderate">Moderate</option>
            <option value="Hard">Hard</option>
        </select>
    </div>
    
    <div class="filter-group">
        <label for="length-filter">Max Length:</label>
        <input type="range" id="length-filter" min="1" max="20" value="20" step="0.5">
        <span id="length-label">All lengths</span>
    </div>
    
    <div class="filter-group">
        <label for="elevation-filter">Max Elevation Gain:</label>
        <input type="range" id="elevation-filter" min="0" max="5000" value="5000" step="100">
        <span id="elevation-label">All elevations</span>
    </div>
    
    <div class="filter-group">
        <label for="rating-filter">Min Star Rating:</label>
        <input type="range" id="rating-filter" min="1" max="5" value="4.7" step="0.1">
        <span id="rating-label">All ratings</span>
    </div>
    
    <div class="filter-group">
        <label for="trip-date">Trip Date:</label>
        <input type="date" id="trip-date">
    </div>
    
    <div class="filter-group">
        <button onclick="resetFilters()" style="background: #6c757d; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
            Reset Filters
        </button>
        <button onclick="findTrailsNearMe()" style="background: #28a745; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
            Find Trails Near Me
        </button>
        <button onclick="toggleHeatmap()" id="heatmap-toggle" style="background: #ff6b35; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
            Show Temperature Overlay
        </button>
    </div>
</div>

<div id="map"></div>

<div class="loading" id="loading">
    Loading trail data and initializing map...
</div>

<script>
// Google API Configuration (injected by Jekyll)
const GOOGLE_API_CONFIG = {
    mapsApiKey: '{{ site.google_api.maps_key }}',
    weatherApiKey: '{{ site.google_api.weather_key }}',
    weatherApiBaseUrl: 'https://weather.googleapis.com/v1/forecast/days:lookup'
};

// Centralized weather API fetching function
async function fetchWeatherForecast(latitude, longitude, days = 10) {
    const url = `${GOOGLE_API_CONFIG.weatherApiBaseUrl}?key=${GOOGLE_API_CONFIG.weatherApiKey}&location.latitude=${latitude}&location.longitude=${longitude}&days=${days}&pageSize=${days}`;
    
    try {
        const response = await fetch(url);
        if (response.ok) {
            return await response.json();
        } else {
            console.log('Weather API error:', response.status, response.statusText);
            return null;
        }
    } catch (error) {
        console.error('Weather API error:', error);
        return null;
    }
}

let map;
let markerCluster;
let trails = [];
let filteredTrails = [];
let markers = [];
let trailLabels = [];
let weatherCache = {};
let temperatureOverlay = null;
let temperatureCircles = [];

// Initialize map when Google Maps loads
function initMap() {
    // Center on Bay Area
    const bayAreaCenter = { lat: 37.4419, lng: -122.1430 };
    
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 10,
        center: bayAreaCenter,
        mapTypeId: 'terrain',
        mapId: '{{ site.google_api.maps_id }}' // Required for AdvancedMarkerElement
    });
    
    // Initialize MarkerClusterer
    markerCluster = new markerClusterer.MarkerClusterer({
        map: map,
        markers: []
    });
    
    // Add listeners to update trail labels when map changes
    map.addListener('zoom_changed', () => {
        updateTrailLabelsVisibility();
    });
    
    map.addListener('bounds_changed', () => {
        // Debounce bounds changes to avoid excessive updates during panning
        clearTimeout(window.boundsUpdateTimeout);
        window.boundsUpdateTimeout = setTimeout(() => {
            updateTrailLabelsVisibility();
        }, 300);
    });
    
    // Load trail data
    loadTrailData();
    
    // Hide loading indicator
    document.getElementById('loading').style.display = 'none';
}

// Make initMap available globally for Google Maps callback
window.initMap = initMap;

async function loadTrailData() {
    try {
        const response = await fetch('/trails/bay_area_trails.json');
        trails = await response.json();
        filteredTrails = trails;
        
        updateTrailStats();
        createMarkers();
        
        // Add event listeners for filters
        document.getElementById('difficulty-filter').addEventListener('change', applyFilters);
        document.getElementById('length-filter').addEventListener('input', function() {
            updateLengthLabel();
            applyFilters();
        });
        document.getElementById('elevation-filter').addEventListener('input', function() {
            updateElevationLabel();
            applyFilters();
        });
        document.getElementById('rating-filter').addEventListener('input', function() {
            updateRatingLabel();
            applyFilters();
        });
        document.getElementById('trip-date').addEventListener('change', function() {
            applyFilters();
            updateAllWeatherDisplays();
            refreshTemperatureOverlay();
        });
        
        // Set default to upcoming Saturday and update labels
        setDefaultTripDate();
        updateLengthLabel();
        updateElevationLabel();
        updateRatingLabel();
        
        // Apply initial filters to reflect default selections
        setTimeout(() => {
            applyFilters();
        }, 100);
        
        // Turn on temperature overlay by default
        setTimeout(() => {
            toggleHeatmap();
        }, 1000);
        
    } catch (error) {
        console.error('Error loading trail data:', error);
        document.getElementById('trail-stats').innerHTML = 'Error loading trail data.';
    }
}

function updateTrailStats() {
    const stats = {
        total: filteredTrails.length,
        avgRating: filteredTrails.reduce((sum, t) => sum + t.stars, 0) / filteredTrails.length,
        difficulties: {}
    };
    
    filteredTrails.forEach(trail => {
        stats.difficulties[trail.difficulty] = (stats.difficulties[trail.difficulty] || 0) + 1;
    });
    
    const statsHtml = `
        <strong>${stats.total}</strong> trails shown | 
        Avg rating: <strong>${stats.avgRating.toFixed(1)}★</strong> | 
        Easy: ${stats.difficulties.Easy || 0} | 
        Moderate: ${stats.difficulties.Moderate || 0} | 
        Hard: ${stats.difficulties.Hard || 0}
    `;
    
    document.getElementById('trail-stats').innerHTML = statsHtml;
}

function createMarkers() {
    // Clear existing markers and labels
    markers.forEach(marker => marker.setMap(null));
    trailLabels.forEach(label => label.setMap(null));
    markers = [];
    trailLabels = [];
    
    filteredTrails.forEach(trail => {
        // Create marker element with custom styling
        const markerElement = document.createElement('div');
        markerElement.innerHTML = createMarkerHTML(trail.difficulty);
        
        const marker = new google.maps.marker.AdvancedMarkerElement({
            position: { lat: trail.latitude, lng: trail.longitude },
            content: markerElement,
            title: trail.name
        });
        
        // Create text label element
        const labelElement = document.createElement('div');
        labelElement.innerHTML = `
            <div style="
                background: rgba(255, 255, 255, 0.9);
                padding: 4px 8px;
                border-radius: 4px;
                border: 1px solid #ddd;
                font-size: 11px;
                font-weight: bold;
                font-family: Arial, sans-serif;
                color: #2c5530;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                white-space: nowrap;
                text-align: center;
            ">
                ${trail.name}<br>
                <span style="color: ${getDifficultyColor(trail.difficulty)}; font-size: 10px;">
                    ${trail.difficulty || ''}
                </span>
            </div>
        `;
        
        const label = new google.maps.marker.AdvancedMarkerElement({
            position: { lat: trail.latitude, lng: trail.longitude },
            content: labelElement,
            map: null // Will be set based on zoom level and density
        });
        
        const infoWindow = new google.maps.InfoWindow({
            content: createInfoWindowContent(trail)
        });
        
        marker.addListener('click', () => {
            infoWindow.open(map, marker);
            loadWeatherForTrail(trail, marker);
        });
        
        // Make label clickable too
        label.addListener('click', () => {
            infoWindow.open(map, marker);
            loadWeatherForTrail(trail, marker);
        });
        
        markers.push(marker);
        trailLabels.push(label);
    });
    
    // Update cluster
    markerCluster.clearMarkers();
    markerCluster.addMarkers(markers);
    
    // Update label visibility based on current zoom
    updateTrailLabelsVisibility();
}

function createMarkerHTML(difficulty) {
    const color = getDifficultyColor(difficulty);
    
    return `
        <div style="
            width: 16px;
            height: 16px;
            background-color: ${color};
            border: 2px solid white;
            border-radius: 50%;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        "></div>
    `;
}

function getDifficultyColor(difficulty) {
    const colors = {
        'Easy': '#28a745',      // Green
        'Moderate': '#ffc107',  // Yellow  
        'Hard': '#dc3545'       // Red
    };
    
    return colors[difficulty] || '#6c757d';
}

function createInfoWindowContent(trail) {
    const features = (trail.features || []).slice(0, 4).map(f => 
        `<span class="feature-tag">${f}</span>`
    ).join('');
    
    const keywords = (trail.review_keywords || []).slice(0, 3).join(', ');
    
    return `
        <div class="trail-info">
            <div class="trail-name">${trail.name}</div>
            <div class="trail-rating">${trail.stars}★ | ${trail.difficulty}</div>
            <div class="trail-details">
                ${trail.length ? `Length: ${trail.length}` : ''} 
                ${trail.duration ? `| Duration: ${trail.duration}` : ''}
            </div>
            <div class="trail-details">
                ${trail.elevation_gain ? `Elevation: ${trail.elevation_gain}` : ''}
                ${trail.dog_friendly ? ' | 🐕 Dog Friendly' : ''}
            </div>
            ${keywords ? `<div class="trail-details"><em>${keywords}</em></div>` : ''}
            <div class="trail-features">${features}</div>
            <div class="weather-info" id="weather-${trail.latitude}-${trail.longitude}">
                Loading weather...
            </div>
            ${trail.alltrails_url ? `
                <div style="margin-top: 8px;">
                    <a href="${trail.alltrails_url}" target="_blank" style="color: #28a745; font-weight: bold;">
                        View on AllTrails →
                    </a>
                </div>
            ` : ''}
        </div>
    `;
}

async function loadWeatherForTrail(trail, marker) {
    const key = `${trail.latitude},${trail.longitude}`;
    const tripDateValue = document.getElementById('trip-date').value;
    const tripDate = calculateDaysFromToday(tripDateValue);
    
    
    // Cache the full forecast under the location key
    const locationKey = `${trail.latitude},${trail.longitude}`;
    
    if (!weatherCache[locationKey]) {
        const forecast = await fetchWeatherForecast(trail.latitude, trail.longitude);
        if (forecast) {
            weatherCache[locationKey] = forecast;
        }
    }
    
    updateWeatherDisplay(trail, weatherCache[locationKey], tripDate, tripDateValue);
}

function updateWeatherDisplay(trail, forecast, tripDate, tripDateValue) {
    const weatherDiv = document.getElementById(`weather-${trail.latitude}-${trail.longitude}`);
    
    if (!weatherDiv) return;
    
    // Parse the date string manually to avoid timezone issues
    const selectedDate = parseLocalDate(tripDateValue);
    const dateText = formatDateForDisplay(selectedDate, tripDate);
    
    
    if (forecast && forecast.forecastDays && tripDate < forecast.forecastDays.length && forecast.forecastDays[tripDate]) {
        const dayForecast = forecast.forecastDays[tripDate];
        const temp = Math.round(dayForecast.maxTemperature?.degrees || 0);
        const condition = dayForecast.daytimeForecast?.weatherCondition?.description?.text || 'Unknown';
        const precipChance = dayForecast.daytimeForecast?.precipitation?.probability?.percent || 0;
        
        weatherDiv.innerHTML = `🌡️ ${dateText}: ${temp}°C, ${condition} ${precipChance > 30 ? `(${precipChance}% rain)` : ''}`;
    } else {
        weatherDiv.innerHTML = `🌡️ ${dateText}: Weather data unavailable (day ${tripDate}/${forecast?.forecastDays?.length || 0})`;
    }
}

function applyFilters() {
    const difficulty = document.getElementById('difficulty-filter').value;
    const maxLength = parseFloat(document.getElementById('length-filter').value);
    const maxElevation = parseFloat(document.getElementById('elevation-filter').value);
    const minRating = parseFloat(document.getElementById('rating-filter').value);
    
    filteredTrails = trails.filter(trail => {
        // Difficulty filter
        if (difficulty && trail.difficulty !== difficulty) return false;
        
        // Length filter
        if (maxLength < 20) {
            const trailLength = parseFloat(trail.length?.replace(/[^\d.]/g, '') || '999');
            if (trailLength > maxLength) return false;
        }
        
        // Elevation filter
        if (maxElevation < 5000) {
            const trailElevation = parseFloat(trail.elevation_gain?.replace(/[^\d.]/g, '') || '0');
            if (trailElevation > maxElevation) return false;
        }
        
        // Rating filter
        if (minRating > 1) {
            const trailRating = parseFloat(trail.stars || '0');
            if (trailRating < minRating) return false;
        }
        
        return true;
    });
    
    updateTrailStats();
    createMarkers();
}

function resetFilters() {
    document.getElementById('difficulty-filter').value = 'Easy';
    document.getElementById('length-filter').value = '20';
    document.getElementById('elevation-filter').value = '5000';
    document.getElementById('rating-filter').value = '4.7';
    setDefaultTripDate();
    updateLengthLabel();
    updateElevationLabel();
    updateRatingLabel();
    
    applyFilters();
}

function findTrailsNearMe() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition((position) => {
            const userLocation = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };
            
            map.setCenter(userLocation);
            map.setZoom(12);
            
            // Add user location marker
            const userMarkerElement = document.createElement('div');
            userMarkerElement.innerHTML = `
                <div style="
                    width: 20px;
                    height: 20px;
                    background-color: #4285f4;
                    border: 3px solid white;
                    border-radius: 50%;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.4);
                "></div>
            `;
            
            new google.maps.marker.AdvancedMarkerElement({
                position: userLocation,
                map: map,
                content: userMarkerElement,
                title: 'Your Location'
            });
        });
    } else {
        alert('Geolocation is not supported by this browser.');
    }
}

// URL parameter handling for filters
function updateURLParams() {
    const params = new URLSearchParams();
    
    const difficulty = document.getElementById('difficulty-filter').value;
    const maxLength = document.getElementById('length-filter').value;
    const minRating = document.getElementById('rating-filter').value;
    const tripDate = document.getElementById('trip-date').value;
    
    if (difficulty) params.set('difficulty', difficulty);
    if (maxLength && maxLength !== '20') params.set('maxLength', maxLength);
    if (minRating && minRating !== '1') params.set('minRating', minRating);
    if (tripDate) params.set('tripDate', tripDate);
    
    const newUrl = window.location.pathname + (params.toString() ? '?' + params.toString() : '');
    window.history.pushState({}, '', newUrl);
}

function loadURLParams() {
    const params = new URLSearchParams(window.location.search);
    
    if (params.get('difficulty')) document.getElementById('difficulty-filter').value = params.get('difficulty');
    if (params.get('maxLength')) document.getElementById('length-filter').value = params.get('maxLength');
    if (params.get('minRating')) document.getElementById('rating-filter').value = params.get('minRating');
    if (params.get('tripDate')) document.getElementById('trip-date').value = params.get('tripDate');
    
    // Update labels after loading URL params
    updateLengthLabel();
    updateElevationLabel();
    updateRatingLabel();
}

// Helper functions for date handling (keeping for backward compatibility)
function getUpcomingSaturday() {
    const today = new Date();
    const dayOfWeek = today.getDay(); // 0 = Sunday, 6 = Saturday
    
    if (dayOfWeek === 6) {
        // Today is Saturday
        return 0;
    } else if (dayOfWeek === 0) {
        // Today is Sunday, Saturday is 6 days away
        return 6;
    } else {
        // Monday-Friday, Saturday is (6 - dayOfWeek) days away
        return 6 - dayOfWeek;
    }
}

function updateLengthLabel() {
    const slider = document.getElementById('length-filter');
    const label = document.getElementById('length-label');
    const value = parseFloat(slider.value);
    
    if (value >= 20) {
        label.textContent = 'All lengths';
    } else {
        label.textContent = `≤ ${value} miles`;
    }
}

function updateElevationLabel() {
    const slider = document.getElementById('elevation-filter');
    const label = document.getElementById('elevation-label');
    const value = parseFloat(slider.value);
    
    if (value >= 5000) {
        label.textContent = 'All elevations';
    } else {
        label.textContent = `≤ ${value} ft`;
    }
}

function updateRatingLabel() {
    const slider = document.getElementById('rating-filter');
    const label = document.getElementById('rating-label');
    const value = parseFloat(slider.value);
    
    if (value <= 1) {
        label.textContent = 'All ratings';
    } else {
        label.textContent = `≥ ${value}★`;
    }
}

function setDefaultTripDate() {
    const today = new Date();
    const upcomingSaturday = new Date(today);
    const dayOfWeek = today.getDay(); // 0 = Sunday, 6 = Saturday
    
    if (dayOfWeek === 6) {
        // Today is Saturday, use today
        upcomingSaturday.setDate(today.getDate());
    } else if (dayOfWeek === 0) {
        // Today is Sunday, Saturday is 6 days away
        upcomingSaturday.setDate(today.getDate() + 6);
    } else {
        // Monday-Friday, Saturday is (6 - dayOfWeek) days away
        upcomingSaturday.setDate(today.getDate() + (6 - dayOfWeek));
    }
    
    // Format date as YYYY-MM-DD for the date input
    const formattedDate = upcomingSaturday.toISOString().split('T')[0];
    document.getElementById('trip-date').value = formattedDate;
}

function updateTrailLabelsVisibility() {
    const zoom = map.getZoom();
    const shouldShowLabels = zoom >= 12;
    
    if (!shouldShowLabels) {
        // Hide all labels when zoomed out
        trailLabels.forEach(label => label.setMap(null));
        return;
    }
    
    // Get current map bounds
    const bounds = map.getBounds();
    if (!bounds) return;
    
    // Filter trails that are visible in current bounds
    const visibleTrails = filteredTrails.filter((trail, index) => {
        const position = new google.maps.LatLng(trail.latitude, trail.longitude);
        return bounds.contains(position);
    });
    
    // Calculate density-based visibility
    const visibleLabelsIndices = calculateOptimalLabelVisibility(visibleTrails, zoom);
    
    // Show/hide labels based on density calculation
    trailLabels.forEach((label, index) => {
        const trail = filteredTrails[index];
        const isVisible = visibleLabelsIndices.has(index) && 
                         bounds.contains(new google.maps.LatLng(trail.latitude, trail.longitude));
        
        if (isVisible) {
            label.setMap(map);
        } else {
            label.setMap(null);
        }
    });
}

function calculateOptimalLabelVisibility(visibleTrails, zoom) {
    const visibleIndices = new Set();
    
    // Calculate minimum distance between labels based on zoom level
    const minDistance = getMinimumLabelDistance(zoom);
    
    // Sort trails by rating to prioritize better trails
    const sortedTrails = visibleTrails
        .map((trail, originalIndex) => ({
            trail,
            originalIndex: filteredTrails.indexOf(trail),
            rating: trail.stars || 0
        }))
        .sort((a, b) => b.rating - a.rating);
    
    // Greedy algorithm to select non-overlapping labels
    const selectedPositions = [];
    
    for (const trailInfo of sortedTrails) {
        const { trail, originalIndex } = trailInfo;
        const position = { lat: trail.latitude, lng: trail.longitude };
        
        // Check if this position is far enough from already selected ones
        const isFarEnough = selectedPositions.every(selectedPos => {
            const distance = calculateDistance(position, selectedPos);
            return distance >= minDistance;
        });
        
        if (isFarEnough) {
            selectedPositions.push(position);
            visibleIndices.add(originalIndex);
        }
    }
    
    return visibleIndices;
}

function getMinimumLabelDistance(zoom) {
    // Minimum distance in kilometers based on zoom level
    // Higher zoom = closer trails can show labels
    if (zoom >= 16) return 0.5;  // 500m
    if (zoom >= 14) return 1.0;  // 1km  
    if (zoom >= 13) return 2.0;  // 2km
    return 3.0; // 3km
}

function calculateDistance(pos1, pos2) {
    // Calculate distance in kilometers using Haversine formula
    const R = 6371; // Earth's radius in km
    const dLat = (pos2.lat - pos1.lat) * Math.PI / 180;
    const dLng = (pos2.lng - pos1.lng) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(pos1.lat * Math.PI / 180) * Math.cos(pos2.lat * Math.PI / 180) *
              Math.sin(dLng/2) * Math.sin(dLng/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

// Update all weather displays when date changes
function updateAllWeatherDisplays() {
    const tripDateValue = document.getElementById('trip-date').value;
    const tripDate = calculateDaysFromToday(tripDateValue);
    
    // Update all visible weather displays
    filteredTrails.forEach(trail => {
        const weatherDiv = document.getElementById(`weather-${trail.latitude}-${trail.longitude}`);
        if (weatherDiv) {
            const locationKey = `${trail.latitude},${trail.longitude}`;
            const forecast = weatherCache[locationKey];
            updateWeatherDisplay(trail, forecast, tripDate, tripDateValue);
        }
    });
}

function parseLocalDate(dateString) {
    if (!dateString) return null;
    
    // Parse the date string (YYYY-MM-DD) manually to avoid timezone issues
    const parts = dateString.split('-');
    if (parts.length !== 3) return null;
    
    const year = parseInt(parts[0]);
    const month = parseInt(parts[1]) - 1; // Month is 0-indexed
    const day = parseInt(parts[2]);
    
    return new Date(year, month, day);
}

function calculateDaysFromToday(dateString) {
    if (!dateString) return 0;
    
    const selectedDate = parseLocalDate(dateString);
    if (!selectedDate) return 0;
    
    const today = new Date();
    
    // Create new Date objects using local timezone
    const todayMidnight = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    const selectedMidnight = new Date(selectedDate.getFullYear(), selectedDate.getMonth(), selectedDate.getDate());
    
    const diffTime = selectedMidnight.getTime() - todayMidnight.getTime();
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    
    return Math.max(0, Math.min(9, diffDays)); // Weather API only has 10 days (0-9)
}

function formatDateForDisplay(date, daysFromToday) {
    if (!date || isNaN(date.getTime())) return 'Invalid Date';
    
    if (daysFromToday === 0) return 'Today';
    if (daysFromToday === 1) return 'Tomorrow';
    
    const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    const dayName = dayNames[date.getDay()];
    const month = monthNames[date.getMonth()];
    const day = date.getDate();
    
    return `${dayName}, ${month} ${day}`;
}

// Create temperature overlay circles from temperature data
function createTemperatureCircles(temperatureData) {
    temperatureData.forEach(dataPoint => {
        const temp = (dataPoint.weight * 25) + 10; // Convert back to Celsius
        const color = getTemperatureColor(temp);
        
        const circle = new google.maps.Circle({
            strokeColor: color,
            strokeOpacity: 0.8,
            strokeWeight: 2,
            fillColor: color,
            fillOpacity: 0.35,
            map: map,
            center: dataPoint.location,
            radius: 8000 // 8km radius
        });
        
        // Add click listener to show temperature
        const infoWindow = new google.maps.InfoWindow({
            content: `<div style="padding: 5px;"><strong>${Math.round(temp)}°C</strong><br>High temperature for selected date</div>`
        });
        
        circle.addListener('click', (event) => {
            infoWindow.setPosition(event.latLng);
            infoWindow.open(map);
        });
        
        temperatureCircles.push(circle);
    });
}

// Update temperature overlay button state
function updateTemperatureButtonState(hasData) {
    const button = document.getElementById('heatmap-toggle');
    
    if (hasData) {
        button.textContent = 'Hide Temperature Overlay';
        button.style.background = '#dc3545';
        
        // Add legend
        addTemperatureLegend();
    } else {
        button.textContent = 'Temperature Data Unavailable';
        button.style.background = '#6c757d';
        setTimeout(() => {
            button.textContent = 'Show Temperature Overlay';
            button.style.background = '#ff6b35';
        }, 2000);
    }
}

// Refresh temperature overlay if it's currently visible
function refreshTemperatureOverlay() {
    if (temperatureCircles.length > 0) {
        // Hide current overlay
        temperatureCircles.forEach(circle => circle.setMap(null));
        temperatureCircles = [];
        
        // Reload with new date
        const button = document.getElementById('heatmap-toggle');
        button.textContent = 'Loading Temperature Data...';
        button.style.background = '#6c757d';
        
        loadTemperatureHeatmap().then(temperatureData => {
            if (temperatureData.length > 0) {
                createTemperatureCircles(temperatureData);
            }
            updateTemperatureButtonState(temperatureData.length > 0);
        });
    }
}

// Temperature heatmap functions
async function loadTemperatureHeatmap() {
    const tripDateValue = document.getElementById('trip-date').value;
    const tripDate = calculateDaysFromToday(tripDateValue);
    const heatmapData = [];
    
    
    // Use existing trail locations and their cached weather data
    // This avoids making hundreds of new API calls
    filteredTrails.forEach(trail => {
        const locationKey = `${trail.latitude},${trail.longitude}`;
        const forecast = weatherCache[locationKey];
        
        if (forecast && forecast.forecastDays && forecast.forecastDays[tripDate]) {
            const temp = forecast.forecastDays[tripDate].maxTemperature?.degrees || 0;
            
            // Normalize temperature to 0-1 scale for heatmap intensity
            // Assuming temp range of 10-35°C for Bay Area
            const intensity = Math.max(0, Math.min(1, (temp - 10) / 25));
            
            heatmapData.push({
                location: new google.maps.LatLng(trail.latitude, trail.longitude),
                weight: intensity
            });
        }
    });
    
    // If we don't have enough data points, add a few strategic locations
    if (heatmapData.length < 20) {
        const strategicPoints = [
            {lat: 37.3097, lng: -122.2164}, // Russian Ridge Preserve
            {lat: 37.2705, lng: -122.0705}, // Big Basin Redwoods State Park
            {lat: 37.1714, lng: -122.2147}, // Big Basin Redwoods (additional coverage)
            {lat: 37.0522, lng: -122.0477}, // Santa Cruz area
            {lat: 37.4040, lng: -122.1853}, // Sveadal (Woodside area)
            {lat: 37.1833, lng: -121.5500}, // Henry Coe State Park
            {lat: 36.6002, lng: -121.8947}, // Monterey area
            {lat: 37.5155, lng: -121.9043}, // Mission Peak
            {lat: 37.2358, lng: -121.8064}, // Santa Teresa County Park
            {lat: 37.3319, lng: -121.6431}, // Joseph D. Grant County Park
            {lat: 37.0303, lng: -121.6797}, // Uvas Canyon County Park
            {lat: 37.3688, lng: -122.0363}, // Sunnyvale
            {lat: 37.5629, lng: -122.3255}, // San Mateo
            {lat: 37.4636, lng: -122.4286}, // Half Moon Bay
            {lat: 37.5074, lng: -122.2594}, // Redwood City
            {lat: 37.7749, lng: -122.4194}, // San Francisco
            {lat: 37.3382, lng: -121.8863}, // San Jose
            {lat: 37.6140, lng: -122.4869}, // Pacifica
            {lat: 37.8215, lng: -122.2592}  // Reinhardt Redwood Regional Park (Oakland Hills)
        ];
        
        for (const point of strategicPoints) {
            try {
                const locationKey = `${point.lat},${point.lng}`;
                
                if (!weatherCache[locationKey]) {
                    const forecast = await fetchWeatherForecast(point.lat, point.lng);
                    
                    if (forecast) {
                        weatherCache[locationKey] = forecast;
                    }
                }
                
                const forecast = weatherCache[locationKey];
                if (forecast && forecast.forecastDays && forecast.forecastDays[tripDate]) {
                    const temp = forecast.forecastDays[tripDate].maxTemperature?.degrees || 0;
                    const intensity = Math.max(0, Math.min(1, (temp - 10) / 25));
                    
                    heatmapData.push({
                        location: new google.maps.LatLng(point.lat, point.lng),
                        weight: intensity
                    });
                }
                
                // Delay between API calls
                await new Promise(resolve => setTimeout(resolve, 200));
                
            } catch (error) {
                console.log('Error fetching temperature for strategic point:', point);
            }
        }
    }
    
    return heatmapData;
}

function getTemperatureColor(temp) {
    // Temperature range: 10-35°C
    if (temp < 15) return '#0066ff'; // Cold - blue
    if (temp < 18) return '#0099ff'; // Cool - light blue
    if (temp < 21) return '#00ccff'; // Mild - cyan
    if (temp < 24) return '#00ff99'; // Comfortable - green
    if (temp < 27) return '#ffff00'; // Warm - yellow
    if (temp < 30) return '#ff9900'; // Hot - orange
    return '#ff3300'; // Very hot - red
}

function toggleHeatmap() {
    const button = document.getElementById('heatmap-toggle');
    
    if (temperatureCircles.length > 0) {
        // Hide temperature overlay
        temperatureCircles.forEach(circle => circle.setMap(null));
        temperatureCircles = [];
        button.textContent = 'Show Temperature Overlay';
        button.style.background = '#ff6b35';
    } else {
        // Show temperature overlay
        button.textContent = 'Loading Temperature Data...';
        button.style.background = '#6c757d';
        
        loadTemperatureHeatmap().then(temperatureData => {
            if (temperatureData.length > 0) {
                createTemperatureCircles(temperatureData);
            }
            updateTemperatureButtonState(temperatureData.length > 0);
        });
    }
}

function addTemperatureLegend() {
    // Only add legend if it doesn't already exist
    if (document.getElementById('temperature-legend')) {
        return;
    }
    
    const legend = document.createElement('div');
    legend.id = 'temperature-legend';
    legend.innerHTML = `
        <div style="background: white; padding: 10px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.3); margin: 10px;">
            <div style="font-weight: bold; margin-bottom: 5px;">Temperature (°C)</div>
            <div style="display: flex; align-items: center; margin: 2px 0;">
                <div style="width: 20px; height: 15px; background: #0066ff; margin-right: 5px;"></div>
                <span style="font-size: 12px;">< 15°C</span>
            </div>
            <div style="display: flex; align-items: center; margin: 2px 0;">
                <div style="width: 20px; height: 15px; background: #0099ff; margin-right: 5px;"></div>
                <span style="font-size: 12px;">15-18°C</span>
            </div>
            <div style="display: flex; align-items: center; margin: 2px 0;">
                <div style="width: 20px; height: 15px; background: #00ccff; margin-right: 5px;"></div>
                <span style="font-size: 12px;">18-21°C</span>
            </div>
            <div style="display: flex; align-items: center; margin: 2px 0;">
                <div style="width: 20px; height: 15px; background: #00ff99; margin-right: 5px;"></div>
                <span style="font-size: 12px;">21-24°C</span>
            </div>
            <div style="display: flex; align-items: center; margin: 2px 0;">
                <div style="width: 20px; height: 15px; background: #ffff00; margin-right: 5px;"></div>
                <span style="font-size: 12px;">24-27°C</span>
            </div>
            <div style="display: flex; align-items: center; margin: 2px 0;">  
                <div style="width: 20px; height: 15px; background: #ff9900; margin-right: 5px;"></div>
                <span style="font-size: 12px;">27-30°C</span>
            </div>
            <div style="display: flex; align-items: center; margin: 2px 0;">
                <div style="width: 20px; height: 15px; background: #ff3300; margin-right: 5px;"></div>
                <span style="font-size: 12px;">> 30°C</span>
            </div>
        </div>
    `;
    
    map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(legend);
}

// Load URL parameters on page load
window.addEventListener('load', loadURLParams);
</script>

<!-- Load Google Maps API with MarkerClusterer -->
<script src="https://unpkg.com/@googlemaps/markerclusterer/dist/index.min.js"></script>
<script async defer 
        src="https://maps.googleapis.com/maps/api/js?key={{ site.google_api.maps_key }}&libraries=marker&callback=initMap">
</script>


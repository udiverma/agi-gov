// Sample US Airport Data (Latitude, Longitude, Name)
// A more comprehensive dataset would be needed for a full implementation.
const airports = [
    { lat: 34.0522, lng: -118.2437, name: 'LAX', city: 'Los Angeles' },
    { lat: 40.7128, lng: -74.0060, name: 'JFK', city: 'New York' },
    { lat: 41.8781, lng: -87.6298, name: 'ORD', city: 'Chicago' },
    { lat: 29.7604, lng: -95.3698, name: 'IAH', city: 'Houston' },
    { lat: 33.4484, lng: -112.0740, name: 'PHX', city: 'Phoenix' },
    { lat: 39.9526, lng: -75.1652, name: 'PHL', city: 'Philadelphia' },
    { lat: 29.4241, lng: -98.4936, name: 'SAT', city: 'San Antonio' },
    { lat: 32.7767, lng: -96.7970, name: 'DFW', city: 'Dallas' },
    { lat: 37.7749, lng: -122.4194, name: 'SFO', city: 'San Francisco' },
    { lat: 39.7392, lng: -104.9903, name: 'DEN', city: 'Denver' },
    { lat: 47.6062, lng: -122.3321, name: 'SEA', city: 'Seattle' },
    { lat: 38.9072, lng: -77.0369, name: 'DCA', city: 'Washington D.C.' },
    { lat: 42.3601, lng: -71.0589, name: 'BOS', city: 'Boston' },
    { lat: 33.7490, lng: -84.3880, name: 'ATL', city: 'Atlanta' },
    { lat: 25.7617, lng: -80.1918, name: 'MIA', city: 'Miami' },
];

let arcsData = [];
let affectedLocations = [];
const affectedListElement = document.getElementById('affected-list');
const startButton = document.getElementById('start-simulation');
const pauseButton = document.getElementById('pause-simulation');
const resumeButton = document.getElementById('resume-simulation');
const resetButton = document.getElementById('reset-simulation');
const dashboardElement = document.getElementById('dashboard');
const toggleButton = document.getElementById('toggle-dashboard');

let simulationIntervalId = null;
let currentAirport = null; 
let currentIndex = -1;   
let simulationRunning = false;
let simulationPaused = false;

// Initialize Globe
const myGlobe = Globe()
    (document.getElementById('globeViz'))
    .globeImageUrl('//unpkg.com/three-globe/example/img/earth-night.jpg')
    .backgroundImageUrl('//unpkg.com/three-globe/example/img/night-sky.png')
    .pointsData(airports)
    .pointAltitude('size')
    .pointColor('color')
    .pointLabel(d => `${d.name} (${d.city})`)
    .pointRadius(0.15) 
    .arcsData(arcsData)
    .arcColor('color')
    .arcDashLength(0.4)
    .arcDashGap(0.1)
    .arcDashAnimateTime(1000)
    .arcStroke(0.3);

// Initial globe settings
myGlobe.pointOfView({ lat: 39.6, lng: -98.5, altitude: 1.5 }); 

// --- Simulation Control Functions ---

function startSimulation() {
    if (simulationRunning) return; 

    console.log("Starting simulation...");
    resetSimulationState(); 

    if (airports.length === 0) return;

    // Initial state
    currentIndex = 0;
    currentAirport = airports[currentIndex];
    affectedLocations.push(currentAirport);
    addAffectedToList(currentAirport);
    updateGlobePoints();

    simulationRunning = true;
    simulationPaused = false;
    updateButtonStates();

    runSimulationStep(); 
    simulationIntervalId = setInterval(runSimulationStep, 3000); 
}

function pauseSimulation() {
    if (!simulationRunning || simulationPaused) return;

    console.log("Simulation paused.");
    clearInterval(simulationIntervalId);
    simulationIntervalId = null;
    simulationPaused = true;
    updateButtonStates();
}

function resumeSimulation() {
    if (!simulationRunning || !simulationPaused) return;

    console.log("Simulation resumed.");
    simulationPaused = false;
    updateButtonStates();
    simulationIntervalId = setInterval(runSimulationStep, 3000); 
}

function resetSimulation() {
    console.log("Simulation reset.");
    pauseSimulation(); 
    resetSimulationState();
    updateGlobePoints(); 
    myGlobe.arcsData(arcsData); 
    affectedListElement.innerHTML = ''; 
    simulationRunning = false;
    simulationPaused = false;
    updateButtonStates();
}

// --- Helper Functions ---

function resetSimulationState() {
    arcsData = [];
    affectedLocations = [];
    currentAirport = null;
    currentIndex = -1;
    if (simulationIntervalId) {
        clearInterval(simulationIntervalId);
        simulationIntervalId = null;
    }
}

function runSimulationStep() {
    if (affectedLocations.length >= airports.length) {
        console.log("Simulation complete.");
        pauseSimulation(); 
        simulationRunning = false; 
        updateButtonStates(); 
        return;
    }

    // Find the next *unaffected* airport
    let nextAirport = null;
    let nextIndex = (currentIndex + 1) % airports.length;
    let initialNextIndex = nextIndex; 

    while (affectedLocations.some(a => a.name === airports[nextIndex].name)) {
        nextIndex = (nextIndex + 1) % airports.length;
        // Safety break if all are somehow affected (should not happen with the check above)
        if (nextIndex === initialNextIndex) {
             console.error("Error finding next unaffected airport - looped back.");
             pauseSimulation();
             simulationRunning = false;
             updateButtonStates();
             return;
        }
    }
    nextAirport = airports[nextIndex];

    // Add arc from current to next
    arcsData.push({
        startLat: currentAirport.lat,
        startLng: currentAirport.lng,
        endLat: nextAirport.lat,
        endLng: nextAirport.lng,
        color: 'yellow' // Change arc color to yellow
    });

    // Add next airport to affected list
    affectedLocations.push(nextAirport);
    addAffectedToList(nextAirport);

    // Update globe data
    updateGlobePoints();
    myGlobe.arcsData(arcsData);

    // Move to the next airport for the next iteration
    currentAirport = nextAirport;
    currentIndex = nextIndex;
}

function updateButtonStates() {
    startButton.style.display = (!simulationRunning && !simulationPaused) ? 'block' : 'none';
    pauseButton.style.display = (simulationRunning && !simulationPaused) ? 'block' : 'none';
    resumeButton.style.display = (simulationRunning && simulationPaused) ? 'block' : 'none';
    resetButton.style.display = (simulationRunning || simulationPaused) ? 'block' : 'none'; 
}

function addAffectedToList(airport) {
    const listItem = document.createElement('li');
    listItem.textContent = `${airport.name} (${airport.city})`;
    affectedListElement.appendChild(listItem);
}

function updateGlobePoints() {
    const updatedPoints = airports.map(apt => ({
        ...apt,
        size: affectedLocations.some(a => a.name === apt.name) ? 0.08 : 0.01, 
        color: affectedLocations.some(a => a.name === apt.name) ? 'red' : 'yellow' 
    }));
    myGlobe.pointsData(updatedPoints);
}

// --- Event Listeners ---

startButton.addEventListener('click', startSimulation);
pauseButton.addEventListener('click', pauseSimulation);
resumeButton.addEventListener('click', resumeSimulation);
resetButton.addEventListener('click', resetSimulation);

toggleButton.addEventListener('click', () => {
    dashboardElement.classList.toggle('open');
});

// --- Initial Setup ---
updateGlobePoints(); 
updateButtonStates(); 

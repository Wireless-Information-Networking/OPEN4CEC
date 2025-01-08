// Create constants for the form and input elements
const pvFormEl = document.getElementById("user-form");
const countryInputEl = document.getElementById("country-select");
const latInputEl = document.getElementById("lat");
const lngInputEl = document.getElementById("lon");
const altInputEl = document.getElementById("alt");
const timezoneInputEl = document.getElementById("time-zone-input");
const surfaceInputEl = document.getElementById("surface");
const efficiencyInputEl = document.getElementById("efficiency");
const feeInputEl = document.getElementById("fee-type-input");
const fixedvalueInputEl = document.getElementById("fixed-value");

function showHome() {
    var mainPageElements = document.getElementsByClassName("main-page");
    for (var i = 0; i < mainPageElements.length; i++) {
        mainPageElements[i].style.display = "none";
    }
    var Home = document.getElementById("home");
    Home.style.display = "block";
}

function showUser() {
    var mainPageElements = document.getElementsByClassName("main-page");
    for (var i = 0; i < mainPageElements.length; i++) {
        mainPageElements[i].style.display = "none";
    }
    var User = document.getElementById("user");
    User.style.display = "block";
}

function getCoords() {
    if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(success, error, {
            enableHighAccuracy: true,
            timeout: 5000,
            maximumAge: 0
        });
    } else {
        alert("Geolocation is not supported by your browser.");
    }
}

function success(position) {
    latInputEl.value = position.coords.latitude.toFixed(2);
    lngInputEl.value = position.coords.longitude.toFixed(2);
}

function error(err) {
    console.warn(`ERROR(${err.code}): ${err.message}`);
}


async function getWeather() {
    // Get the input values
    const latitude = latInputEl.value.trim();
    const longitude = lngInputEl.value.trim();
    const timezone = timezoneInputEl.value;

    // Input validation
    if (!latitude || !longitude || !timezone) {
        PVGenCard.innerHTML = "<p class='error'>Position and time zone required. Please complete user's form.</p>";
        return;
    }

    // Fetch weather data from the server
    fetch('/weather', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ latitude: latitude, longitude: longitude, timezone: timezone })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Error:', data.error);
        } else {
            const weatherArray = data.images;

            // Clear previous content
            const locationCard = document.getElementById('weather-card');
            locationCard.innerHTML = '';
            locationCard.style.display = 'flex'; // Set parent container to flex
            locationCard.style.justifyContent = 'center'; // Center the scrollContainer horizontally
            locationCard.style.overflowX = 'hidden'; 

            // Create a container for horizontal scrolling
            const scrollContainer = document.createElement('div');
            scrollContainer.style.display = 'flex'; // Flex container to align items in a row
            scrollContainer.style.overflowX = 'auto'; // Enable horizontal scrolling
            scrollContainer.style.whiteSpace = 'nowrap'; // Prevent items from wrapping
            scrollContainer.style.padding = '5px 10px 5px'; // Optional: padding for a better look

            // Loop through weatherArray and append images with hours
            weatherArray.forEach((weather, index) => {
                const weatherItem = document.createElement('div');
                weatherItem.style.textAlign = 'center'; // Center the image and hour text
                weatherItem.style.minWidth = '60px'; // Ensure consistent item width
                weatherItem.style.marginRight = '0px'; // Add margin between items

                const img = document.createElement('img');
                img.src = `assets/images/weather-icons/${weather}.svg`; // Construct image path
                img.alt = weather;  // Use weather string as alt text
                img.style.width = '50px'; // Example styling

                // Create hour text below the image
                const hourText = document.createElement('p');
                hourText.textContent = `${index}:00`; // Convert index to hour (00:00 to 23:00)
                hourText.style.marginTop = '3px';
                hourText.style.marginBottom = '3px' // Add margin for spacing
                hourText.style.textAlign = 'center'; // Center the hour text

                // Append image and hour to the weather item
                weatherItem.appendChild(img);
                weatherItem.appendChild(hourText);

                // Append the weather item to the scroll container
                scrollContainer.appendChild(weatherItem);
            });

            // Append the scroll container to the locationCard
            locationCard.appendChild(scrollContainer);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}


async function getPrices() {
    const country = document.getElementById('country-select').value;
    console.log(country);
    
    fetch('/day_ahead_prices', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ country: country })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Error:', data.error);
        } else {
            const priceCard = document.getElementById('price-card');
            priceCard.innerHTML = '';  // Clear previous content

            // Prepare data for the plot
            const labels = [];  // X-axis labels (00:00 to 23:00)
            const prices = [];  // Y-axis data (euros/MWh)
            
            data.data.forEach(point => {
                // Assuming point.position is from 1 to 24 (representing each hour)
                const hour = (point.position - 1).toString().padStart(2, '0');  // Format hour as "HH"
                labels.push(`${hour}:00`);  // X-axis label (hour in "HH:00" format)
                prices.push(point['price.amount']);  // Y-axis value (euros/MWh)
            });

            // Create a canvas for the chart
            const canvas = document.createElement('canvas');
            priceCard.appendChild(canvas);
            priceCard.style.height = '30%'

            priceCard.style.display = 'flex';

            // Set styles to ensure the canvas grows/shrinks with the window
            canvas.style.width = '100%';
            canvas.style.width = priceCard.offsetWidth + 'px';
            canvas.style.height = priceCard.offsetHeight + 'px';

            // Update canvas height on window resize
            window.addEventListener('resize', () => {
                canvas.style.width = priceCard.offsetWidth + 'px';
                canvas.style.height = priceCard.offsetHeight + 'px';
            });

            // Create the chart using Chart.js
            new Chart(canvas, {
                type: 'line',  // Line chart
                data: {
                    labels: labels,  // X-axis labels (hours)
                    datasets: [{
                        label: 'Price (€/MWh)',
                        data: prices,  // Y-axis data (prices)
                        borderColor: 'rgba(75, 192, 192, 1)',  // Line color
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',  // Fill color under the line
                        fill: true,  // Enable fill
                        tension: 0.3,  // Smooth the line
                    }]
                },
                options: {
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Hour (00:00 - 23:00)'  // X-axis title
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Price (€/MWh)'  // Y-axis title
                            },
                            beginAtZero: true  // Ensure Y-axis starts at 0
                        }
                    }
                }
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

async function getGenType(){
    const country = document.getElementById('country-select').value;
    console.log(country);
    
    fetch('/actual_gen_type', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ country: country })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Error:', data.error);
        } else {
            const genTypeCard = document.getElementById('country-generation-card');
            genTypeCard.innerHTML = '';  // Clear previous content
            
            // Fixed color mapping for generation types
            const colorMapping = {
                // Green (0 CO2 emissions)
                'Hydro Pumped Storage': 'rgba(0, 128, 0, 1)',  // Green 1
                'Hydro Run-of-river and poundage': 'rgba(34, 139, 34, 1)',  // Green 2
                'Hydro Water Reservoir': 'rgba(60, 179, 113, 1)',  // Green 4
                'Marine': 'rgba(46, 139, 87, 1)',  // Green 5
                'Nuclear': 'rgba(50, 205, 50, 1)',  // Green 6
                'Other renewable': 'rgba(144, 238, 144, 1)',  // Green 8
                'Solar': 'rgba(127, 255, 0, 1)',  // Green 10
                'Wind Offshore': 'rgba(152, 251, 152, 1)',  // Green 9
                'Wind Onshore': 'rgba(0, 255, 127, 1)',  // Green 3
            
                // Yellow (moderate CO2 emissions)
                'Fossil Coal-derived gas': 'rgba(255, 255, 153, 1)',  // Light Yellow
                'Fossil Oil': 'rgba(255, 223, 0, 1)',  // Mustard Yellow
                'Fossil Oil shale': 'rgba(255, 255, 102, 1)',  // Yellow
                'Fossil Peat': 'rgba(255, 239, 0, 1)',  // Bright Yellow
                'Waste': 'rgba(255, 255, 153, 1)',  // Pale Yellow
                'Geothermal': 'rgba(255, 250, 205, 1)',  // Lemon Chiffon
                'Other': 'rgba(255, 255, 204, 1)',  // Light Pale Yellow
            
                // Red (high CO2 emissions)
                'Biomass': 'rgba(255, 99, 71, 1)',  // Tomato Red
                'Fossil Brown coal/Lignite': 'rgba(178, 34, 34, 1)',  // Firebrick Red
                'Fossil Gas': 'rgba(255, 69, 0, 1)',  // Orange Red
                'Fossil Hard coal': 'rgba(220, 20, 60, 1)',  // Crimson Red
                'Fossil Oil shale': 'rgba(255, 99, 132, 1)',  // Hot Pink Red
            };
            
            // Prepare data for the pie chart and calculate the green percentage
            const labels = [];  // Generation types (e.g., solar, wind)
            const values = [];  // Corresponding generation values (e.g., MWh)
            const backgroundColors = [];  // Colors for each section of the pie chart

            let totalGeneration = 0;  // Total generation
            let greenGeneration = 0;  // Total green (0 CO2 emissions) generation

            const greenSources = [
                'Hydro Pumped Storage',
                'Hydro Run-of-river and poundage',
                'Hydro Water Reservoir',
                'Marine',
                'Nuclear',
                'Other renewable',
                'Solar',
                'Wind Offshore',
                'Wind Onshore'
            ];

            const generationData = data.data;
            Object.entries(generationData).forEach(([type, value]) => {
                labels.push(type);  // Add the type to labels
                values.push(value);  // Add the value to the dataset
                totalGeneration += value;  // Add to the total generation

                // Check if the source is green and add to greenGeneration if so
                if (greenSources.includes(type)) {
                    greenGeneration += value;
                }

                // Use the color from the colorMapping or default to grey if type is missing in mapping
                const color = colorMapping[type] || 'rgba(201, 203, 207, 1)';  // Grey for unknown types
                backgroundColors.push(color);
            });

            // Calculate the percentage of green energy
            const greenPercentage = (greenGeneration / totalGeneration) * 100;

            // Display info
            const infoDiv = document.createElement('div');
            infoDiv.id = 'info-container';

            const greenPercentageDiv = document.createElement('div');
            greenPercentageDiv.textContent = `Green energy: ${greenPercentage.toFixed(2)}%`;
            greenPercentageDiv.id ='tanpercent-green';

            const co2Div = document.createElement('div');
            co2Div.textContent = `CO2 impact in last hour: ${data.co2.toFixed(2)} Tonnes`;
            co2Div.id = 'co2-impact';


            // Create a canvas for the pie chart
            const canvas = document.createElement('canvas');
            const container = document.createElement('div');
            container.id = 'gen-type-container'
            genTypeCard.appendChild(container);
            container.appendChild(canvas);

            infoDiv.appendChild(greenPercentageDiv);
            infoDiv.appendChild(co2Div);
            genTypeCard.appendChild(infoDiv);

            // Create the pie chart using Chart.js
            new Chart(canvas, {
                type: 'pie',  // Pie chart
                data: {
                    labels: labels,  // Generation types (e.g., solar, wind)
                    datasets: [{
                        data: values,  // Generation values (e.g., MWh)
                        backgroundColor: backgroundColors,  // Fixed colors for the pie chart sections
                    }]
                },
                options: {
                    responsive: true,  // Make the chart responsive
                    plugins: {
                        legend: {
                            display: false,
                            position: 'bottom'  // Show the legend at the bottom
                        },
                        tooltip: {
                            callbacks: {
                                label: function(tooltipItem) {
                                    const value = tooltipItem.raw;
                                    return `${tooltipItem.label}: ${value} MWh`;
                                }
                            }
                        }
                    }
                }
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

async function getPVGen() {
    // Get the input values
    const latitude = latInputEl.value.trim();
    const longitude = lngInputEl.value.trim();
    const altitude = altInputEl.value.trim();
    const timezone = timezoneInputEl.value.trim();
    const surface = surfaceInputEl.value.trim();
    const efficiency = efficiencyInputEl.value.trim();
    const PVGenCard = document.getElementById('PV-generation-card');

    // Input validation
    if (!latitude || !longitude || !altitude || !timezone || !surface || !efficiency) {
        PVGenCard.innerHTML = "<p class='error'>All fields are required. Please complete the form.</p>";
        return;
    }

    try {
        const response = await fetch('/PVgen', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                latitude: latitude,
                longitude: longitude,
                altitude: altitude,
                timezone: timezone,
                surface: surface,
                efficiency: efficiency
            })
        });

        const data = await response.json();

        // Check for errors in the response
        if (data.error) {
            PVGenCard.innerHTML = `<p class='error'>Error: ${data.error}</p>`;
            return;
        }

        // Extract the power data
        const powerArray = data.power;

        // Clear previous content and create a canvas for the chart
        PVGenCard.innerHTML = ``;
        const canvas = document.createElement('canvas');
        PVGenCard.appendChild(canvas);

        // Prepare data for the line chart
        const hours = Array.from({ length: 24 }, (_, i) => `${String(i).padStart(2, '0')}:00`);  // Format hours as HH:00
        const powerData = powerArray.map(powerValue => powerValue.toFixed(2));

        // Create the line chart using Chart.js
        new Chart(canvas, {
            type: 'line',
            data: {
                labels: hours,  // Hours of the day in "HH:00" format
                datasets: [{
                    label: 'Energy Generated (Wh)',
                    data: powerData,  // Power values for each hour
                    borderColor: 'rgba(255, 165, 0, 1)',  // Orange line color
                    backgroundColor: 'rgba(255, 255, 0, 0.3)',  // Yellow fill color (transparent)
                    borderWidth: 2,  // Line width
                    fill: true  // Fill under the line
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Time of Day'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Power (Wh)'
                        },
                        beginAtZero: true  // Start y-axis at 0
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(tooltipItem) {
                                return `${tooltipItem.raw} Wh`;
                            }
                        }
                    }
                }
            }
        });

    } catch (error) {
        // Handle any errors that occur during the fetch
        console.error('Fetch error:', error);
        PVGenCard.innerHTML = "<p class='error'>Failed to fetch data. Please try again later.</p>";
    }
}

async function getSell() {
    // Get the input values
    const latitude = latInputEl.value.trim();
    const longitude = lngInputEl.value.trim();
    const altitude = altInputEl.value.trim();
    const timezone = timezoneInputEl.value.trim();
    const surface = surfaceInputEl.value.trim();
    const efficiency = efficiencyInputEl.value.trim();
    const fee = feeInputEl.value.trim();
    const fixed_price = fixedvalueInputEl.value.trim();
    const country = document.getElementById('country-select').value;

    const PVGenCard = document.getElementById('sell-card');

    console.log(fee)
    // Input validation
    if (!latitude || !longitude || !altitude || !timezone || !surface || !efficiency || !fee) {
        PVGenCard.innerHTML = "<p class='error'>All fields are required. Please complete the form.</p>";
        return;
    }

    try {
        const response = await fetch('/sell', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                latitude: latitude,
                longitude: longitude,
                altitude: altitude,
                timezone: timezone,
                surface: surface,
                efficiency: efficiency,
                fee: fee,
                country: country,
                fixed_price: fixed_price
            })
        });

        const data = await response.json();

        // Check for errors in the response
        if (data.error) {
            PVGenCard.innerHTML = `<p class='error'>Error: ${data.error}</p>`;
            return;
        }
        console.log(data);
        // Extract the power data
        const powerArray = data.sell;

        // Clear previous content and create a canvas for the chart
        PVGenCard.innerHTML = ``;
        const canvas = document.createElement('canvas');
        PVGenCard.appendChild(canvas);

        // Prepare data for the line chart
        const hours = Array.from({ length: 24 }, (_, i) => `${String(i).padStart(2, '0')}:00`);  // Format hours as HH:00
        const powerData = powerArray.map(powerValue => powerValue.toFixed(2));

        // Create the line chart using Chart.js
        new Chart(canvas, {
            type: 'line',
            data: {
                labels: hours,  // Hours of the day in "HH:00" format
                datasets: [{
                    label: 'Selling prices for your PV installation (€)',
                    data: powerData,  // Power values for each hour
                    borderColor: 'rgba(0, 128, 0, 1)',  // Green line color
                    backgroundColor: 'rgba(144, 238, 144, 0.3)',  // Light green fill color (transparent)

                    borderWidth: 2,  // Line width
                    fill: true  // Fill under the line
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Time of Day'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Money (€)'
                        },
                        beginAtZero: true  // Start y-axis at 0
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(tooltipItem) {
                                return `${tooltipItem.raw} €`;
                            }
                        }
                    }
                }
            }
        });

    } catch (error) {
        // Handle any errors that occur during the fetch
        console.error('Fetch error:', error);
        PVGenCard.innerHTML = "<p class='error'>Failed to fetch data. Please try again later.</p>";
    }
}

async function getAdvice() {
    const container = document.getElementById('advice-graph-container');
    container.innerHTML = '';

    const canvas = document.createElement('canvas');
    canvas.style.height = '100%';
    container.appendChild(canvas);

    const labels = ['💰', '🌍', '⚡', '🔋'];
    const values0 = [0, 0, 0, 0];
    const values1 = [8, 9, 10, 5];
    const values2 = [6, 5, 7, 10];
    const values3 = [8, 10, 3, 2];
    const values4 = [2, 6, 3, 4];

    const tooltipsText = {
        '💰': 'Money expences score',
        '🌍': 'CO2 impact score',
        '⚡': 'Energy available score',
        '🔋': 'Energy stored score'
    };

    const chart = new Chart(canvas, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Advice score [1-10]',
                data: values0,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: true,
            scales: {
                x: {
                    display: true,
                },
                y: {
                    display: true,
                    beginAtZero: true,
                    min: 0,
                    max: 10,
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const label = context.label;
                            const value = context.raw;
                            const tooltipMessage = tooltipsText[label] || '';
                            return `${tooltipMessage}: ${value}`;
                        }
                    }
                }
            }
        }
    });

    function updateChartData(selectedValues) {
        chart.data.datasets[0].data = selectedValues;
        chart.update();
    }

    document.getElementById('value-1').addEventListener('change', () => updateChartData(values1));
    document.getElementById('value-2').addEventListener('change', () => updateChartData(values2));
    document.getElementById('value-3').addEventListener('change', () => updateChartData(values3));
    document.getElementById('value-4').addEventListener('change', () => updateChartData(values4));
}

getAdvice();

// Key to access stored data in localStorage
const STORAGE_KEY = "pvData";

// Load stored data on page load and populate the form fields
window.onload = function () {
    const storedData = getStoredPVData();
  
    if (storedData) {
      countryInputEl.value = storedData.country || "";
      latInputEl.value = storedData.latitude || "";
      lngInputEl.value = storedData.longitude || "";
      altInputEl.value = storedData.altitude || "";
      timezoneInputEl.value = storedData.timeZone || "";
      surfaceInputEl.value = storedData.surface || "";
      efficiencyInputEl.value = storedData.efficiency || "";
      feeInputEl.value = storedData.feetype || "";
      fixedvalueInputEl.value = storedData.fixedvalue || "";
    }

    if (validatePVForm(latInputEl.value, lngInputEl.value, surfaceInputEl.value, efficiencyInputEl.value))
    {
        getWeather();
        getPrices();
        getGenType();
        getPVGen();
        getSell();
        getAdvice();
    }
    else{
        showUser();
        alert("Please complete user's form");
    }
  };

// Add a submit event listener for the form
pvFormEl.addEventListener("submit", (event) => {
    event.preventDefault(); // Prevent the form from submitting to the server
  
    // Collect values from the form fields
    const country = countryInputEl.value;
    const latitude = latInputEl.value;
    const longitude = lngInputEl.value;
    const altitude = altInputEl.value;
    const timeZone = timezoneInputEl.value;
    const surface = surfaceInputEl.value;
    const efficiency = efficiencyInputEl.value;
    const feetype = feeInputEl.value;
    const fixedvalue = fixedvalueInputEl.value


  
    // Validate form data
    if (validatePVForm(latitude, longitude, surface, efficiency)) {
      // Store the form data in localStorage, overwriting the previous values
      storePVData({
        country,
        latitude,
        longitude,
        altitude,
        timeZone,
        surface,
        efficiency,
        feetype,
        fixedvalue
      });
  
      // Optionally: Notify the user that the data was saved
      alert("Data saved successfully!");
      location.reload();
  
    } else {
      alert("Invalid input values. Please check your entries.");
    }
  });
  
  // Form validation function
  function validatePVForm(latitude, longitude, surface, efficiency) {
    return (
      latitude && longitude && surface > 0 && efficiency > 0
    );
  }
  
  // Store form data in localStorage (overwrite existing data)
  function storePVData(pvData) {
    // Store the updated data back into localStorage
    localStorage.setItem(STORAGE_KEY, JSON.stringify(pvData));
  }
  
  // Retrieve stored data from localStorage
  function getStoredPVData() {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : null;
  }

  const card = document.getElementById('siri-card');
  card.addEventListener('click', function() {
    const inner = this.querySelector('.flip-card-inner');
    inner.style.transform = inner.style.transform === 'rotateY(180deg)' ? 'rotateY(0)' : 'rotateY(180deg)';
  });
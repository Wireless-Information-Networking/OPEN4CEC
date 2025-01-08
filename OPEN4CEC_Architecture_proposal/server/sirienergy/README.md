# UABENERGY

## Introduction

Progresive Web App that allows to get usefull information to take the best decisions in your energy usage.

## Structure

UABENERGY  
│  
├── docker-compose.yaml (to run container with Docker Compose)  
├── Dockerfile (to build the Docker image)  
├── .env (stores environment variables)  
├── app.py (main backend file that initializes the application)  
├── commands.py (additional commands or functions for the app)  
├── services/  
│   ├── entsoe_aux.py (auxiliar functions for ENTSO-E)  
│   ├── entsoe_gentype.py (functions to obtain generation by generation type)  
│   ├── prices.py (functions to obtain electricity prices)  
│   └── weather.py (functions to obtain wheather on certain location)  
├── static/  
│   ├── assets/  
│   │   ├── images/  
│   │   │   ├── icons/ (contains icons used in the app interface)  
│   │   │   ├── nav-icons/ (contains icons used in the navegation tool)  
│   │   │   └── weather-icons/ (icons representing weather conditions)  
│   ├── css/  
│   │   └── style.css (styles for the frontend interface)  
│   ├── js/  
│   │   └── app.js (JavaScript for frontend functionality)  
│   ├── index.html (HTML template for the frontend interface)  
│   └── manifest.json (configurations for the progressive web app)  
└── requirements.txt (Python dependencies for the project)  

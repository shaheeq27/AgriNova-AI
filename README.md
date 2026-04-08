**🌱 Dynamic Crop Recommendation System**

An intelligent full-stack web application that recommends the most suitable crops using Machine Learning + climate analysis + soil & seasonal inputs.


**🚀 Overview**

This system helps farmers and agricultural planners choose optimal crops based on:
	•	🌍 Location (city)
	•	🌱 Soil type
	•	📅 Season
	•	🌦 Climate data (temperature, rainfall, humidity)

It combines Machine Learning predictions with a rule-based scoring system to provide accurate and reliable recommendations.


**✨ Key Features**

	•	🤖 Machine Learning Model (Random Forest)
Predicts top 3 crops with confidence scores
	•	📊 Hybrid Recommendation System
Combines ML predictions + scoring algorithm
	•	🌦 2-Year Climate Analysis
Uses historical weather data (temperature, rainfall, humidity)
	•	🧠 Input Normalization
Handles flexible user inputs (e.g., “loamy soil”, “Loamy”, etc.)
	•	🧪 Fertilizer Recommendation
Suggests fertilizer type, timing, and quantity based on farm size
	•	⚡ PostgreSQL Caching
Stores weather data to reduce API calls and improve performance
	•	🎨 Modern UI/UX
	•	Animated landing page
	•	AI prediction cards
	•	Confidence progress bars



**🏗️ System Architecture**

User Input (City, Soil, Season)
        ↓
Weather API (2-Year Historical Data)
        ↓
Data Processing & Normalization
        ↓
Machine Learning Model (Random Forest)
        ↓
Top 3 Predictions + Confidence Scores
        ↓
Rule-Based Scoring System
        ↓
Final Recommendations + Fertilizer Guidance
        ↓
Frontend Visualization (Cards + UI)


**🛠️ Tech Stack**

🔙 Backend
	•	Python
	•	Flask

🤖 Machine Learning
	•	Scikit-learn
	•	Pandas
	•	NumPy

🗄️ Database
	•	PostgreSQL

🌐 Frontend
	•	HTML
	•	CSS
	•	JavaScript

🌦 APIs
	•	Open-Meteo API (Weather Data)


**▶️ How to Run Locally**

# Clone repository
git clone https://github.com/your-username/Dynamic-Crop-Recommendation-System.git

# Go to project folder
cd Dynamic-Crop-Recommendation-System

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py

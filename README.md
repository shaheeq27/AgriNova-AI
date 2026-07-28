# 🌱 AgriNova – AI Crop Intelligence Platform

AgriNova is an intelligent full-stack web application that helps farmers and agricultural planners identify the most suitable crops using **Machine Learning**, **historical climate analysis**, and **soil & seasonal conditions**.

The platform combines Machine Learning predictions with a rule-based recommendation engine to provide accurate crop suggestions, fertilizer guidance, and an intuitive dashboard for decision making.

---

## 🚀 Overview

AgriNova analyses multiple environmental factors to recommend the most suitable crops for cultivation.

The recommendation process considers:

- 🌍 City / Location
- 🌱 Soil Type
- 📅 Season
- 🌦 Historical Climate Data
  - Average Temperature
  - Average Rainfall
  - Average Humidity

Using these inputs, the system generates intelligent crop recommendations, confidence scores, and fertilizer suggestions through a modern and interactive user interface.

---

# ✨ Features

### 🤖 Machine Learning Prediction
- Random Forest Classifier
- Predicts the Top 3 most suitable crops
- Confidence score for every prediction

### 🌦 Historical Climate Analysis
- Fetches 2 years of historical weather data
- Calculates:
  - Average Temperature
  - Average Rainfall
  - Average Humidity

### 📊 Hybrid Recommendation Engine
- Machine Learning prediction
- Rule-based crop scoring
- Final crop suitability ranking

### 🌱 Fertilizer Recommendation
- Recommended fertilizer type
- Application timing
- Quantity estimation based on farm size

### ⚡ PostgreSQL Weather Cache
- Stores previously fetched climate data
- Reduces API calls
- Improves application performance

### 🎨 Modern User Interface
- Animated splash screen
- Premium landing page
- Glassmorphism-inspired design
- Responsive layout
- Climate summary dashboard
- Best recommendation card
- Machine Learning prediction cards
- Crop recommendation portfolio

---

# 🏗️ System Architecture

```text
                User Input
      (City • Soil • Season • Farm Size)
                       │
                       ▼
      Historical Weather Data (Open-Meteo)
                       │
                       ▼
      Climate Data Processing & Normalization
                       │
                       ▼
      Machine Learning Model (Random Forest)
                       │
                       ▼
         Top Crop Predictions + Confidence
                       │
                       ▼
      Rule-Based Recommendation Engine
                       │
                       ▼
      Fertilizer Recommendation System
                       │
                       ▼
        AgriNova Interactive Dashboard
```

---

# 🛠️ Tech Stack

## Backend
- Python
- Flask

## Machine Learning
- Scikit-learn
- Pandas
- NumPy

## Database
- PostgreSQL

## Frontend
- HTML5
- CSS3
- JavaScript

## APIs
- Open-Meteo Weather API

---

# 📂 Project Structure

```text
AgriNova/
│
├── app.py
├── crop_engine.py
├── weather_api.py
├── database.py
├── requirements.txt
│
├── static/
│   ├── style.css
│   ├── splash.css
│   └── images/
│
├── templates/
│   ├── splash.html
│   ├── welcome.html
│   ├── index.html
│   └── result.html
│
└── README.md
```

---

# 📸 Screenshots

> Add screenshots after uploading them to GitHub.

Suggested screenshots:

- Splash Screen
- Landing Page
- Crop Analysis Form
- Climate Summary Dashboard
- Machine Learning Predictions
- Crop Recommendation Cards

---

# ▶️ Installation

## Clone the Repository

```bash
git clone https://github.com/your-username/AgriNova.git
```

## Navigate to the Project

```bash
cd AgriNova
```

## Create a Virtual Environment

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run the Application

```bash
python app.py
```

Open your browser and visit:

```
http://127.0.0.1:5000
```

---

# 💡 How It Works

1. User enters:
   - City
   - Soil Type
   - Season
   - Farm Size

2. The application fetches historical climate data from the Open-Meteo API.

3. Climate data is processed and normalized.

4. The Random Forest model predicts the most suitable crops.

5. A rule-based scoring engine ranks the recommendations.

6. Fertilizer guidance is generated.

7. Results are displayed through an interactive dashboard with:
   - Climate Summary
   - Best Recommendation
   - ML Prediction Cards
   - Crop Portfolio
   - Fertilizer Guidance

---

# 🔮 Future Enhancements

- 7-Day Weather Forecast Integration
- Crop Yield Prediction
- Market Price Analysis
- Disease Risk Prediction
- Water Requirement Analysis
- Explainable AI Recommendations
- Multi-language Support
- Satellite Image Integration

---

# 📚 Technologies Used

- Python
- Flask
- HTML5
- CSS3
- JavaScript
- PostgreSQL
- Pandas
- NumPy
- Scikit-learn
- Open-Meteo API

---

# 👨‍💻 Author

**Shaheeq Shaik**

Computer Science Engineering Student

---

# ⭐ Support

If you found this project helpful, consider giving it a **⭐ Star** on GitHub.

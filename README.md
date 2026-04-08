# 🌱 Dynamic Crop Recommendation System

A Machine Learning-based web application that recommends optimal crops based on climate conditions, soil type, and season.

---

## 🚀 Features

- 🌦 Uses 2 years of historical weather data (temperature, rainfall, humidity)
- 🤖 Machine Learning model (Random Forest) for crop prediction
- 📊 Top 3 crop predictions with confidence scores
- 🧠 Hybrid system combining ML + rule-based scoring
- 🧪 Fertilizer recommendations with quantity estimation
- ⚡ PostgreSQL caching for faster performance
- 🎨 Interactive UI with animations and AI prediction cards

---

## 🏗️ System Architecture

User Input → Weather API → Data Processing → ML Model → Predictions → UI

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **Machine Learning:** Scikit-learn, Pandas, NumPy
- **Database:** PostgreSQL
- **Frontend:** HTML, CSS, JavaScript

---

## ▶️ How to Run

```bash
git clone <your-repo>
cd Dynamic-Crop-Recommendation-System

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python app.py

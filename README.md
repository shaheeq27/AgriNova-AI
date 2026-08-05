<p align="center">
  <h1 align="center">🌱 AgriNova AI</h1>
  <p align="center"><em>Where Nature Meets Intelligence</em></p>
  <p align="center">AI-Powered Precision Agriculture Platform — from seed to harvest.</p>
</p>

---

## Overview

AgriNova AI is a production-grade precision agriculture platform that assists farmers throughout the complete crop lifecycle using Artificial Intelligence, Machine Learning, Computer Vision, Knowledge Engineering, and Data Analytics.

**Current Version: 1.0.0** — Core Platform MVP

## Architecture

```
AgriNova-AI/
├── backend/              # FastAPI + SQLAlchemy (async)
│   ├── app/
│   │   ├── api/v1/       # REST API routes
│   │   ├── core/         # Config, DB, auth, exceptions
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── repositories/ # Data access layer
│   │   ├── schemas/      # Pydantic validation
│   │   └── services/     # Business logic
│   ├── data/             # KB seed scripts
│   └── ml/               # ML model training & artifacts
├── frontend/             # Next.js 15 + TypeScript
│   └── src/
│       ├── app/          # Pages (App Router)
│       ├── components/   # 80+ reusable components
│       ├── animations/   # Animation wrappers
│       ├── hooks/        # Custom React hooks
│       ├── styles/       # CSS design tokens
│       └── theme/        # TypeScript theme tokens
└── data/                 # Datasets (crop_dataset.csv)
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.14, FastAPI, SQLAlchemy (async), Pydantic v2 |
| **Frontend** | Next.js 15, React, TypeScript |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **ML** | scikit-learn, RandomForest (90.2% accuracy, 30 crops) |
| **Weather** | Open-Meteo API (free, no API key) |
| **Auth** | JWT (python-jose), bcrypt hashing |

## V1.0 Features

### 🤖 ML Crop Recommendation Engine
- RandomForest classifier trained on 4,500 augmented samples
- 30 crops, 90.2% accuracy
- Inputs: temperature, humidity, rainfall, soil type, N/P/K/pH
- Returns top 5 crops with confidence scores and explanations
- Rule-based fallback when model unavailable

### 🌾 Crop Lifecycle Management
- Plant crops on farms with season and area tracking
- Auto-generated growth timeline from Knowledge Base
- Daily task generation per growth stage

### 📅 Timeline & Daily Tasks
- 6-stage growth pipeline (Germination → Maturity)
- Stage-specific daily tasks (irrigation, fertilizer, monitoring)
- Task completion tracking

### 🌦 Weather Intelligence
- Real-time weather via Open-Meteo API
- 7-day forecast
- Weather alerts (frost, heat, heavy rain, high wind)
- Historical weather logging

### 🧪 Fertilizer Engine
- KB-driven fertilizer recommendations
- Stage-specific and crop-specific
- Application logging

### 💧 Irrigation Engine
- Water requirement calculations per crop/soil/stage
- Weather-adjusted recommendations
- Irrigation activity logging

### 🦠 Disease Detection
- Symptom-based matching against KB disease library
- Confidence scoring (Jaccard similarity)
- Image upload infrastructure (V1.0: storage only, CV in V6.0)
- Disease record tracking with status workflow

### 🔐 Authentication & Authorization
- JWT-based authentication
- User registration with email validation
- Farm ownership verification on all protected endpoints

### 🏡 Farm Management
- Full CRUD for farm profiles
- Multi-farm support per user
- Soil type and location tracking

### 📚 Knowledge Base
- 30 crop profiles with ideal conditions
- 180 growth stages (6 per crop)
- 8 disease entries with symptoms, treatment, prevention
- 30 fertilizer guidelines
- 120 irrigation guidelines

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/register` | Register user |
| `POST` | `/api/v1/auth/login` | Login (JWT) |
| `GET` | `/api/v1/auth/me` | Get profile |
| `POST` | `/api/v1/farms` | Create farm |
| `GET` | `/api/v1/farms` | List farms |
| `GET` | `/api/v1/farms/{id}` | Get farm |
| `PUT` | `/api/v1/farms/{id}` | Update farm |
| `DELETE` | `/api/v1/farms/{id}` | Delete farm |
| `POST` | `/api/v1/crops/recommend` | ML crop recommendation |
| `POST` | `/api/v1/crops/plant` | Plant crop |
| `GET` | `/api/v1/crops/farm/{id}` | List farm crops |
| `GET` | `/api/v1/crops/{id}` | Get crop detail |
| `GET` | `/api/v1/crops/{id}/timeline` | Get timeline |
| `GET` | `/api/v1/crops/{id}/tasks` | Get daily tasks |
| `GET` | `/api/v1/weather/farm/{id}` | Weather + forecast |
| `GET` | `/api/v1/fertilizer/recommend/{crop}` | Fertilizer rec |
| `GET` | `/api/v1/irrigation/recommend/{crop}` | Irrigation rec |
| `POST` | `/api/v1/disease/detect` | Detect disease |
| `GET` | `/api/v1/knowledge/crops` | List KB crops |
| `GET` | `/api/v1/knowledge/diseases` | List KB diseases |

Full interactive docs: `http://localhost:8000/docs` (Swagger UI) or `/redoc`

## Quick Start

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Seed Knowledge Base
python -m data.seed_knowledge

# Train ML Model
python -m ml.train_crop_model

# Run server
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`

## Environment Variables

Create `backend/.env`:
```env
APP_NAME=AgriNova AI
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite+aiosqlite:///./agrinova.db
```

## ML Model Details

| Metric | Value |
|--------|-------|
| Algorithm | RandomForest (200 trees) |
| Training samples | 4,500 (augmented from 30 crop profiles) |
| Test accuracy | 90.2% |
| Features | temp, humidity, rainfall, N, P, K, pH, soil_type |
| Crops covered | 30 (Rice, Wheat, Maize, Cotton, Sugarcane, etc.) |

## Roadmap

- [x] **V0.0** — Foundation (Auth, Farm, KB)
- [x] **V1.0** — Core Platform (ML, Lifecycle, Weather, Engines)
- [ ] **V2.0** — AI Intelligence (Gemini integration, NLP advisor)
- [ ] **V3.0** — Analytics Dashboard
- [ ] **V4.0** — Community & Marketplace
- [ ] **V5.0** — IoT Integration
- [ ] **V6.0** — Computer Vision (Disease Detection CNN)

## License

MIT

---

<p align="center">
  <strong>AgriNova AI</strong> — Built with 🌱 for Indian agriculture
</p>

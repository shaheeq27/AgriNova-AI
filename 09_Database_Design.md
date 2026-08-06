# 🌱 AgriNova AI

# Database Design

---

# Purpose

The database is the central storage system of AgriNova AI. It stores users, farms, crops, AI predictions, weather data, timelines, and knowledge base information while ensuring data consistency, reliability, and scalability.

---

# Table of Contents

1. Database Overview
2. Database Technology
3. Design Principles
4. Database Structure
5. Core Tables
6. Relationships
7. Indexing & Performance
8. Data Integrity
9. Future Expansion
10. Summary

---

# 1. Database Overview

AgriNova AI uses a relational database to manage structured agricultural data.

The database stores:

- Users
- Farms
- Crops
- Weather
- Disease Records
- Fertilizer Plans
- Irrigation Plans
- Timelines
- Knowledge Base
- AI Predictions

---

# 2. Database Technology

| Technology | Purpose |
|------------|---------|
| PostgreSQL | Primary Database |
| SQLAlchemy | ORM |
| Alembic | Schema Migration |
| Redis | Caching |

### Why PostgreSQL?

- Reliable
- ACID Compliant
- Strong Relationships
- High Performance
- Easy Scaling

---

# 3. Design Principles

The database is designed to be:

- Normalized
- Scalable
- Secure
- Consistent
- Easy to Maintain

Each table stores one specific type of information.

---

# 4. Database Structure

```
Users
   │
 Farms
   │
 Crops
   │
Timelines
   │
Recommendations

Knowledge Base

Weather

Disease Records
```

The database is organized around the farm, which acts as the central entity.

---

# 5. Core Tables

| Table | Purpose |
|--------|---------|
| Users | User Accounts |
| Farms | Farm Information |
| Crops | Crop Details |
| Crop Recommendations | AI Predictions |
| Weather Cache | Weather Data |
| Disease Records | Disease History |
| Fertilizer Plans | Fertilizer Recommendations |
| Irrigation Plans | Water Schedules |
| Crop Timeline | Growth Stages |
| Knowledge Base | Agricultural Data |

---

# 6. Relationships

```
User
 │
 └── Farm
        │
        ├── Crop
        ├── Timeline
        ├── Fertilizer
        ├── Irrigation
        ├── Disease
        └── Recommendation
```

One user can own multiple farms.

Each farm can contain multiple crops and related records.

---

# 7. Indexing & Performance

To improve query speed:

- Primary Keys
- Foreign Keys
- Indexed Search Fields
- Cached Weather Data
- Optimized Queries

Redis is used to reduce repeated API requests.

---

# 8. Data Integrity

The database ensures:

- Unique IDs
- Valid Relationships
- Required Fields
- Referential Integrity
- Safe Transactions

Database migrations are managed using Alembic.

---

# 9. Future Expansion

Planned additions:

- Market Prices
- IoT Sensor Data
- Satellite Images
- Drone Reports
- Enterprise Organizations
- AI Conversation History
- Yield Prediction Records

The current design allows these tables to be added without restructuring the database.

---

# 10. Summary

The AgriNova AI database is built on PostgreSQL using a normalized relational design. It provides reliable storage for all platform data while maintaining strong relationships, efficient querying, and scalability for future AI-powered features.
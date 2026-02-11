# 🚗 Audi Used Car Inventory – End-to-End Data Pipeline & ML System

**Live Application:**  
👉 https://audi-used-car.onrender.com/

---

## 📌 Objective

This project implements a **complete end-to-end automated data pipeline and machine learning system** that:

- Scrapes used car inventory from a real-world website
- Synchronizes data with a database
- Trains a machine learning model for price prediction
- Exposes REST APIs
- Runs on a 24-hour automated schedule
- Is deployed and accessible publicly

---

## 🌐 Target Website

**Audi West Island – Used Inventory**  
https://www.audiwestisland.com/fr/inventaire/occasion/

> The website uses JavaScript-rendered content, requiring a browser-based scraping approach.

---

## 🏗️ System Architecture
n8n (24-hour Scheduler)
↓
FastAPI Backend (Render)
↓
Playwright Web Scraper
↓
MongoDB Sync Engine
↓
ML Training Pipeline
↓
MongoDB Atlas


---

## 🧰 Technology Stack

| Layer | Technology |
|-----|-----------|
| Web Scraping | Playwright |
| Backend API | FastAPI |
| Database | MongoDB Atlas |
| Automation | n8n |
| Machine Learning | Scikit-learn |
| Deployment | Render |
| Language | Python 3 |

---

## 🕷️ Web Scraping

- Implemented using **Playwright**
- Handles JavaScript-rendered pages
- Waits for DOM elements before extraction
- Extracted fields:
  - Vehicle title
  - VIN (unique identifier)
  - Year
  - Mileage (km)
  - Price
  - Trim
  - Listing URL

---

## 🗄️ Database Design

### Vehicles Collection
Stores the latest state of each vehicle:
- `vin`
- `title`
- `year`
- `mileage_km`
- `price`
- `trim`
- `listing_url`
- `date_scraped`
- `last_seen`
- `status` (active / inactive)

### Sync Logs Collection
Tracks synchronization history:
- `sync_time`
- `added`
- `updated`
- `removed`
- `total_active`

---

## 🔄 Automated Synchronization

A custom **sync engine**:
- Inserts new vehicles
- Updates existing vehicles
- Marks missing vehicles as inactive
- Logs every run for auditing

Runs automatically every **24 hours** via n8n.

---

## 🤖 Machine Learning Pipeline

- **Model Type:** Regression
- **Features:**
  - Vehicle year
  - Mileage
- **Target:** Price
- Model retrains automatically after every successful sync
- Model is loaded lazily to ensure production stability

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|------|--------|------------|
| GET | `/vehicles` | Fetch all active vehicles |
| GET | `/vehicles/{vin}/predict` | Predict price for a vehicle |
| POST | `/trigger-sync` | Run scraping, sync & ML training |
| GET | `/sync-status` | View last sync summary |

Swagger UI available at:
/docs

---

## ⏰ Automation with n8n

- **Schedule Trigger:** Every 24 hours
- **Action:** HTTP Request
- **Endpoint Called:** POST /trigger-sync


Ensures full automation without manual intervention.

---

## 🚀 Deployment

- Backend deployed on **Render**
- Database hosted on **MongoDB Atlas**
- Secure configuration using environment variables
- Public URL:

👉 https://audi-used-car.onrender.com/

---

## 📁 Project Structure
audi-used-car-ml/
│
├── api/ # FastAPI routes
├── scraper/ # Playwright scraper
├── sync/ # Data synchronization logic
├── ml/ # ML training & prediction
├── db/ # MongoDB connection
├── requirements.txt
├── render.ya
ml
└── README.md

---

## ✅ Key Outcomes

- Fully automated data ingestion pipeline
- Real-world dynamic web scraping
- Production-ready ML lifecycle
- REST APIs with live deployment
- Scalable and modular architecture

---

## 📌 Conclusion

This project demonstrates a **production-grade implementation** of web scraping, data engineering, machine learning, automation, and cloud deployment in a single integrated system.

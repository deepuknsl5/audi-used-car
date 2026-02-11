Audi Used Car Inventory – End-to-End Data Pipeline & Machine Learning System
1. Problem Statement

The objective of this assignment is to design and implement an automated data pipeline that:

Scrapes used car inventory data from a real-world website

Stores and synchronizes data reliably in a database

Trains a machine learning model for price prediction

Exposes REST APIs for data access and predictions

Runs automatically on a scheduled basis

Is deployed and accessible via a public URL

2. Target Data Source

Website: Audi West Island – Used Car Inventory
URL: https://www.audiwestisland.com/fr/inventaire/occasion/

This website uses JavaScript-rendered content, requiring a browser-based scraping solution.

3. System Architecture

High-level Flow:

n8n (24-hour scheduler)
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

The architecture ensures automation, scalability, and fault tolerance.

4. Technology Stack
Layer	Technology
Web Scraping	Playwright
Backend	FastAPI
Database	MongoDB Atlas
Automation	n8n
Machine Learning	Scikit-learn
Deployment	Render
Programming Language	Python 3
5. Web Scraping Approach

Implemented using Playwright to handle JavaScript-rendered pages

Waits for DOM elements to load before extraction

Extracted fields:

Vehicle Title

VIN (unique identifier)

Year

Mileage (km)

Price

Trim

Listing URL

Pagination and dynamic content handled automatically

6. Database Design
Vehicles Collection

Stores the latest state of each vehicle:

vin

title

year

mileage_km

price

trim

listing_url

date_scraped

last_seen

status (active / inactive)

Sync Logs Collection

Maintains audit history of synchronization runs:

sync_time

added

updated

removed

total_active

7. Data Synchronization Logic

A custom sync engine performs:

Insert → New vehicles

Update → Existing vehicles with changed attributes

Deactivate → Vehicles no longer present on the website

This guarantees data accuracy and historical traceability.

8. Machine Learning Pipeline

Model Type: Regression

Features Used:

Vehicle Year

Mileage

Target Variable: Price

Automation:

Model retrains automatically after every successful sync

Model is saved and loaded lazily for production stability

9. API Design
Method	Endpoint	Description
GET	/vehicles	Retrieve all active vehicles
GET	/vehicles/{vin}/predict	Predict price for a vehicle
POST	/trigger-sync	Run scrape + sync + ML training
GET	/sync-status	View latest sync summary

All APIs are exposed via FastAPI and return JSON responses.

10. Automation (n8n)

Schedule Trigger runs every 24 hours

Triggers an HTTP request to:

POST /trigger-sync

Ensures:

Fresh data ingestion

Automatic retraining

No manual intervention

11. Deployment

Backend deployed on Render

Database hosted on MongoDB Atlas

Secure configuration using environment variables:

MONGO_URI

Public access via:

🔗 Live Application:
https://audi-used-car.onrender.com/

12. Project Structure
audi-used-car-ml/
│
├── api/        # FastAPI routes
├── scraper/   # Playwright scraper
├── sync/      # Data synchronization logic
├── ml/        # ML training & prediction
├── db/        # MongoDB connection
├── requirements.txt
├── render.yaml
└── README.md
13. Key Outcomes

Fully automated end-to-end pipeline

Real-world web scraping with JS handling

Production-ready ML workflow

Cloud deployment with scheduling

Clean, modular, scalable codebase

14. Conclusion

This assignment demonstrates the ability to design and implement a real-world, production-grade data and ML system, covering scraping, storage, automation, machine learning, APIs, and deployment.

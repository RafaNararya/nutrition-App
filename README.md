# Personalized Nutrition API (Micro and Macronutrient Focused)

A high-performance, containerized REST API built with **FastAPI** and **PostgreSQL**. This system serves as the intelligence engine for personalized nutritional analysis, processing over 370+ USDA-derived data points to provide optimized dietary insights.

## The Goal
While most nutrition apps are just glorified spreadsheets, this project aims to bridge the gap between raw data and actionable insights. By leveraging a relational database and machine learning models (Scikit-learn), the API calculates dynamic nutritional targets based on biometric inputs (height, weight, age) and food consumption patterns.

## Tech Stack
* **Backend:** FastAPI 
* **Database:** PostgreSQL 
* **ML/Logic:** Scikit-learn (Biometric analysis)
* **DevOps:** Docker, Docker-compose


## System Architecture
├── app/
│   ├── main.py          # Entry point & FastAPI initialization
│   ├── routers/         # API endpoints (Users, Nutrition, Analysis)
│   ├── models/          # SQLAlchemy database schemas
│   ├── schemas/         # Pydantic data validation models
│   └── database.py      # Connection pooling & Session management
└── requirements.txt     # Dependency management
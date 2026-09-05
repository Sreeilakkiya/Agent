# FlowRecover - AI Revenue Leak Hunter

## Project Overview
FlowRecover is an AI-powered B2B revenue protection platform that detects, predicts, explains, prevents, and recovers revenue leaks.

## Architecture
```
Frontend (React + Vite + Tailwind) 
    ↓
FastAPI REST API 
    ↓
Business Logic & ML Services 
    ↓
PostgreSQL Database
```

## Tech Stack
- **Frontend**: React, Vite, JavaScript, Tailwind CSS, Recharts, Axios, React Router
- **Backend**: Python, FastAPI, Pydantic, SQLAlchemy, PostgreSQL, JWT
- **ML**: Scikit-learn, Pandas, NumPy, Joblib
- **AI**: LLM abstraction layer for explanations

## Folder Structure
```
flowrecover/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── ml/
│   │   └── utils/
│   ├── requirements.txt
│   └── .env.example
├── ml/
│   ├── data/
│   ├── training/
│   ├── models/
│   └── notebooks/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── layouts/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── utils/
│   ├── package.json
│   └── .env.example
├── docker-compose.yml
├── README.md
└── .gitignore
```

## Database Schema
- **users**: id, email, password_hash, company_id, created_at, updated_at
- **companies**: id, name, created_at, updated_at
- **customers**: id, company_id, name, email, tenure_days, plan_value, activity_score, created_at, updated_at
- **transactions**: id, customer_id, amount, payment_method, status, failure_count, created_at
- **subscriptions**: id, customer_id, start_date, end_date, status, renewal_count
- **refunds**: id, transaction_id, reason, amount, status, created_at
- **risk_predictions**: id, customer_id, prediction_type, probability, revenue_at_risk, severity, created_at
- **recovery_actions**: id, prediction_id, action_type, status, outcome, revenue_protected, created_at

## API Endpoints
- POST /auth/register, /auth/login
- GET /dashboard, /customers, /customers/{id}, /leaks, /predictions, /prevention, /recovery
- POST /predict/payment, /predict/churn, /predict/refund, /ai/explain, /actions, /upload/csv
- GET /health

## Setup Instructions

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database credentials
python -m app.main
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### Database
Ensure PostgreSQL is running and create a database named `flowrecover`.

## Demo Credentials
- Email: demo@flowrecover.com
- Password: demo123

## Features
1. **Dashboard**: KPI cards showing Total Revenue, Revenue at Risk, Revenue Protected, High Risk Cases, Recovery Rate
2. **Leak Detection**: Categorize leaks by Payment Failure, Customer Churn, Refund Risk
3. **ML Models**: Real Random Forest models for prediction
4. **Prevention Engine**: Actionable recommendations based on risk scores
5. **AI Insights**: LLM-generated explanations for risks
6. **Data Upload**: CSV upload with validation or use demo dataset

## Future Improvements
- Real-time data streaming
- Advanced anomaly detection
- Integration with payment gateways
- Email/SMS notifications
- Custom model training UI

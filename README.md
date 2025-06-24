# Zabbix AI Anomaly Detection

A monitoring solution that integrates Zabbix with AI-powered anomaly detection to provide intelligent insights about system performance and potential issues.

## Project Structure

```
zabbix_ai_anomaly/
├── backend/                 # FastAPI backend application
│   ├── app/                 # Application code
│   │   ├── __init__.py
│   │   ├── api/             # API endpoints
│   │   ├── core/            # Core functionality
│   │   ├── db/              # Database models and connections
│   │   └── services/        # Business logic services
│   ├── tests/               # Backend tests
│   └── main.py              # Entry point for the backend
├── frontend/                # React frontend application
│   ├── public/              # Static assets
│   ├── src/                 # Source code
│   │   ├── components/      # Reusable components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   └── main.jsx         # Entry point for the frontend
│   ├── index.html           # HTML template
│   └── vite.config.js       # Vite configuration
├── .env.example             # Example environment variables
├── .gitignore               # Git ignore file
├── README.md                # Project documentation
└── requirements.txt         # Python dependencies
```

## Setup and Installation

### Backend

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and configure your environment variables.

4. Start the backend server:
   ```
   cd backend
   uvicorn main:app --reload
   ```

### Frontend

1. Install dependencies:
   ```
   cd frontend
   npm install
   ```

2. Start the development server:
   ```
   npm run dev
   ```

## Features

- Real-time monitoring data visualization
- AI-powered anomaly detection
- Root cause analysis
- User feedback collection for model improvement
- Historical data analysis

## Technologies

- **Backend**: FastAPI, SQLAlchemy, Pandas, Google Generative AI
- **Frontend**: React, Recharts, Axios
- **Data Sources**: Zabbix API, MySQL 
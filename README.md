# GitHub Stats Analyzer

A comprehensive GitHub project statistics analyzer that shows trending repositories based on stars, forks, and watchers.

## Features

- Display top 1000 repositories by:
  - Daily star count
  - Weekly star growth
  - Fork count
  - Watcher count
- Detailed project statistics for the last 3 months
- Automated data collection using Python
- React-based web interface
- Python backend API
- Data storage in Cloudflare D1

## Project Structure

```
github-stats/
├── frontend/           # React frontend application
├── backend/           # Python backend API
├── crawler/           # Python data collection scripts
└── database/         # Database schemas and migrations
```

## Setup Instructions

1. Install dependencies:
```bash
# Frontend
cd frontend
npm install

# Backend
cd backend
pip install -r requirements.txt
```

2. Configure environment variables:
- Create `.env` file in the root directory
- Add necessary API keys and configuration

3. Run the application:
```bash
# Start frontend
cd frontend
npm start

# Start backend
cd backend
python app.py
```

## Technologies Used

- Frontend: React, Material-UI
- Backend: Python, FastAPI
- Database: Cloudflare D1
- Data Collection: Python, GitHub API
- Deployment: Cloudflare Workers

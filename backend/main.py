from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import sqlite3
from typing import List
from pydantic import BaseModel

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Repository(BaseModel):
    id: int
    name: str
    full_name: str
    description: str | None
    url: str
    stars: int
    forks: int
    watchers: int

class RepositoryDetail(Repository):
    history: List[dict]

def get_db():
    return sqlite3.connect('../database/github_stats.db')

@app.get("/api/trending/daily", response_model=List[Repository])
async def get_daily_trending():
    conn = get_db()
    cursor = conn.cursor()
    
    yesterday = (datetime.now() - timedelta(days=1)).isoformat()
    
    cursor.execute('''
        SELECT 
            r.github_id,
            r.name,
            r.full_name,
            r.description,
            r.url,
            s.stars,
            s.forks,
            s.watchers
        FROM repositories r
        JOIN repository_stats s ON r.github_id = s.repository_id
        WHERE s.collected_at > ?
        ORDER BY s.stars DESC
        LIMIT 1000
    ''', (yesterday,))
    
    repos = cursor.fetchall()
    conn.close()
    
    return [
        Repository(
            id=repo[0],
            name=repo[1],
            full_name=repo[2],
            description=repo[3],
            url=repo[4],
            stars=repo[5],
            forks=repo[6],
            watchers=repo[7]
        )
        for repo in repos
    ]

@app.get("/api/trending/weekly", response_model=List[Repository])
async def get_weekly_trending():
    conn = get_db()
    cursor = conn.cursor()
    
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    
    cursor.execute('''
        WITH weekly_growth AS (
            SELECT 
                repository_id,
                MAX(stars) - MIN(stars) as star_growth
            FROM repository_stats
            WHERE collected_at > ?
            GROUP BY repository_id
        )
        SELECT 
            r.github_id,
            r.name,
            r.full_name,
            r.description,
            r.url,
            s.stars,
            s.forks,
            s.watchers
        FROM repositories r
        JOIN repository_stats s ON r.github_id = s.repository_id
        JOIN weekly_growth w ON r.github_id = w.repository_id
        ORDER BY w.star_growth DESC
        LIMIT 1000
    ''', (week_ago,))
    
    repos = cursor.fetchall()
    conn.close()
    
    return [
        Repository(
            id=repo[0],
            name=repo[1],
            full_name=repo[2],
            description=repo[3],
            url=repo[4],
            stars=repo[5],
            forks=repo[6],
            watchers=repo[7]
        )
        for repo in repos
    ]

@app.get("/api/repository/{repo_id}", response_model=RepositoryDetail)
async def get_repository_detail(repo_id: int):
    conn = get_db()
    cursor = conn.cursor()
    
    # Get repository info
    cursor.execute('''
        SELECT 
            r.github_id,
            r.name,
            r.full_name,
            r.description,
            r.url,
            s.stars,
            s.forks,
            s.watchers
        FROM repositories r
        JOIN repository_stats s ON r.github_id = s.repository_id
        WHERE r.github_id = ?
        ORDER BY s.collected_at DESC
        LIMIT 1
    ''', (repo_id,))
    
    repo = cursor.fetchone()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Get historical stats
    three_months_ago = (datetime.now() - timedelta(days=90)).isoformat()
    cursor.execute('''
        SELECT 
            stars,
            forks,
            watchers,
            collected_at
        FROM repository_stats
        WHERE repository_id = ? AND collected_at > ?
        ORDER BY collected_at
    ''', (repo_id, three_months_ago))
    
    history = cursor.fetchall()
    conn.close()
    
    return RepositoryDetail(
        id=repo[0],
        name=repo[1],
        full_name=repo[2],
        description=repo[3],
        url=repo[4],
        stars=repo[5],
        forks=repo[6],
        watchers=repo[7],
        history=[
            {
                "stars": h[0],
                "forks": h[1],
                "watchers": h[2],
                "date": h[3]
            }
            for h in history
        ]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

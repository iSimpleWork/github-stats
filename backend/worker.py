from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import json
from typing import List
from pydantic import BaseModel

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

async def query_db(db, query, params=()):
    stmt = db.prepare(query)
    return await stmt.bind(params).all()

@app.get("/api/trending/daily", response_model=List[Repository])
async def get_daily_trending(request):
    db = request.app.state.db
    yesterday = (datetime.now() - timedelta(days=1)).isoformat()
    
    results = await query_db(db, '''
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
    
    return [
        Repository(
            id=row["github_id"],
            name=row["name"],
            full_name=row["full_name"],
            description=row["description"],
            url=row["url"],
            stars=row["stars"],
            forks=row["forks"],
            watchers=row["watchers"]
        )
        for row in results
    ]

@app.get("/api/trending/weekly", response_model=List[Repository])
async def get_weekly_trending(request):
    db = request.app.state.db
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    
    results = await query_db(db, '''
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
    
    return [
        Repository(
            id=row["github_id"],
            name=row["name"],
            full_name=row["full_name"],
            description=row["description"],
            url=row["url"],
            stars=row["stars"],
            forks=row["forks"],
            watchers=row["watchers"]
        )
        for row in results
    ]

@app.get("/api/repository/{repo_id}", response_model=RepositoryDetail)
async def get_repository_detail(request, repo_id: int):
    db = request.app.state.db
    
    # Get repository info
    repo_results = await query_db(db, '''
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
    
    if not repo_results:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    repo = repo_results[0]
    
    # Get historical stats
    three_months_ago = (datetime.now() - timedelta(days=90)).isoformat()
    history_results = await query_db(db, '''
        SELECT 
            stars,
            forks,
            watchers,
            collected_at
        FROM repository_stats
        WHERE repository_id = ? AND collected_at > ?
        ORDER BY collected_at
    ''', (repo_id, three_months_ago))
    
    return RepositoryDetail(
        id=repo["github_id"],
        name=repo["name"],
        full_name=repo["full_name"],
        description=repo["description"],
        url=repo["url"],
        stars=repo["stars"],
        forks=repo["forks"],
        watchers=repo["watchers"],
        history=[
            {
                "stars": h["stars"],
                "forks": h["forks"],
                "watchers": h["watchers"],
                "date": h["collected_at"]
            }
            for h in history_results
        ]
    )

def create_app(env):
    app.state.db = env.DB
    return app

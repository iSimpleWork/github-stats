import os
import time
from datetime import datetime, timedelta
import schedule
from github import Github
from dotenv import load_dotenv
import sqlite3
import json

# Load environment variables
load_dotenv()

class GitHubCrawler:
    def __init__(self):
        self.github = Github(os.getenv('GITHUB_TOKEN'))
        self.db_path = '../database/github_stats.db'
        self.setup_database()

    def setup_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create repositories table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS repositories (
            id INTEGER PRIMARY KEY,
            github_id INTEGER UNIQUE,
            name TEXT,
            full_name TEXT,
            description TEXT,
            url TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        ''')

        # Create stats table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS repository_stats (
            id INTEGER PRIMARY KEY,
            repository_id INTEGER,
            stars INTEGER,
            forks INTEGER,
            watchers INTEGER,
            collected_at TEXT,
            FOREIGN KEY (repository_id) REFERENCES repositories(github_id)
        )
        ''')

        conn.commit()
        conn.close()

    def collect_repository_data(self):
        print(f"Starting data collection at {datetime.now()}")
        
        try:
            # Search for most starred repositories
            query = "stars:>1000"
            repos = self.github.search_repositories(
                query=query,
                sort="stars",
                order="desc"
            )

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            count = 0
            for repo in repos:
                if count >= 1000:
                    break

                # Insert or update repository info
                cursor.execute('''
                INSERT OR REPLACE INTO repositories 
                (github_id, name, full_name, description, url, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    repo.id,
                    repo.name,
                    repo.full_name,
                    repo.description,
                    repo.html_url,
                    repo.created_at.isoformat(),
                    repo.updated_at.isoformat()
                ))

                # Insert current stats
                cursor.execute('''
                INSERT INTO repository_stats 
                (repository_id, stars, forks, watchers, collected_at)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    repo.id,
                    repo.stargazers_count,
                    repo.forks_count,
                    repo.watchers_count,
                    datetime.now().isoformat()
                ))

                count += 1
                if count % 10 == 0:
                    print(f"Processed {count} repositories")
                
                # Respect GitHub API rate limits
                time.sleep(1)

            conn.commit()
            conn.close()
            print(f"Completed data collection at {datetime.now()}")

        except Exception as e:
            print(f"Error during data collection: {str(e)}")

    def run_scheduler(self):
        # Run data collection every 6 hours
        schedule.every(6).hours.do(self.collect_repository_data)
        
        # Run immediately on start
        self.collect_repository_data()
        
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    crawler = GitHubCrawler()
    crawler.run_scheduler()

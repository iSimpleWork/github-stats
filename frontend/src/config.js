const config = {
    apiBaseUrl: process.env.NODE_ENV === 'production'
        ? 'https://github-stats-api.your-worker.workers.dev'  // 替换为实际的Workers域名
        : 'http://localhost:8000'
};

export default config;

# AI Web Crawler

An intelligent web crawler that searches the web, filters results using LLM, extracts company data, and enriches contact information.

## Features

- **Smart Search**: Uses SearxNG to find relevant URLs
- **LLM Filtering**: GPT-powered filtering of search results before crawling
- **Intelligent Extraction**: Extracts company data from web pages using Playwright
- **Enrichment Pipeline**: Deduplicates and enriches company contact details
- **Real-time Updates**: Live activity log with Server-Sent Events
- **Export Options**: Download results as CSV or JSON

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **OpenAI GPT-3.5**: LLM for filtering and enrichment
- **Playwright**: Browser automation via remote service
- **SearxNG**: Privacy-respecting metasearch engine

### Frontend
- **React + Vite**: Modern frontend build tooling
- **Server-Sent Events**: Real-time progress updates

## Setup

### Backend

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
```

3. Activate virtual environment:
- Windows: `.\venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create `.env` file:
```
OPENAI_API_KEY=your_api_key_here
```

6. Run the server:
```bash
python main.py
```

Backend will run on `http://127.0.0.1:8000`

### Frontend

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run development server:
```bash
npm run dev
```

Frontend will run on `http://localhost:5173`

## Usage

1. Enter a search query (e.g., "cosmetics distributors in Philippines")
2. Set the number of results to fetch
3. Click "Search" and watch the live activity log
4. Optionally click "Enrich Results" to enhance contact details
5. Download results as CSV or JSON

## Environment Variables

### Backend (.env)
- `OPENAI_API_KEY`: Your OpenAI API key for LLM operations

## Deployment

### Railway (Recommended)

1. Push to GitHub
2. Connect repository to Railway
3. Set environment variables in Railway dashboard
4. Deploy!

### Docker

```bash
# Backend
cd backend
docker build -t web-crawler-backend .
docker run -p 8000:8000 --env-file .env web-crawler-backend

# Frontend
cd frontend
docker build -t web-crawler-frontend .
docker run -p 5173:5173 web-crawler-frontend
```

## Project Structure

```
web crawler/
├── backend/
│   ├── services/
│   │   ├── crawler.py       # Web crawling logic
│   │   ├── enrichment.py    # LLM enrichment pipeline
│   │   ├── llm_filter.py    # Search result filtering
│   │   └── searxng.py       # Search integration
│   ├── main.py              # FastAPI app
│   ├── models.py            # Pydantic models
│   └── requirements.txt     # Python dependencies
└── frontend/
    ├── src/
    │   ├── App.jsx          # Main React component
    │   └── App.css          # Styles
    └── package.json         # Node dependencies
```

## License

MIT

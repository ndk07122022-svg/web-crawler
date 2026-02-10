# Deployment Checklist

## Pre-Deployment Steps

### Backend Setup
1. **Environment Variables**
   - Copy `.env.example` to `.env`
   - Add your `OPENAI_API_KEY`
   - In production, set `PORT` if required by host

2. **Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Test Locally**
   ```bash
   python main.py
   # Should run on http://0.0.0.0:8000
   ```

### Frontend Setup
1. **Environment Variables**
   - For development: Copy `.env.example` to `.env`
   - For production: Copy `.env.production.example` to `.env.production`
   - Update `VITE_API_URL` with your backend URL

2. **Dependencies**
   ```bash
   npm install
   ```

3. **Test Build**
   ```bash
   npm run build
   npm run preview
   ```

## Deployment Options

### Railway (Recommended)

#### Backend
1. Create new project on Railway
2. Connect GitHub repository
3. Select `backend` as root directory
4. Add environment variables:
   - `OPENAI_API_KEY`: Your OpenAI key
5. Deploy!

#### Frontend
1. Create new project on Railway
2. Connect GitHub repository
3. Select `frontend` as root directory
4. Add environment variables:
   - `VITE_API_URL`: Your backend Railway URL
5. Deploy!

### Docker

#### Backend
```bash
cd backend
docker build -t web-crawler-backend .
docker run -p 8000:8000 --env-file .env web-crawler-backend
```

#### Frontend
```bash
cd frontend
docker build -t web-crawler-frontend .
docker run -p 5173:5173 web-crawler-frontend
```

### Environment Variables Summary

**Backend (.env)**
- `OPENAI_API_KEY` - Required for LLM operations
- `PORT` - Optional, defaults to 8000

**Frontend (.env / .env.production)**
- `VITE_API_URL` - Backend API URL

## Post-Deployment Verification

1. ✅ Backend health check: `GET {backend_url}/`
2. ✅ Test search endpoint: `POST {backend_url}/search`
3. ✅ Frontend loads correctly
4. ✅ Search functionality works
5. ✅ Enrichment pipeline works
6. ✅ Download CSV/JSON works

## Troubleshooting

### CORS Issues
- Backend already configured with `allow_origins=["*"]`
- For production, update to specific frontend domain

### Port Issues
- Railway/Render auto-assign PORT
- Backend reads from `os.environ.get("PORT", 8000)`

### API Connection
- Verify `VITE_API_URL` is set correctly in frontend
- Check backend URL in browser console network tab

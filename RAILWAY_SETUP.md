# Quick Deployment Checklist

## Files Created/Updated ✅

- ✅ `railway.toml` (root) - Backend Railway config
- ✅ `frontend/railway.toml` - Frontend Railway config  
- ✅ `frontend/vite.config.js` - Updated for dynamic port binding

---

## Railway Deployment Steps

### Backend Service

1. **Create new Railway project** from your GitHub repo
2. **Add environment variables**:
   ```
   GROQ_API_KEY=your_key_here
   SEARXNG_URL=https://search.inetol.net
   ```
3. **Deploy** - Railway will use root `railway.toml`
4. **Copy backend URL** (e.g., `https://xxx-backend.railway.app`)

### Frontend Service

1. **Add new service** in the same Railway project
2. **Select same GitHub repo**
3. **Settings → Build → Root Directory** = `frontend`
4. **Add environment variable**:
   ```
   VITE_API_URL=<your-backend-url-from-step-4>
   ```
5. **Deploy** - Railway will use `frontend/railway.toml`
6. **Access your app** at the frontend URL!

---

## Environment Variables Summary

| Service | Variable | Example Value |
|---------|----------|---------------|
| Backend | `GROQ_API_KEY` | `gsk_...` |
| Backend | `SEARXNG_URL` | `https://search.inetol.net` |
| Frontend | `VITE_API_URL` | `https://xxx-backend.railway.app` |

---

## What Each File Does

- **`railway.toml`** (root): Tells Railway to build backend using `backend/Dockerfile` with backend directory as context
- **`frontend/railway.toml`**: Tells Railway to build frontend using `frontend/Dockerfile` with frontend directory as context
- **`frontend/vite.config.js`**: Enables Vite preview server to use Railway's dynamic `$PORT` variable

---

## After Deployment

Both services will have their own URLs:
- **Frontend**: Your main web app - share this with users!
- **Backend**: API server - frontend calls this automatically

See [railway_deployment_guide.md](file:///C:/Users/rsa_g/.gemini/antigravity/brain/727a477b-83a3-4d2a-af33-4cff6f629f23/railway_deployment_guide.md) for detailed instructions and troubleshooting.

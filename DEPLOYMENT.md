# Deployment Guide: Railway (Backend) + Vercel (Frontend)

This guide explains how to deploy InvoiceFlow to production using Railway for the backend and Vercel for the frontend.

## Prerequisites

1. **GitHub Account** - Your code should be in a GitHub repository
2. **Railway Account** - Sign up at [railway.app](https://railway.app)
3. **Vercel Account** - Sign up at [vercel.com](https://vercel.com)
4. **Azure Account** - For Form Recognizer (already configured)
5. **OpenAI API Key** - For LLM enhancement (optional but recommended)

---

## Part 1: Deploy Backend to Railway

### Step 1: Prepare Repository

1. Ensure your code is pushed to GitHub
2. Make sure `backend/Dockerfile` exists (✅ already exists)
3. Make sure `railway.json` exists (✅ created)

### Step 2: Create Railway Project

1. Go to [railway.app](https://railway.app) and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your InvoiceFlow repository
5. Railway will auto-detect the Dockerfile in `backend/` directory

### Step 3: Add PostgreSQL Database

1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway will create a PostgreSQL database automatically
4. **Copy the DATABASE_URL** from the database service variables

### Step 4: Configure Environment Variables

In Railway, go to your backend service → **Variables** tab, add:

```bash
# Database (from Railway PostgreSQL service)
DATABASE_URL=postgresql://user:password@host:port/dbname

# Azure Form Recognizer (required)
AZURE_FORM_RECOGNIZER_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_FORM_RECOGNIZER_KEY=your-azure-key-here

# OpenAI (optional but recommended)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
USE_LLM_FOR_EXTRACTION=true

# CORS - Add your Vercel frontend URL (update after deploying frontend)
CORS_ORIGINS=["https://your-app.vercel.app"]

# Environment
ENVIRONMENT=production
DEBUG=false

# MinIO/S3 - Use Railway's storage or external S3
# Option A: Use Railway Volume (for development)
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=invoiceflow
MINIO_USE_SSL=false

# Option B: Use AWS S3 (recommended for production)
# MINIO_ENDPOINT=s3.amazonaws.com
# MINIO_ACCESS_KEY=your-aws-access-key
# MINIO_SECRET_KEY=your-aws-secret-key
# MINIO_BUCKET=invoiceflow-prod
# MINIO_USE_SSL=true
```

**Important Notes:**
- Railway provides `$PORT` automatically - your app should use it
- Update `CORS_ORIGINS` after you get your Vercel URL
- For production, use AWS S3 instead of MinIO (Railway doesn't provide MinIO service)

### Step 5: Run Database Migrations

Railway will auto-deploy, but you need to run migrations:

1. In Railway, go to your backend service
2. Click **"Settings"** → **"Deploy"**
3. Add a **"Deploy Command"**:
   ```bash
   alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port $PORT
   ```

Or use Railway's **"Generate Domain"** to get your backend URL, then SSH in and run:
```bash
alembic upgrade head
```

### Step 6: Get Backend URL

1. In Railway, go to your backend service
2. Click **"Settings"** → **"Generate Domain"**
3. Copy the URL (e.g., `invoiceflow-backend.railway.app`)
4. **Save this URL** - you'll need it for Vercel

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Prepare Frontend

1. Update `frontend/src/lib/api.ts` to use environment variable (✅ already done)
2. Make sure `vercel.json` exists (✅ created)

### Step 2: Create Vercel Project

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend` (important!)
   - **Build Command**: `npm run build` (or `cd frontend && npm run build`)
   - **Output Directory**: `.next`
   - **Install Command**: `npm install` (or `cd frontend && npm install`)

### Step 3: Configure Environment Variables

In Vercel, go to your project → **Settings** → **Environment Variables**, add:

```bash
NEXT_PUBLIC_API_URL=https://your-railway-backend.railway.app
```

**Important:** Replace `your-railway-backend.railway.app` with your actual Railway backend URL from Step 6 above.

### Step 4: Deploy

1. Click **"Deploy"**
2. Vercel will build and deploy your frontend
3. You'll get a URL like `invoiceflow.vercel.app`

### Step 5: Update CORS in Railway

1. Go back to Railway
2. Update the `CORS_ORIGINS` environment variable:
   ```bash
   CORS_ORIGINS=["https://invoiceflow.vercel.app"]
   ```
3. Redeploy the backend service

---

## Part 3: Post-Deployment Checklist

### ✅ Backend (Railway)

- [ ] Database migrations ran successfully
- [ ] Health check endpoint works: `https://your-backend.railway.app/health`
- [ ] API endpoints are accessible
- [ ] Environment variables are set correctly
- [ ] CORS is configured with Vercel URL

### ✅ Frontend (Vercel)

- [ ] Frontend builds successfully
- [ ] `NEXT_PUBLIC_API_URL` points to Railway backend
- [ ] Frontend can communicate with backend (check browser console)
- [ ] No CORS errors

### ✅ Storage (MinIO/S3)

**Option A: Use AWS S3 (Recommended for Production)**

1. Create an AWS S3 bucket
2. Create IAM user with S3 access
3. Update Railway environment variables:
   ```bash
   MINIO_ENDPOINT=s3.amazonaws.com
   MINIO_ACCESS_KEY=your-aws-access-key
   MINIO_SECRET_KEY=your-aws-secret-key
   MINIO_BUCKET=invoiceflow-prod
   MINIO_USE_SSL=true
   ```

**Option B: Use Railway Volume (Development Only)**

Railway doesn't provide MinIO service, but you can:
1. Add a MinIO service using a Docker image (not recommended for production)
2. Or modify the code to use Railway's volume storage (requires code changes)

---

## Troubleshooting

### Backend Issues

**Problem:** Backend won't start
- Check Railway logs
- Verify `DATABASE_URL` is correct
- Ensure `$PORT` is used (Railway sets this automatically)

**Problem:** Database connection fails
- Verify PostgreSQL service is running in Railway
- Check `DATABASE_URL` format: `postgresql://user:pass@host:port/db`

**Problem:** CORS errors
- Verify `CORS_ORIGINS` includes your Vercel URL
- Check that URL has `https://` prefix

### Frontend Issues

**Problem:** Frontend can't connect to backend
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check that backend URL is accessible (try in browser)
- Ensure CORS is configured on backend

**Problem:** Build fails
- Check that `Root Directory` is set to `frontend` in Vercel
- Verify all dependencies are in `package.json`
- Check build logs in Vercel dashboard

---

## Environment Variables Summary

### Railway (Backend)
```bash
DATABASE_URL=postgresql://... (from Railway PostgreSQL)
AZURE_FORM_RECOGNIZER_ENDPOINT=...
AZURE_FORM_RECOGNIZER_KEY=...
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini
USE_LLM_FOR_EXTRACTION=true
CORS_ORIGINS=["https://your-app.vercel.app"]
ENVIRONMENT=production
DEBUG=false
MINIO_ENDPOINT=s3.amazonaws.com (or your S3 endpoint)
MINIO_ACCESS_KEY=...
MINIO_SECRET_KEY=...
MINIO_BUCKET=invoiceflow-prod
MINIO_USE_SSL=true
```

### Vercel (Frontend)
```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

---

## Next Steps

1. **Set up monitoring** - Add error tracking (Sentry, etc.)
2. **Configure custom domains** - Add your own domain to Railway and Vercel
3. **Set up CI/CD** - Both platforms auto-deploy on git push
4. **Add SSL** - Both platforms provide SSL automatically
5. **Backup database** - Configure Railway PostgreSQL backups

---

## Quick Reference

- **Railway Dashboard**: https://railway.app/dashboard
- **Vercel Dashboard**: https://vercel.com/dashboard
- **Backend Health Check**: `https://your-backend.railway.app/health`
- **Frontend URL**: `https://your-app.vercel.app`


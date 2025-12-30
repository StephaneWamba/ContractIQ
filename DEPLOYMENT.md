# Deployment Guide: Railway (Backend) + Vercel (Frontend)

This guide explains how to deploy ContractIQ to production using Railway for the backend and Vercel for the frontend.

## Prerequisites

1. **GitHub Account** - Your code should be in a GitHub repository
2. **Railway Account** - Sign up at [railway.app](https://railway.app)
3. **Vercel Account** - Sign up at [vercel.com](https://vercel.com)
4. **OpenAI API Key** - For document processing and RAG (required)

---

## Part 1: Deploy Backend to Railway

### Step 1: Push Code to GitHub

Make sure your code is pushed to GitHub:

```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### Step 2: Create Railway Project

1. Go to [railway.app](https://railway.app) and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `contractiq` repository

**Important**: Railway needs to know where the backend code is.

1. In Railway project, go to your service → **Settings**
2. Scroll down to **Root Directory** section
3. Click **Change** and set it to: `backend`
4. Click **Save**
5. Railway will now detect the Python project and use `Dockerfile.prod` (configured in `railway.json`)

### Step 3: Add PostgreSQL Database

1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway will create a PostgreSQL database automatically
4. **Copy the `DATABASE_URL`** from the database service variables (or it will be automatically linked)

### Step 4: Configure Environment Variables

In Railway, go to your backend service → **Variables** tab, add:

```bash
# Database (automatically provided by Railway PostgreSQL)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Environment
ENVIRONMENT=production
SECRET_KEY=<generate-a-strong-secret-key>

# CORS - Add your Vercel frontend URL (update after deploying frontend)
# Format: comma-separated or JSON array: ["https://your-app.vercel.app"]
CORS_ORIGINS=https://your-app.vercel.app

# OpenAI (required for document processing and RAG)
OPENAI_API_KEY=sk-...

# Optional
ANTHROPIC_API_KEY=sk-...
```

**To generate a secret key:**

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 5: Run Database Migrations

Railway will automatically run migrations if you add this to the start command, or you can run manually:

1. Go to Railway service → **Deployments** tab
2. Click on the latest deployment → **View Logs**
3. Run migrations manually via Railway CLI or add to startup:

Add this to your deployment process (via Railway's post-deploy hook or startup script):

```bash
alembic upgrade head
```

### Step 6: Get Backend URL

After deployment, Railway will generate a domain like:

- `https://your-service.railway.app`

Copy this URL - you'll need it for the frontend.

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Import Repository

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"Add New"** → **"Project"**
3. Import your GitHub repository
4. Configure the project:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Next.js (auto-detected)
   - **Build Command**: `pnpm build` (or leave default)
   - **Output Directory**: `.next` (default)

### Step 2: Configure Environment Variables

In Vercel project settings → **Environment Variables**, add:

```bash
NEXT_PUBLIC_API_URL=https://your-railway-service.railway.app/api/v1
```

**Important**: Replace `https://your-railway-service.railway.app` with your actual Railway backend URL.

### Step 3: Deploy

1. Click **"Deploy"**
2. Vercel will build and deploy automatically
3. After deployment, copy your Vercel URL (e.g., `https://your-app.vercel.app`)

### Step 4: Update Backend CORS

Go back to Railway and update the `CORS_ORIGINS` environment variable:

```bash
CORS_ORIGINS=https://your-app.vercel.app
```

Redeploy the backend service (or it will auto-redeploy when you save the variable).

---

## Part 3: Post-Deployment

### Verify Deployment

1. **Backend Health Check:**

   ```bash
   curl https://your-railway-service.railway.app/health
   ```

   Should return: `{"status":"healthy"}`

2. **Frontend:**
   - Visit your Vercel URL
   - Try registering a new user
   - Test document upload and processing

### Database Migrations

If you add new migrations in the future:

1. Push code to GitHub
2. Railway will auto-deploy
3. Run migrations manually via Railway CLI or add to startup script:
   ```bash
   alembic upgrade head
   ```

### Environment Variables Reference

#### Backend (Railway):

- `DATABASE_URL` - PostgreSQL connection (auto-provided)
- `ENVIRONMENT=production`
- `SECRET_KEY` - JWT secret key (generate strong key)
- `CORS_ORIGINS` - Frontend URL(s)
- `OPENAI_API_KEY` - Required for document processing
- `ANTHROPIC_API_KEY` - Optional

#### Frontend (Vercel):

- `NEXT_PUBLIC_API_URL` - Backend API URL

---

## Troubleshooting

### Backend Issues

1. **Migrations not running:**

   - Add `alembic upgrade head` to startup script
   - Or run manually via Railway CLI

2. **CORS errors:**

   - Check `CORS_ORIGINS` includes your Vercel URL
   - Ensure no trailing slash
   - Format: `https://your-app.vercel.app` or JSON array

3. **Database connection:**
   - Verify `DATABASE_URL` is set correctly
   - Check database service is running in Railway

### Frontend Issues

1. **API connection errors:**

   - Verify `NEXT_PUBLIC_API_URL` is correct
   - Check backend is running and accessible
   - Ensure CORS is configured correctly

2. **Build errors:**
   - Check Vercel build logs
   - Ensure `pnpm` is used (packageManager in package.json)
   - Verify all dependencies are in package.json

---

## Expected URLs

- **Backend**: `https://contractiq-backend-xxxxx.railway.app`
- **Frontend**: `https://contractiq.vercel.app` (or your custom domain)

---

## Additional Notes

1. **File Uploads**: Railway provides persistent volumes, but consider using S3/R2 for production file storage
2. **Vector Store**: ChromaDB is currently using local storage. For production, consider ChromaDB Cloud or Pinecone
3. **Monitoring**: Set up Railway and Vercel monitoring/alerting
4. **SSL/TLS**: Both Railway and Vercel provide SSL certificates automatically

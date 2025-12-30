# Quick Deployment Checklist

## Before Pushing to GitHub

✅ **Backend is ready:**
- [x] `backend/Dockerfile` exists
- [x] `railway.json` created
- [x] Dockerfile uses `$PORT` environment variable
- [x] All dependencies in `pyproject.toml`

✅ **Frontend is ready:**
- [x] `vercel.json` created
- [x] `next.config.js` configured for production
- [x] API URL uses environment variable

✅ **Repository structure:**
- [x] `.railwayignore` created (excludes frontend from Railway)
- [x] `.vercelignore` created (excludes backend from Vercel)

---

## Railway Setup (5 minutes)

1. **Connect GitHub repo** → Railway will auto-detect Dockerfile
2. **Add PostgreSQL** → Railway provides database automatically
3. **Set environment variables:**
   ```
   DATABASE_URL=<from Railway PostgreSQL>
   AZURE_FORM_RECOGNIZER_ENDPOINT=<your-endpoint>
   AZURE_FORM_RECOGNIZER_KEY=<your-key>
   OPENAI_API_KEY=<your-key>
   CORS_ORIGINS=["https://your-vercel-app.vercel.app"]
   ```
4. **Get backend URL** → Railway generates domain automatically

---

## Vercel Setup (3 minutes)

1. **Import GitHub repo**
2. **Set Root Directory:** `frontend`
3. **Set environment variable:**
   ```
   NEXT_PUBLIC_API_URL=https://your-railway-backend.railway.app
   ```
4. **Deploy** → Vercel builds automatically

---

## After Deployment

1. **Update CORS** in Railway with your Vercel URL
2. **Test:** Visit your Vercel URL
3. **Check logs** if something doesn't work

---

## ⚠️ Important Notes

1. **MinIO/S3:** Railway doesn't provide MinIO. You need to:
   - Use AWS S3 (recommended for production)
   - Or modify code to use Railway volumes (requires code changes)

2. **Database Migrations:** Run `alembic upgrade head` after first deployment

3. **CORS:** Must update `CORS_ORIGINS` in Railway after getting Vercel URL

4. **Environment Variables:** Both platforms support setting them in dashboard

---

## Expected URLs

- **Backend:** `https://invoiceflow-backend.railway.app`
- **Frontend:** `https://invoiceflow.vercel.app`

Both platforms auto-deploy on git push! 🚀


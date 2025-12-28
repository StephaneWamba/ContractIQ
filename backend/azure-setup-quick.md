# Quick Azure Form Recognizer Setup

## 1. Create Resource in Azure Portal

1. Go to https://portal.azure.com
2. Create a resource → Search "Form Recognizer" → Create
3. Choose **Free (F0)** tier for testing
4. Note your **Endpoint** and **Key** from "Keys and Endpoint" section

## 2. Configure InvoiceFlow

**Option A: Using .env file (Recommended)**

```bash
cd backend
cp env.example .env
# Edit .env and add your credentials
```

**Option B: Direct in docker-compose.yml**
Edit `docker-compose.yml` and replace:

```yaml
AZURE_FORM_RECOGNIZER_ENDPOINT: ${AZURE_FORM_RECOGNIZER_ENDPOINT:-}
AZURE_FORM_RECOGNIZER_KEY: ${AZURE_FORM_RECOGNIZER_KEY:-}
```

With:

```yaml
AZURE_FORM_RECOGNIZER_ENDPOINT: https://your-resource.cognitiveservices.azure.com/
AZURE_FORM_RECOGNIZER_KEY: your-actual-key-here
```

## 3. Restart Backend

```bash
docker-compose restart backend
```

## 4. Test

```bash
curl http://localhost:8100/health
```

**Done!** You can now upload and process documents.

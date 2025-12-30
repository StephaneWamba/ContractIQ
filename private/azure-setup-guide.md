# Azure Form Recognizer Setup Guide

## Step 1: Create Azure Account (if needed)

1. Go to https://azure.microsoft.com/free/
2. Sign up for a free account (includes $200 credit for 30 days)

## Step 2: Create Form Recognizer Resource

1. **Log into Azure Portal**
   - Go to https://portal.azure.com
   - Sign in with your Azure account

2. **Create a new resource**
   - Click "Create a resource" (top left)
   - Search for "Form Recognizer"
   - Select "Form Recognizer" from Microsoft
   - Click "Create"

3. **Configure the resource**
   - **Subscription**: Choose your subscription
   - **Resource Group**: Create new or use existing
   - **Region**: Choose closest region (e.g., `West US 2`, `East US`)
   - **Name**: e.g., `invoiceflow-form-recognizer`
   - **Pricing Tier**: 
     - **Free (F0)**: 500 pages/month (good for testing)
     - **Standard (S0)**: Pay per page (for production)
   - Click "Review + create"
   - Click "Create"

4. **Wait for deployment** (1-2 minutes)

## Step 3: Get Your Credentials

1. **Navigate to your resource**
   - Go to "All resources" in Azure Portal
   - Click on your Form Recognizer resource

2. **Get the Endpoint**
   - In the Overview section, find "Endpoint"
   - Copy the full URL (e.g., `https://your-resource.cognitiveservices.azure.com/`)
   - This is your `AZURE_FORM_RECOGNIZER_ENDPOINT`

3. **Get the API Key**
   - Go to "Keys and Endpoint" in the left menu
   - You'll see two keys: `KEY 1` and `KEY 2`
   - Copy either one (both work)
   - This is your `AZURE_FORM_RECOGNIZER_KEY`

## Step 4: Configure InvoiceFlow

1. **Create `.env` file**
   ```bash
   cd backend
   cp env.example .env
   ```

2. **Edit `.env` file**
   ```env
   # Azure Form Recognizer
   AZURE_FORM_RECOGNIZER_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
   AZURE_FORM_RECOGNIZER_KEY=your-key-here
   ```

3. **Update docker-compose.yml** (if using Docker)
   - The environment variables are already configured
   - Make sure your `.env` file is in the `backend/` directory
   - Or set them directly in `docker-compose.yml`:
     ```yaml
     environment:
       AZURE_FORM_RECOGNIZER_ENDPOINT: https://your-resource.cognitiveservices.azure.com/
       AZURE_FORM_RECOGNIZER_KEY: your-key-here
     ```

## Step 5: Restart Services

```bash
docker-compose restart backend
```

Or if not using Docker:
```bash
# Restart your FastAPI server
```

## Step 6: Test the Configuration

1. **Check health endpoint**
   ```bash
   curl http://localhost:8100/health
   ```

2. **Test document upload** (with a PDF invoice)
   ```bash
   curl -X POST "http://localhost:8100/api/documents/upload?workspace_id=test-workspace&document_type=invoice" \
     -F "file=@sample-invoice.pdf"
   ```

## Troubleshooting

### Error: "Invalid endpoint"
- Make sure endpoint URL ends with `/`
- Check for typos in the URL

### Error: "Invalid key"
- Verify you copied the full key (no spaces)
- Try using KEY 2 instead of KEY 1

### Error: "Resource not found"
- Check that the resource is in the correct region
- Verify the endpoint URL matches your resource

### Error: "Quota exceeded"
- Free tier: 500 pages/month limit
- Upgrade to Standard (S0) tier for more capacity

## Pricing Information

- **Free Tier (F0)**: 
  - 500 pages/month
  - Good for development/testing
  
- **Standard Tier (S0)**:
  - Pay per page
  - ~$1.50 per 1,000 pages
  - No monthly limit

## Security Best Practices

1. **Never commit `.env` file to git** (already in `.gitignore`)
2. **Use environment variables in production**
3. **Rotate keys periodically** (Azure Portal → Keys and Endpoint → Regenerate)
4. **Use Azure Key Vault** for production deployments

## Next Steps

Once configured, you can:
- Upload invoices and extract data
- Process purchase orders
- Extract delivery note information
- Test the full document processing pipeline



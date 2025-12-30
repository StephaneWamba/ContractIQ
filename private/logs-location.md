# Where Are Logs Stored?

## Log Location

**Logs are stored in Docker container logs** - they are NOT saved to files by default.

### Access Logs:

1. **View all backend logs**:
   ```bash
   docker-compose logs backend
   ```

2. **Follow logs in real-time**:
   ```bash
   docker-compose logs -f backend
   ```

3. **Filter for specific log messages**:
   ```bash
   # Currency-related logs
   docker-compose logs backend | grep -E "\[INVOICE CURRENCY\]|\[PO CURRENCY\]|\[CURRENCY"
   
   # Tax validation logs
   docker-compose logs backend | grep -E "\[INVOICE TAX VALIDATION\]"
   
   # All custom logs
   docker-compose logs backend | grep -E "\[INVOICE|\[PO|\[CURRENCY"
   ```

4. **View last N lines**:
   ```bash
   docker-compose logs --tail 100 backend
   ```

### PowerShell Commands:

```powershell
# View all logs
docker-compose logs backend

# Filter logs
docker-compose logs backend | Select-String -Pattern "\[INVOICE|\[PO|\[CURRENCY"

# Last 50 lines
docker-compose logs --tail 50 backend
```

## Log Structure

Logs are output to **stdout/stderr** and captured by Docker. They are:
- **Not persisted to disk** by default
- **Lost when container restarts** (unless you configure log rotation)
- **Viewable via `docker-compose logs`**

## Current Issue from Logs

From your logs, I can see:
```
[CURRENCY CHECK] Missing currency codes - PO: USD, Invoice: None
```

**Root Cause**: Invoice currency extraction is failing - all invoices show `None` for currency code.

**Why**: The fallback currency extraction code may not be accessing paragraphs correctly for the `prebuilt-invoice` model (different structure than `prebuilt-layout`).

## Fix Applied

I've updated the invoice currency extraction to:
1. Try multiple ways to access document content (paragraphs, pages, line items)
2. Extract currency from line item fields (UnitPrice, Amount) which often contain currency symbols
3. Add comprehensive logging to track what's happening

## Next Steps

1. **Re-process documents** to see if currency extraction now works
2. **Check logs** to see currency extraction attempts:
   ```bash
   docker-compose logs backend | Select-String -Pattern "\[INVOICE CURRENCY\]"
   ```
3. **Verify currency mismatch detection** works once currencies are extracted



# Running Frontend Locally

The frontend is now configured to run locally (outside Docker) to avoid file watching issues.

## Prerequisites

- Node.js v22+ installed
- pnpm installed globally: `npm install -g pnpm`

## Setup

1. **Navigate to frontend directory:**
   ```bash
   cd ContractIQ/frontend
   ```

2. **Install dependencies:**
   ```bash
   pnpm install
   ```
   (Or use `npx pnpm@9 install` if pnpm is not in PATH)

3. **Create .env.local file** (if it doesn't exist):
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8002/api/v1
   ```

4. **Start the development server:**
   ```bash
   pnpm dev
   ```
   (Or use `npx pnpm@9 dev` if pnpm is not in PATH)

5. **Access the app:**
   Open http://localhost:3000 in your browser

## Docker Services

Make sure backend and database are running:
```bash
docker-compose up -d db backend
```

The frontend service has been commented out in docker-compose.yml since it runs locally now.



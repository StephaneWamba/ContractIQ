# InvoiceFlow - Document Matching & Reconciliation Platform

Automated document matching and three-way reconciliation for Purchase Orders, Invoices, and Delivery Notes.

## Features

- **Document Processing**: Extract structured data from PO, Invoice, and Delivery Note PDFs using Azure Form Recognizer
- **Automatic Matching**: Match documents by PO number or vendor name
- **Line Item Comparison**: Detect quantity mismatches, price changes, missing items
- **Three-Way Reconciliation**: Compare PO ↔ Invoice ↔ Delivery Note
- **Report Generation**: Generate PDF reconciliation reports with discrepancy flags

## Tech Stack

- **Backend**: FastAPI (Python), PostgreSQL, Azure Form Recognizer, PyMuPDF
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, shadcn/ui
- **Infrastructure**: Docker, MinIO (S3-compatible), PostgreSQL
- **Package Manager**: `uv` (backend), `npm` (frontend)

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Azure Form Recognizer account (for document extraction)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/StephaneWamba/InvoiceFlow.git
   cd InvoiceFlow
   ```

2. **Configure environment**
   ```bash
   make setup
   # Edit backend/.env with your Azure Form Recognizer credentials
   ```

3. **Start services**
   ```bash
   make build
   make up
   ```

4. **Run migrations**
   ```bash
   make migrate
   ```

### Ports

- **Backend API**: 8100
- **Frontend**: 3100
- **PostgreSQL**: 5440
- **MinIO API**: 9100
- **MinIO Console**: 9101

### Services

- **Backend API**: http://localhost:8100
- **Frontend**: http://localhost:3100
- **MinIO Console**: http://localhost:9101 (minioadmin/minioadmin)
- **PostgreSQL**: localhost:5440

### Development

```bash
# View logs
make logs

# Stop services
make down

# Clean everything
make clean
```

## Project Structure

```
InvoiceFlow/
├── backend/          # FastAPI backend
│   ├── src/
│   │   ├── api/      # API routes
│   │   ├── core/     # Config, database
│   │   └── models/   # SQLAlchemy models
│   ├── alembic/      # Database migrations
│   └── Dockerfile
├── frontend/         # Next.js frontend
│   ├── src/
│   │   └── app/      # Next.js app directory
│   └── Dockerfile
├── private/          # Project documentation
├── docker-compose.yml
└── Makefile
```

## Documentation

All project documentation is in the `private/` folder:
- `document-matching-reconciliation.md` - Project specification
- `tech-stack-recommendation.md` - Technology choices
- `roadmap.md` - Development roadmap

## License

MIT


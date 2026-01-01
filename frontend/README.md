# ContractIQ Frontend

Modern, high-performance frontend for ContractIQ - AI-Powered Contract Intelligence Platform.

## Features

- 🎨 **Modern UI/UX**: Beautiful, user-friendly interface with premium aesthetics
- ⚡ **High Performance**: Optimized for speed with code splitting, lazy loading, and memoization
- 🎯 **Type-Safe**: Full TypeScript support with type-safe API client
- 📱 **Responsive**: Works seamlessly on desktop and mobile devices
- 🌈 **Accessible**: WCAG compliant with proper color contrast and semantic HTML
- 🚀 **Production Ready**: Optimized builds, error handling, and loading states

## Tech Stack

- **Next.js 16** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS
- **shadcn/ui** - High-quality component library
- **React Dropzone** - File upload with drag & drop
- **Sonner** - Toast notifications
- **date-fns** - Date formatting

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

The app will be available at `http://localhost:3000`

### Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── page.tsx           # Home page
│   ├── documents/          # Documents page
│   ├── clauses/            # Clause extraction page
│   ├── qa/                 # Q&A page
│   └── settings/           # Settings page
├── components/
│   ├── ui/                 # shadcn/ui components
│   ├── layout/             # Layout components
│   ├── workspace/          # Workspace management
│   ├── documents/          # Document components
│   └── clauses/            # Clause components
├── lib/
│   └── api.ts             # API client
└── public/                # Static assets
```

## Key Components

### Workspace Management
- Create and select workspaces
- Organize documents by workspace

### Document Upload
- Drag & drop file upload
- Progress indicators
- File validation (PDF, DOCX, max 50MB)

### Document List
- Real-time status updates
- Auto-refresh for processing documents
- File metadata display

### Clause Extraction
- Risk assessment visualization
- Filterable clause table
- Risk badges with color coding
- Confidence scores

## Performance Optimizations

- **Code Splitting**: Automatic route-based code splitting
- **Lazy Loading**: Components loaded on demand
- **Memoization**: React.memo and useMemo for expensive operations
- **Image Optimization**: Next.js Image component
- **Font Optimization**: Preloaded fonts with display swap
- **Bundle Optimization**: Tree shaking and minification

## Design System

### Colors

- **Primary**: Professional blue (`oklch(45% 0.15 250)`)
- **Risk Levels**:
  - Low: Green (`oklch(75% 0.12 140)`)
  - Medium: Yellow (`oklch(75% 0.15 80)`)
  - High: Orange (`oklch(65% 0.18 50)`)
  - Critical: Red (`oklch(55% 0.22 25)`)
- **Status Colors**:
  - Success: Green
  - Warning: Yellow
  - Error: Red
  - Info: Blue

### Typography

- **Font**: Geist Sans (primary), Geist Mono (code)
- **Sizes**: Responsive typography scale
- **Weights**: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)

## Building for Production

```bash
# Build optimized production bundle
npm run build

# Start production server
npm start
```

## Testing

The frontend is designed to work seamlessly with the ContractIQ backend. Ensure:

1. Backend is running on `http://localhost:8000`
2. Database is set up and migrations are applied
3. Environment variables are configured

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## License

Proprietary - ContractIQ

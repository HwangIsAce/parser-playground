# Playground Frontend

Next.js frontend for Forge Playground document parsing application.

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm, yarn, or pnpm

### Installation

```bash
npm install
# or
yarn install
# or
pnpm install
```

### Development

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Environment Variables

Create `.env.local` file:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### Build

```bash
npm run build
npm run start
```

## Project Structure

```
frontend/
├── src/
│   ├── app/              # Next.js App Router
│   │   ├── layout.tsx    # Root layout
│   │   ├── page.tsx       # Home page
│   │   └── globals.css   # Global styles
│   ├── components/        # React components
│   │   ├── FileUploader.tsx
│   │   └── ResultViewer.tsx
│   ├── lib/              # Utilities
│   │   └── api.ts        # API client
│   └── types/            # TypeScript types
│       └── index.ts
├── public/               # Static files
└── package.json
```

## Features

- File upload
- Document viewing
- Parse mode selection (basic/enhance)
- Result display

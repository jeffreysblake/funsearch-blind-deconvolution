# FunSearch Framework - Frontend

React-based web interface for the FunSearch framework.

## Tech Stack

- **React 18+** with TypeScript
- **Vite** - Build tool and dev server
- **Ant Design 5.x** - UI component library
- **React Router** - Navigation
- **React Query** - Server state management
- **Zustand** - Client state management
- **Plotly.js** - Data visualization
- **Axios** - HTTP client

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
npm install
```

### Development

Start the development server on port 7350:

```bash
npm run dev
```

The app will be available at http://localhost:7350

### Build

Build for production:

```bash
npm run build
```

Preview production build:

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── api/              # API client and endpoints
│   ├── components/       # React components
│   │   └── layout/      # Layout components
│   ├── config/          # Configuration files
│   ├── hooks/           # Custom React hooks
│   ├── pages/           # Page components
│   ├── store/           # Zustand stores
│   ├── types/           # TypeScript type definitions
│   ├── App.tsx          # Main app component
│   ├── main.tsx         # Entry point
│   └── router.tsx       # Route configuration
├── public/              # Static assets
└── package.json
```

## Available Routes

- `/` - Home page (project list)
- `/projects/:id` - Project detail page
- `/projects/:projectId/experiments/:expId` - Experiment monitor
- `/templates` - Template gallery

## Environment Variables

Copy `.env.example` to `.env.local` and configure:

```env
VITE_API_BASE_URL=http://localhost:7351
VITE_WS_BASE_URL=ws://localhost:7351
```

## Features

### Implemented

- ✅ Project management UI
- ✅ Experiment monitoring dashboard
- ✅ Real-time metrics display (placeholder)
- ✅ Template gallery
- ✅ Responsive layout
- ✅ Type-safe API client
- ✅ State management (React Query + Zustand)

### Coming Soon

- 🔄 Live charts with Plotly.js
- 🔄 WebSocket real-time updates
- 🔄 Code editor for specifications
- 🔄 Advanced filtering and search
- 🔄 Export/import functionality

## Development Notes

- The frontend communicates with the backend API at `http://localhost:7351`
- WebSocket connections for real-time updates use `ws://localhost:7351`
- All API calls are proxied through Vite during development

## License

See the LICENSE file in the project root.

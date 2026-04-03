# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Development workspace with multiple projects spanning Python Flask, Next.js, Express.js, and React Native applications focused on educational tools, management systems, and inspection applications.

## Primary Projects & Commands

### 1. Flask Grade Management System
**Location**: Root directory (`/home/blackpc/`)
**Stack**: Flask 2.3.3, SQLAlchemy 3.0.5, SQLite, Bootstrap 5
**Run**: `python app.py` → http://localhost:5000
**Database**: Auto-creates `grade_management.db`

### 2. 21st Century Engineering Calculator
**Location**: `/21st/`
**Stack**: Next.js 15.3.4, React 19, TypeScript, Tailwind CSS 4, MathJS 14.5.2
**Commands**:
```bash
cd 21st
npm run dev --turbopack  # Development (recommended)
npm run build           # Production build
npm run start           # Production server
npm run lint            # Code quality check
```
**URL**: http://localhost:3000

### 3. SANGDAM Counseling System (Microservices)
**Location**: `/cursor/sangdam/`
**Architecture**: Monorepo with backend/frontend separation
**Stack**:
- Backend: Express.js, JWT auth, SQLite/MongoDB/MySQL, Socket.io, Sequelize ORM
- Frontend: React 18, Redux Toolkit, Vite, Tailwind CSS 3.3
**Commands**:
```bash
cd cursor/sangdam
npm run dev              # Run both frontend & backend (concurrently)
npm run backend:dev      # Backend only (port 5000)
npm run frontend:dev     # Frontend only (port 3000)
npm test                 # Run all tests
```
**Database**: Currently SQLite (`sangdam.db`), configurable via `backend/.env`

### 4. Python Counseling System
**Location**: `/counseling_system_python/`
**Stack**: Flask 3.0, Bootstrap 5, in-memory database
**Run**: `python run.py` → http://localhost:9000
**Note**: No external database needed, resets on restart

### 5. Engineering Calculator (Desktop)
**Location**: `/engineering_calculator.py`
**Stack**: Python Tkinter
**Run**: `python engineering_calculator.py`

### 6. Fire Inspection App (Express.js Backend + Mobile)
**Location**: `/fire-inspection-app/`
**Stack**: Express 4.18.2, Sequelize 6.33, SQLite, JWT, PDFKit, React Native mobile
**Commands**:
```bash
cd fire-inspection-app/backend
npm run dev              # Backend dev (port 5000)
npm run init-db          # Initialize database
```
**API Routes**: `/api/auth`, `/api/buildings`, `/api/inspections`, `/api/checklists`, `/api/reports`, `/api/dashboard`
**Mobile**: React Native app at `/fire-inspection-app/mobile/` with offline-first SQLite, GPS, photo capture

### 7. Fire Inspection Web Dashboard (Next.js + Prisma)
**Location**: `/09_app_fire/fire-inspection-app/`
**Stack**: Next.js 16.0.1, TypeScript 5.9, Tailwind CSS 4, Prisma 5.22, Zustand 5.0
**Commands**:
```bash
cd 09_app_fire/fire-inspection-app
npm run dev              # Development (port 3000)
npm run build            # Production build
npm run db:push          # Sync Prisma schema to DB
npm run db:generate      # Generate Prisma client
npm run db:studio        # Visual DB manager (port 5555)
npm run db:seed          # Load seed data
npm run db:reset         # Drop, recreate, reseed
```
**Database**: SQLite via Prisma at `prisma/dev.db`

### 8. Health Tracker (React Native)
**Location**: `/app-student/health-tracker/`
**Stack**: React Native 0.82.1, React Navigation 7.x, SQLite Storage, TypeScript
**Commands**:
```bash
cd app-student/health-tracker
npm run android          # Run on Android
npm run ios              # Run on iOS
npm start                # Metro bundler
npm test                 # Jest tests
```

## High-Level Architecture

### SANGDAM System (Most Complex)
```
cursor/sangdam/
├── backend/
│   ├── src/
│   │   ├── config/      # DB configuration (SQLite/MongoDB/MySQL)
│   │   ├── controllers/ # Business logic for each route
│   │   ├── middleware/   # JWT auth, error handling, rate limiting
│   │   ├── models/       # User, Counseling, Feedback schemas (Sequelize)
│   │   ├── routes/       # RESTful API endpoints
│   │   └── utils/        # Helpers for validation, email
│   └── server.js         # Express app with Helmet security
├── frontend/
│   ├── src/
│   │   ├── pages/        # Route components (auth, student, professor)
│   │   ├── store/        # Redux store with auth & UI slices
│   │   └── services/     # Axios API service layer
│   └── vite.config.js    # Proxy to backend on /api
└── package.json          # Monorepo scripts using concurrently
```

Key patterns:
- JWT tokens stored in localStorage (frontend)
- Role-based access control (student/professor)
- Real-time updates via Socket.io
- API proxy configuration in Vite for development

### Next.js Calculator Architecture (`/21st/`)
- Single-page app with all logic in `src/components/EngineeringCalculator.tsx`
- Uses MathJS `evaluate()` for safe math expression parsing
- Keyboard event handling with useEffect hooks
- Component composition with shadcn/ui button variants
- TypeScript path alias: `@/*` → `src/*`

### Fire Inspection Web Dashboard (`/09_app_fire/`)
- Next.js App Router with API routes at `app/api/`
- Prisma ORM with SQLite (`prisma/schema.prisma`)
- Zustand for auth state management with persistence (`lib/stores/auth.ts`)
- JWT auth via `lib/auth/jwt.ts` + route protection in `middleware.ts`
- Models: User (INSPECTOR/MANAGER/ADMIN), Company, Facility, Equipment, Inspection, ChecklistItem, Defect, Photo

## Test Accounts

For counseling systems (both SANGDAM and Python):
- Students: `student1` / `password123`, `student2` / `password123`
- Professors: `professor1` / `password123`, `professor2` / `password123`

For fire inspection systems:
- Roles: admin, manager, inspector (check seed data or init-db for credentials)

## Port Allocation

Projects share ports — only run one per port at a time:
- **Port 3000**: Next.js Calculator (`/21st/`) OR SANGDAM Frontend OR Fire Inspection Web OR Engineering Calculator (`/engineering-calculator/`)
- **Port 5000**: Flask Grade Management OR SANGDAM Backend OR Fire Inspection Backend
- **Port 5555**: Prisma Studio (fire inspection web)
- **Port 8081**: React Native Metro bundler
- **Port 9000**: Python Counseling System

## Database Management

| Project | Type | File | ORM | Reset Method |
|---------|------|------|-----|-------------|
| Root Flask | SQLite | `grade_management.db` | SQLAlchemy | Delete `.db` file |
| SANGDAM | SQLite (default) | `sangdam.db` | Sequelize | Delete `.db` file |
| Fire Inspection API | SQLite | `fire_inspection.db` | Sequelize | `npm run init-db` |
| Fire Inspection Web | SQLite | `prisma/dev.db` | Prisma | `npm run db:reset` |
| Python Counseling | In-memory | N/A | None | Restart server |
| Health Tracker | SQLite | Device local | SQLite Storage | Clear app data |

- **SANGDAM**: Switch DB type via `backend/.env` (`DB_TYPE=sqlite|mongodb|mysql`)

## Testing

- **SANGDAM Backend**: Jest + Supertest (`cd cursor/sangdam && npm test`)
- **SANGDAM Frontend**: Vitest (`cd cursor/sangdam/frontend && npm test`)
- **Health Tracker**: Jest (`cd app-student/health-tracker && npm test`)
- **Python projects**: Manual testing with provided test accounts

## Environment Variables

### SANGDAM Backend (`cursor/sangdam/backend/.env`)
```
DB_TYPE=sqlite
SQLITE_DATABASE=sangdam.db
PORT=5000
JWT_SECRET=your-secret-key
FRONTEND_URL=http://localhost:3000
```

### Fire Inspection Web (`09_app_fire/fire-inspection-app/.env`)
```
DATABASE_URL="file:./dev.db"
JWT_SECRET=your-secret-key
JWT_EXPIRES_IN="7d"
NEXT_PUBLIC_APP_URL="http://localhost:3000"
NEXT_PUBLIC_API_URL="http://localhost:3000/api"
```

### Fire Inspection Backend (`fire-inspection-app/backend/.env`)
```
PORT=5000
JWT_SECRET=your-secret-key
DB_NAME=fire_inspection.db
UPLOAD_DIR=uploads
PDF_DIR=reports
NODE_ENV=development
```

## Key Implementation Details

### Authentication Flow (SANGDAM & Fire Inspection)
1. Login sends credentials to `/api/auth/login`
2. Backend validates with bcrypt and returns JWT token
3. Frontend stores token and adds to request headers
4. Protected routes check token validity via middleware

### Grade Calculation (Flask App)
Automatic grade assignment in `app.py`: A+ (≥95) through F (<60)

### Adding New API Endpoint (SANGDAM)
1. Create controller in `backend/src/controllers/`
2. Add route in `backend/src/routes/`
3. Register route in `server.js`
4. Add service method in `frontend/src/services/`
5. Update Redux slice if state management needed

### Database Schema Changes
- **SQLAlchemy** (Flask): Modify model in `app.py`, delete DB file to recreate
- **Sequelize** (SANGDAM/Fire): Update model in `src/models/`, restart server
- **Prisma** (Fire Web): Edit `prisma/schema.prisma`, run `npm run db:push`

## Debugging

```bash
# Find processes on common ports
lsof -i :3000 -i :5000 -i :9000
kill -9 <PID>

# SANGDAM health check
curl http://localhost:5000/api/health

# Prisma visual DB browser
cd 09_app_fire/fire-inspection-app && npm run db:studio
```

## Root package.json

The root `package.json` includes `genkit` and `@genkit-ai/googleai` dependencies for Google AI integration, plus `mathjs` for calculation support.

## Three Man Team
Available agents: Arch (Architect), Bob (Builder), Richard (Reviewer)

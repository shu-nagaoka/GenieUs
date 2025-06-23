# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Frontend Development Commands

### Essential Development Commands
```bash
# Development server with Turbopack
npm run dev

# Production build (includes Prisma migrations)
npm run build

# Run tests
npm test                  # Unit tests with Jest
npm run test:e2e         # E2E tests with Playwright
npm run test:coverage    # Coverage report

# Code quality
npm run lint             # ESLint check
npm run lint:fix         # Auto-fix linting issues
npm run format           # Prettier formatting
```

### Testing Specific Files
```bash
# Run specific Jest test
npm test -- path/to/test.test.tsx

# Run Playwright test with UI
npx playwright test --ui

# Debug specific E2E test
npx playwright test path/to/test.spec.ts --debug
```

## High-Level Architecture

### Next.js App Router Structure
This is a Next.js 15 application using the App Router pattern with React 19. The architecture follows a feature-based component organization:

```
src/
├── app/                    # Next.js App Router pages and API routes
│   ├── api/auth/          # NextAuth configuration (not fully implemented)
│   ├── chat/              # Real-time chat with ADK backend
│   └── (dashboard)/       # Dashboard routes group
├── components/
│   ├── features/          # Domain-specific components (childcare features)
│   ├── layout/            # App layout components (sidebar, navigation)
│   ├── ui/                # shadcn/ui primitives
│   └── common/            # Shared components
├── hooks/                 # Custom React hooks
├── lib/                   # Utilities and configurations
└── types/                 # TypeScript type definitions
```

### Key Architectural Patterns

1. **Component Architecture**: Uses shadcn/ui component library built on Radix UI with Tailwind CSS styling. Components are composed from primitives in `components/ui/`.

2. **API Integration**: Currently uses direct fetch calls to `http://localhost:8000`. React Query is installed but not yet implemented for server state management.

3. **Styling System**: Tailwind CSS with CSS variables for theming. Theme colors are defined in `globals.css` and extended in `tailwind.config.ts`.

4. **Chat Implementation**: The chat feature (`src/app/chat/page.tsx`) now supports Markdown rendering using `react-markdown` with GitHub Flavored Markdown support.

## Chat Feature with Markdown Support

The chat interface renders AI responses with proper Markdown formatting:
- Uses `react-markdown` with `remark-gfm` plugin
- Styled with Tailwind Typography (`prose` classes)
- User messages display as plain text
- Genie (AI) messages render with full Markdown support including:
  - Bold/italic text
  - Lists (ordered/unordered)
  - Headings
  - Code blocks
  - Blockquotes

## Backend Integration Points

### Chat API
```typescript
// POST to /api/v1/chat
const response = await fetch('http://localhost:8000/api/v1/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: userMessage,
    user_id: 'user123',
    session_id: sessionId
  })
})
```

### Environment Variables
Required in `.env.local`:
- Authentication providers configuration
- Backend API URL (currently hardcoded as `http://localhost:8000`)

## Testing Strategy

### Unit Tests (Jest)
- Component testing with React Testing Library
- Test files in `__tests__/` directory
- Focus on user interactions and component behavior

### E2E Tests (Playwright)
- Full user flow testing
- Tests located in `test/e2e/`
- Multi-browser testing configured

## Design System

Uses shadcn/ui with "new-york" style and "stone" base color. Key design tokens:
- Primary color: Amber (for childcare warmth)
- Font: "Kiwi Maru" for friendly appearance
- Responsive sidebar navigation
- Card-based layouts with backdrop blur effects

## Pre-commit Hooks

Husky runs lint-staged on commit:
1. ESLint for TypeScript/React issues
2. Prettier for consistent formatting
3. Tests must pass before commit

## Development Workflow

1. Feature branches should follow component structure
2. New UI components should extend shadcn/ui primitives
3. API calls should handle errors with user-friendly messages in Japanese
4. Maintain TypeScript strict mode compliance
5. Use path alias `@/` for imports from `src/`
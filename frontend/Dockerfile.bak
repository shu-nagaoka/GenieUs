# Use Node.js 20 for compatibility with package requirements
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache libc6-compat

# Copy package files
COPY package*.json ./

# Set environment variables for build
ENV NEXT_TELEMETRY_DISABLED=1
ENV SKIP_ENV_VALIDATION=1

# Install dependencies including devDependencies (needed for build)
# Note: --ignore-scripts prevents Husky from running in Docker
RUN npm ci --ignore-scripts --include=dev

# Copy source code
COPY . .

# Copy production environment file if it exists
COPY .env.production.local* ./

# Build with increased memory and skip env validation
ENV SKIP_ENV_VALIDATION=true
# Build時の環境変数をセット
ENV NEXT_PUBLIC_API_BASE_URL=https://genius-backend-staging-280304291898.asia-northeast1.run.app
ENV NEXT_PUBLIC_API_URL=https://genius-backend-staging-280304291898.asia-northeast1.run.app
ENV NEXTAUTH_SECRET=build-time-secret
ENV GOOGLE_CLIENT_ID=build-time-id
ENV GOOGLE_CLIENT_SECRET=build-time-secret
RUN npm run build

# Set production environment after build
ENV NODE_ENV=production

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
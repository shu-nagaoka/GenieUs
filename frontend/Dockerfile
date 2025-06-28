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

# Build with increased memory
RUN npm run build

# Set production environment after build
ENV NODE_ENV=production

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
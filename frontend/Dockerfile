# Use Node.js 20 for compatibility with package requirements
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache libc6-compat

# Copy package files
COPY package*.json ./

# Set production environment
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV SKIP_ENV_VALIDATION=1

# Install dependencies (disable scripts to avoid Husky issues in Docker)
RUN npm ci --ignore-scripts

# Copy source code
COPY . .

# Build with increased memory
RUN npm run build

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
# Use Node.js 18 for better compatibility
FROM node:18-alpine

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

# Install dependencies with increased memory
RUN npm install --verbose

# Copy source code
COPY . .

# Build with increased memory
RUN npm run build

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
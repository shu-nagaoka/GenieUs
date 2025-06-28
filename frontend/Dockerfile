# Use official Node.js runtime as base image
FROM node:20

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of application code
COPY . .

# Set environment variables before build
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV SKIP_ENV_VALIDATION=1

# Build the application
RUN npm run build:docker

# Expose port 3000
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
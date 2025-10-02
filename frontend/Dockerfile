# Frontend Dockerfile for Railway
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (including express)
RUN npm install

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Verify dist folder exists and list contents
RUN ls -la && ls -la dist/ 2>/dev/null || echo 'dist directory not found, checking if build failed'

# Expose port
EXPOSE 3000

# Start server
CMD ["node", "server.js"]

# Frontend Dockerfile for Railway
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Install express for serving
RUN npm install express

# Expose port
EXPOSE 3000

# Start server
CMD ["node", "server.js"]

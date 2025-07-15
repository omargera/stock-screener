#!/bin/bash

# Stock Screener Docker Commands
# Make this script executable with: chmod +x docker_commands.sh

echo "🐳 Stock Screener Docker Setup"
echo "================================"

# Build the Docker image
echo "📦 Building Docker image..."
docker build -t stock-screener:latest .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
    
    # Run the container
    echo "🚀 Running stock screener container..."
    docker run --rm stock-screener:latest
else
    echo "❌ Docker build failed!"
    exit 1
fi

echo ""
echo "🔧 Additional Docker Commands:"
echo "------------------------------"
echo "Build image:         docker build -t stock-screener:latest ."
echo "Run container:       docker run --rm stock-screener:latest"
echo "Run interactively:   docker run --rm -it stock-screener:latest bash"
echo "Run with options:    docker run --rm stock-screener:latest --mode market-analysis"
echo "Health check:        docker run --rm stock-screener:latest --health-check"
echo "View images:         docker images"
echo "Remove image:        docker rmi stock-screener:latest" 
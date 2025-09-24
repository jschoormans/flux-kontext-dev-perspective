#!/bin/bash

# Deployment script for Kontext Hack
echo "🚀 Deploying Kontext Hack..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your FAL_API_KEY"
    exit 1
fi

# Check if FAL_API_KEY is set
if ! grep -q "FAL_API_KEY=" .env; then
    echo "❌ Error: FAL_API_KEY not found in .env file!"
    exit 1
fi

echo "✅ Environment variables found"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Test the application
echo "🧪 Testing application..."
npm start &
SERVER_PID=$!
sleep 5

# Check if server is running
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Application is running successfully"
    kill $SERVER_PID
else
    echo "❌ Application failed to start"
    kill $SERVER_PID
    exit 1
fi

echo "🎉 Ready for deployment!"
echo ""
echo "Deployment options:"
echo "1. Vercel: vercel"
echo "2. Railway: Connect GitHub repo to Railway"
echo "3. Render: Connect GitHub repo to Render"
echo "4. Heroku: heroku create && git push heroku main"
echo ""
echo "Don't forget to set FAL_API_KEY in your deployment platform!"

#!/bin/bash

echo "🚀 Setting up Audio Transcription Workflow with n8n"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads outputs transcriptions n8n_data

# Build the transcription service Docker image
echo "🔨 Building transcription service Docker image..."
docker build -t transcription-service .

# Start n8n and services
echo "🐳 Starting n8n and services..."
docker compose up -d

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Access n8n at: http://localhost:5678"
echo "   Username: admin"
echo "   Password: strongpass"
echo ""
echo "2. Import the workflow:"
echo "   - Go to Workflows in n8n"
echo "   - Click 'Import from file'"
echo "   - Select 'audio_transcription_workflow.json'"
echo ""
echo "3. Test the workflow:"
echo "   - Send a POST request to: http://localhost:5678/webhook/upload-audio"
echo "   - Include an m4a file in the request body"
echo ""
echo "📁 File locations:"
echo "   - Uploads: ./uploads/"
echo "   - Converted files: ./outputs/"
echo "   - Transcriptions: ./transcriptions/"
echo ""
echo "🔧 To stop services: docker compose down" 
# Audio Transcription Workflow with n8n

This project provides a complete n8n workflow for uploading m4a audio files, converting them to mp3 format, and transcribing them using OpenAI's Whisper model.

## 🚀 Features

- **File Upload**: Webhook endpoint for uploading audio files
- **Audio Conversion**: Automatic conversion from m4a to mp3 using FFmpeg
- **Transcription**: High-quality transcription using Whisper large-v3-turbo model
- **Docker Integration**: Containerized services for easy deployment
- **Progress Tracking**: Real-time progress updates during transcription
- **Error Handling**: Comprehensive error handling and validation

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.12+ (for local testing)
- At least 8GB RAM (for Whisper model)

## 🛠️ Setup

### 1. Clone and Setup

```bash
# Run the setup script
./setup.sh
```

This will:
- Create necessary directories
- Build the transcription service Docker image
- Start n8n and all services

### 2. Access n8n

- **URL**: http://localhost:5678
- **Username**: admin
- **Password**: strongpass

### 3. Import Workflow

1. Go to Workflows in n8n
2. Click "Import from file"
3. Select `audio_transcription_workflow.json`

## 🔄 Workflow Overview

The workflow consists of the following steps:

1. **Webhook Trigger**: Receives uploaded audio files
2. **File Validation**: Checks if the file is an audio file
3. **File Save**: Saves the uploaded file to the uploads directory
4. **Audio Conversion**: Converts m4a to mp3 using FFmpeg
5. **Transcription**: Processes the mp3 file using Whisper
6. **Response**: Returns the transcription results

## 📁 Directory Structure

```
n8n/
├── uploads/           # Uploaded audio files
├── outputs/           # Converted mp3 files
├── transcriptions/    # Transcription output files
├── n8n_data/         # n8n configuration and workflows
├── transcribe.py      # Original transcription script
├── transcribe_api.py  # API-friendly transcription script
├── requirements.txt   # Python dependencies
├── docker-compose.yml # Docker services configuration
├── Dockerfile        # Transcription service container
├── setup.sh          # Setup script
├── test_workflow.py  # Test script
└── README.md         # This file
```

## 🧪 Testing

### Using the Test Script

```bash
# Test with an m4a file
python test_workflow.py path/to/your/audio.m4a
```

### Manual Testing with curl

```bash
# Upload an audio file
curl -X POST \
  -F "file=@path/to/your/audio.m4a" \
  http://localhost:5678/webhook/upload-audio
```

### Manual Testing with Python

```python
import requests

# Upload file
with open('audio.m4a', 'rb') as f:
    files = {'file': ('audio.m4a', f, 'audio/m4a')}
    response = requests.post('http://localhost:5678/webhook/upload-audio', files=files)
    
print(response.json())
```

## 🔧 Configuration

### Environment Variables

You can modify the following in `docker-compose.yml`:

- `N8N_BASIC_AUTH_USER`: n8n username
- `N8N_BASIC_AUTH_PASSWORD`: n8n password
- `GENERIC_TIMEZONE`: Timezone for n8n

### Audio Conversion Settings

The FFmpeg conversion uses these settings:
- Codec: libmp3lame
- Bitrate: 192k
- Format: MP3

### Transcription Settings

The Whisper transcription uses:
- Model: openai/whisper-large-v3-turbo
- Chunk size: 30 seconds
- Sampling rate: 16kHz

## 📊 API Response Format

### Success Response

```json
{
  "success": true,
  "message": "Audio transcription completed successfully",
  "original_file": "audio.m4a",
  "converted_file": "audio.m4a.mp3",
  "transcription": {
    "full_text": "The transcribed text...",
    "duration_seconds": 120.5,
    "processing_time_minutes": 2.3,
    "total_chunks": 4
  },
  "output_file": "/app/output/transcription_audio.m4a.mp3.txt"
}
```

### Error Response

```json
{
  "success": false,
  "error": "Invalid file type. Please upload an audio file.",
  "received_mimetype": "text/plain"
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Docker not running**
   ```bash
   docker --version
   docker-compose --version
   ```

2. **Port already in use**
   ```bash
   # Check what's using port 5678
   lsof -i :5678
   ```

3. **Insufficient memory for Whisper**
   - Ensure you have at least 8GB RAM available
   - Consider using a smaller Whisper model

4. **File upload issues**
   - Check file permissions
   - Ensure the file is a valid audio format
   - Verify the uploads directory exists

### Logs

```bash
# View n8n logs
docker-compose logs n8n

# View transcription service logs
docker-compose logs transcription-service

# View all logs
docker-compose logs
```

## 🔄 Workflow Customization

### Adding New Audio Formats

1. Update the file validation in the workflow
2. Modify the FFmpeg conversion command
3. Test with the new format

### Changing Transcription Model

1. Edit `transcribe_api.py`
2. Change the `model_name` variable
3. Rebuild the Docker image

### Adding Post-Processing

1. Add new nodes to the workflow
2. Connect them after the transcription step
3. Update the response format

## 📈 Performance Tips

1. **Use SSD storage** for faster file I/O
2. **Increase Docker memory** for better Whisper performance
3. **Use smaller audio files** for faster processing
4. **Consider batch processing** for multiple files

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [n8n](https://n8n.io/) for the workflow automation platform
- [OpenAI Whisper](https://github.com/openai/whisper) for the transcription model
- [FFmpeg](https://ffmpeg.org/) for audio conversion
- [Docker](https://www.docker.com/) for containerization 
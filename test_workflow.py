#!/usr/bin/env python3
"""
Test script for the Audio Transcription Workflow
Uploads an m4a file to n8n and retrieves the transcription
"""

import requests
import json
import sys
import os
from pathlib import Path

def upload_audio_file(file_path, webhook_url):
    """
    Upload an audio file to the n8n workflow
    
    Args:
        file_path (str): Path to the audio file (m4a, mp3, etc.)
        webhook_url (str): n8n webhook URL
    
    Returns:
        dict: Response from the workflow
    """
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")
    
    # Prepare the file for upload
    with open(file_path, 'rb') as f:
        files = {
            'file': (os.path.basename(file_path), f, 'audio/m4a')
        }
        
        print(f"📤 Uploading {file_path} to n8n workflow...")
        
        try:
            response = requests.post(webhook_url, files=files)
            response.raise_for_status()
            
            result = response.json()
            print("✅ Upload successful!")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Upload failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None

def main():
    # Configuration
    WEBHOOK_URL = "http://localhost:5678/webhook/upload-audio"
    
    # Check if file path is provided
    if len(sys.argv) < 2:
        print("Usage: python test_workflow.py <audio_file_path>")
        print("Example: python test_workflow.py sample.m4a")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Upload the file
    result = upload_audio_file(file_path, WEBHOOK_URL)
    
    if result:
        if result.get('success'):
            print("\n🎉 Transcription completed successfully!")
            print(f"📄 Original file: {result.get('original_file')}")
            print(f"🔄 Converted file: {result.get('converted_file')}")
            
            transcription = result.get('transcription', {})
            print(f"⏱️  Duration: {transcription.get('duration_seconds', 'N/A')} seconds")
            print(f"⏱️  Processing time: {transcription.get('processing_time_minutes', 'N/A')} minutes")
            print(f"📊 Total chunks: {transcription.get('total_chunks', 'N/A')}")
            
            print(f"\n📝 Transcription:")
            print("=" * 50)
            print(transcription.get('full_text', 'No transcription text available'))
            print("=" * 50)
            
            if result.get('output_file'):
                print(f"\n💾 Full transcription saved to: {result.get('output_file')}")
        else:
            print(f"❌ Transcription failed: {result.get('error', 'Unknown error')}")
    else:
        print("❌ Failed to upload file")

if __name__ == "__main__":
    main() 
import torch
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
import librosa
import numpy as np
import os
import time
import json
import sys
import argparse
from datetime import datetime

def load_model():
    """Load the Whisper model and processor"""
    model_name = "openai/whisper-large-v3-turbo"
    processor = AutoProcessor.from_pretrained(model_name)
    model = AutoModelForSpeechSeq2Seq.from_pretrained(model_name)
    return processor, model

def transcribe_audio_chunk(audio_chunk, processor, model):
    """Transcribe a chunk of audio with automatic language detection"""
    inputs = processor(audio_chunk, sampling_rate=16000, return_tensors="pt")

    with torch.no_grad():
        generated_ids = model.generate(
            inputs["input_features"],
            task="transcribe"
        )

    return processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

def transcribe_file(audio_file_path, output_dir=None):
    """Transcribe an audio file and return results as JSON"""
    
    if not os.path.exists(audio_file_path):
        return {
            "success": False,
            "error": f"Audio file not found: {audio_file_path}"
        }
    
    try:
        # Load model
        print("Loading Whisper model...")
        processor, model = load_model()
        
        # Load audio using librosa
        print(f"Loading audio file: {audio_file_path}")
        audio_array, sampling_rate = librosa.load(audio_file_path, sr=16000)
        duration = len(audio_array) / sampling_rate
        print(f"Audio loaded successfully. Duration: {duration:.2f} seconds")

        # Process audio in chunks (30 seconds each)
        chunk_duration = 30  # seconds
        chunk_samples = int(chunk_duration * sampling_rate)
        total_chunks = (len(audio_array) + chunk_samples - 1) // chunk_samples

        print(f"Processing {total_chunks} chunks...")

        # Initialize results
        transcriptions = []
        start_time = time.time()

        for i in range(0, len(audio_array), chunk_samples):
            chunk = audio_array[i:i + chunk_samples]
            chunk_num = i//chunk_samples + 1

            print(f"Processing chunk {chunk_num}/{total_chunks}...")

            if len(chunk) < chunk_samples:
                # Pad the last chunk if it's shorter
                chunk = np.pad(chunk, (0, chunk_samples - len(chunk)), 'constant')

            try:
                chunk_transcription = transcribe_audio_chunk(chunk, processor, model)
                
                if chunk_transcription.strip():
                    transcriptions.append({
                        "chunk": chunk_num,
                        "timestamp": chunk_num * chunk_duration,
                        "text": chunk_transcription.strip()
                    })
                    print(f"✓ Chunk {chunk_num}: {chunk_transcription}")
                else:
                    transcriptions.append({
                        "chunk": chunk_num,
                        "timestamp": chunk_num * chunk_duration,
                        "text": "[silence or no speech detected]"
                    })
                    print(f"✓ Chunk {chunk_num}: [silence]")

            except Exception as e:
                error_msg = f"ERROR: {e}"
                transcriptions.append({
                    "chunk": chunk_num,
                    "timestamp": chunk_num * chunk_duration,
                    "text": error_msg
                })
                print(f"✗ Chunk {chunk_num}: {error_msg}")
                continue

        # Calculate total time
        total_time = time.time() - start_time
        
        # Combine all transcriptions into full text
        full_text = " ".join([t["text"] for t in transcriptions if t["text"] != "[silence or no speech detected]"])
        
        # Create output directory if specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"transcription_{os.path.basename(audio_file_path)}.txt")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Transcription Results\n")
                f.write(f"File: {audio_file_path}\n")
                f.write(f"Duration: {duration:.2f} seconds\n")
                f.write(f"Processing time: {total_time/60:.1f} minutes\n")
                f.write("="*50 + "\n\n")
                f.write(full_text)
                f.write("\n\n" + "="*50 + "\n")
                f.write("Chunk-by-chunk breakdown:\n")
                for t in transcriptions:
                    f.write(f"[{t['timestamp']}s] Chunk {t['chunk']}: {t['text']}\n")

        return {
            "success": True,
            "file_path": audio_file_path,
            "duration_seconds": duration,
            "processing_time_minutes": total_time / 60,
            "total_chunks": total_chunks,
            "full_text": full_text,
            "chunks": transcriptions,
            "output_file": output_file if output_dir else None
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "file_path": audio_file_path
        }

def main():
    parser = argparse.ArgumentParser(description='Transcribe audio file using Whisper')
    parser.add_argument('audio_file', help='Path to the audio file to transcribe')
    parser.add_argument('--output-dir', help='Directory to save output files', default=None)
    
    args = parser.parse_args()
    
    result = transcribe_file(args.audio_file, args.output_dir)
    
    # Output JSON result
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main() 
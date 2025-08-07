import torch
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
import librosa
import numpy as np
import os
import time
from datetime import datetime

# Load the model and processor - using a smaller but still multilingual model
model_name = "openai/whisper-large-v3-turbo"  # Much smaller and faster
processor = AutoProcessor.from_pretrained(model_name)
model = AutoModelForSpeechSeq2Seq.from_pretrained(model_name)

# Load and process the audio file
audio_file_path = '/content/7.30 2.mp3'
output_file = 'realtime_transcription.txt'
progress_file = 'transcription_progress.txt'

def transcribe_audio_chunk(audio_chunk, processor, model):
    """Transcribe a chunk of audio with automatic language detection"""
    inputs = processor(audio_chunk, sampling_rate=16000, return_tensors="pt")

    with torch.no_grad():
        generated_ids = model.generate(
            inputs["input_features"],
            task="transcribe"
        )

    return processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

def save_chunk_result(chunk_num, transcription, output_file, progress_file):
    """Save chunk result immediately and update progress"""
    timestamp = datetime.now().strftime("%H:%M:%S")

    # Save to main output file
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] Chunk {chunk_num}: {transcription}\n")

    # Update progress file
    with open(progress_file, 'w', encoding='utf-8') as f:
        f.write(f"Last processed: Chunk {chunk_num} at {timestamp}\n")
        f.write(f"Transcription: {transcription}\n")

try:
    # Load audio using librosa
    print(f"Loading audio file: {audio_file_path}")
    audio_array, sampling_rate = librosa.load(audio_file_path, sr=16000)  # Resample to 16kHz
    print(f"Audio loaded successfully. Duration: {len(audio_array)/sampling_rate:.2f} seconds")

    # Process audio in chunks (30 seconds each)
    chunk_duration = 30  # seconds
    chunk_samples = int(chunk_duration * sampling_rate)
    total_chunks = (len(audio_array) + chunk_samples - 1) // chunk_samples

    print(f"Processing {total_chunks} chunks...")
    print(f"Results will be saved to: {output_file}")
    print(f"Progress tracking: {progress_file}")
    print("="*50)

    # Initialize output files
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Real-time Multilingual Transcription\n")
        f.write(f"File: {audio_file_path}\n")
        f.write(f"Duration: {len(audio_array)/sampling_rate:.2f} seconds\n")
        f.write(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*50 + "\n\n")

    with open(progress_file, 'w', encoding='utf-8') as f:
        f.write(f"Transcription Progress\n")
        f.write(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total chunks: {total_chunks}\n")
        f.write("="*30 + "\n")

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

            if chunk_transcription.strip():  # Only add non-empty transcriptions
                save_chunk_result(chunk_num, chunk_transcription, output_file, progress_file)
                print(f"✓ Chunk {chunk_num}: {chunk_transcription}")
            else:
                save_chunk_result(chunk_num, "[silence or no speech detected]", output_file, progress_file)
                print(f"✓ Chunk {chunk_num}: [silence]")

        except Exception as e:
            error_msg = f"ERROR: {e}"
            save_chunk_result(chunk_num, error_msg, output_file, progress_file)
            print(f"✗ Chunk {chunk_num}: {error_msg}")
            continue

        # Calculate and display progress
        elapsed_time = time.time() - start_time
        avg_time_per_chunk = elapsed_time / chunk_num
        remaining_chunks = total_chunks - chunk_num
        estimated_remaining_time = remaining_chunks * avg_time_per_chunk

        print(f"   Progress: {chunk_num}/{total_chunks} ({chunk_num/total_chunks*100:.1f}%)")
        print(f"   Estimated time remaining: {estimated_remaining_time/60:.1f} minutes")
        print()

    # Final summary
    total_time = time.time() - start_time
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(f"\n" + "="*50 + "\n")
        f.write(f"Transcription completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total processing time: {total_time/60:.1f} minutes\n")

    with open(progress_file, 'a', encoding='utf-8') as f:
        f.write(f"\nCOMPLETED at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total time: {total_time/60:.1f} minutes\n")

    print(f"\n🎉 Transcription complete!")
    print(f"📄 Full results: {output_file}")
    print(f"📊 Progress log: {progress_file}")
    print(f"⏱️  Total time: {total_time/60:.1f} minutes")

except Exception as e:
    print(f"Error during transcription: {e}")
    import traceback
    traceback.print_exc()